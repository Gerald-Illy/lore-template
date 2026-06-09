"""
Jira Tree Discovery Script

Deterministic BFS traversal of a Jira hierarchy via acli.
Produces a SINGLE manifest that accumulates all knowledge across crawls.

The manifest:
- Is always extended or updated, never reduced
- Supports multiple entry points (trees) in one file
- Merges overlapping trees automatically
- Trees = parent/child hierarchy only, never dependencies
- Only read/written by Python scripts, never by Claude

Optimizations:
- Batch size 100 (Jira JQL limit)
- Combined children search + metadata fetch (one call per level)
- Parallel batch execution via ThreadPoolExecutor
- Bidirectional deps with blocking distinction

Usage:
    python jira_tree.py <entry-point> [--depth N]

Examples:
    python jira_tree.py PROJ-1000
    python jira_tree.py PROJ-1000 --depth 4
    python jira_tree.py PROJ-1001
"""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


# Instance-specific custom fields — configure per Jira instance
METADATA_FIELDS = "key,issuetype,summary,status,assignee,priority,updated,parent,issuelinks,comment,customfield_18700,customfield_17800"
PII_SKIP = "comment,assignee,reporter,creator,description,summary"
MANIFEST_PATH = Path(".lore/manifests/crawl-jira-manifest.json")
BATCH_SIZE = 100
MAX_WORKERS = 4


def run_acli(args: list[str]) -> str:
    cmd = ["acli", "jira", "workitem"] + args + ["--pii-skip", PII_SKIP]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"acli failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def _parse_issue(issue: dict, key: str) -> dict:
    fields = issue.get("fields", {})

    deps_out = []
    deps_in = []
    blocks = []
    blocked_by = []

    for link in (fields.get("issuelinks") or []):
        link_type = (link.get("type") or {})

        if "outwardIssue" in link:
            target_key = link["outwardIssue"].get("key", "")
            if target_key:
                deps_out.append(target_key)
                outward_label = link_type.get("outward", "")
                if "block" in outward_label.lower():
                    blocks.append(target_key)
        elif "inwardIssue" in link:
            target_key = link["inwardIssue"].get("key", "")
            if target_key:
                deps_in.append(target_key)
                inward_label = link_type.get("inward", "")
                if "block" in inward_label.lower():
                    blocked_by.append(target_key)

    comment_data = fields.get("comment") or {}
    comment_count = comment_data.get("total", 0)

    # Instance-specific custom fields — configure per Jira instance
    owning_program_field = fields.get("customfield_18700")
    owning_program = owning_program_field.get("value", "") if isinstance(owning_program_field, dict) else None

    team_field = fields.get("customfield_17800")
    team = team_field.get("name", "") if isinstance(team_field, dict) else None

    return {
        "key": issue.get("key", key),
        "type": (fields.get("issuetype") or {}).get("name", "Unknown"),
        "summary": fields.get("summary", ""),
        "status": (fields.get("status") or {}).get("name", "Unknown"),
        "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
        "updated": fields.get("updated", ""),
        "parent": (fields.get("parent") or {}).get("key", None),
        "children": [],
        "comment_count": comment_count,
        "deps_out": deps_out,
        "deps_in": deps_in,
        "blocks": blocks,
        "blocked_by": blocked_by,
        "owning_program": owning_program,
        "team": team,
    }


def _fetch_batch_by_key(keys: list[str]) -> dict[str, dict]:
    """Fetch metadata for a batch of keys via JQL key in (...)."""
    keys_csv = ", ".join(keys)
    jql = f"key in ({keys_csv})"
    try:
        raw = run_acli(["search", "--jql", jql, "--json", "--paginate",
                       "--fields", METADATA_FIELDS])
        if not raw:
            return {}
        data = json.loads(raw)
        issues = data if isinstance(data, list) else [data]
        results = {}
        for issue in issues:
            key = issue.get("key", "")
            if key:
                parsed = _parse_issue(issue, key)
                if parsed:
                    results[key] = parsed
        return results
    except Exception as e:
        print(f"  [WARN] Batch fetch failed: {e}", file=sys.stderr)
        return {}


def _fetch_children_keys_batch(parent_keys: list[str]) -> list[str]:
    """Fetch child keys for a batch of parents (fast, no fields)."""
    keys_csv = ", ".join(parent_keys)
    jql = f"parent in ({keys_csv}) ORDER BY key ASC"
    try:
        raw = run_acli(["search", "--jql", jql, "--json", "--paginate"])
        if not raw:
            return []
        data = json.loads(raw)
        if data is None:
            return []
        issues = data if isinstance(data, list) else [data]
        return [i["key"] for i in issues if isinstance(i, dict) and "key" in i]
    except Exception as e:
        print(f"  [WARN] Children search failed for {len(parent_keys)} parents: {e}", file=sys.stderr)
        return []


def fetch_children_keys_parallel(parent_keys: list[str]) -> list[str]:
    """Fetch child keys for all parents, batched and parallel."""
    if not parent_keys:
        return []

    batches = [parent_keys[i:i + BATCH_SIZE] for i in range(0, len(parent_keys), BATCH_SIZE)]

    if len(batches) == 1:
        return _fetch_children_keys_batch(batches[0])

    all_keys: list[str] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_fetch_children_keys_batch, batch): batch for batch in batches}
        for future in as_completed(futures):
            try:
                all_keys.extend(future.result())
            except Exception as e:
                print(f"  [WARN] Parallel batch failed: {e}", file=sys.stderr)

    return all_keys


def fetch_by_key_parallel(keys: list[str]) -> dict[str, dict]:
    """Fetch metadata for keys, batched and parallel."""
    if not keys:
        return {}

    batches = [keys[i:i + BATCH_SIZE] for i in range(0, len(keys), BATCH_SIZE)]

    if len(batches) == 1:
        return _fetch_batch_by_key(batches[0])

    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_fetch_batch_by_key, batch): batch for batch in batches}
        for future in as_completed(futures):
            try:
                batch_result = future.result()
                results.update(batch_result)
            except Exception as e:
                print(f"  [WARN] Parallel batch failed: {e}", file=sys.stderr)

    return results


def discover_tree(entry_point: str, max_depth: int) -> dict[str, dict]:
    """BFS tree discovery: fast children search + parallel metadata fetch."""
    print(f"Discovering Jira tree from {entry_point} (max depth: {max_depth})...")

    # Fetch root
    try:
        raw = run_acli(["view", entry_point, "--json", "--fields", METADATA_FIELDS])
        data = json.loads(raw)
        issue = data if isinstance(data, dict) else data[0]
        root = _parse_issue(issue, entry_point)
    except Exception as e:
        print(f"ERROR: Could not fetch entry point {entry_point}: {e}", file=sys.stderr)
        sys.exit(1)

    nodes: dict[str, dict] = {root["key"]: root}
    current_level = [root["key"]]
    depth = 0

    while current_level and depth < max_depth:
        depth += 1
        print(f"  Level {depth}: searching children of {len(current_level)} items...")

        # Step 1: Fast children key discovery (no fields)
        child_keys = fetch_children_keys_parallel(current_level)

        if not child_keys:
            break

        # Step 2: Fetch full metadata for children (batch 100, parallel)
        print(f"    Fetching metadata for {len(child_keys)} items...")
        children = fetch_by_key_parallel(child_keys)

        next_level = []
        for key, meta in children.items():
            nodes[key] = meta
            parent_key = meta.get("parent")
            if parent_key and parent_key in nodes:
                if key not in nodes[parent_key]["children"]:
                    nodes[parent_key]["children"].append(key)
            next_level.append(key)

        print(f"    Found {len(next_level)} items at level {depth}")
        current_level = next_level

    return nodes


# --- Manifest operations ---

def load_manifest(path: Path) -> dict:
    """Load existing manifest or create empty one."""
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("format_version") == 1:
                return data
            print("  [INFO] Old manifest format detected, starting fresh.", file=sys.stderr)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [WARN] Could not load manifest: {e}. Starting fresh.", file=sys.stderr)

    return {
        "format_version": 1,
        "last_updated": None,
        "entry_points": [],
        "nodes": {},
    }


def merge_into_manifest(manifest: dict, discovered: dict[str, dict], entry_point: str):
    """Merge discovered nodes into existing manifest. Always extend/update, never remove."""
    if entry_point not in manifest["entry_points"]:
        manifest["entry_points"].append(entry_point)

    for key, node in discovered.items():
        existing = manifest["nodes"].get(key)

        new_node = {
            "type": node["type"],
            "summary": node["summary"],
            "status": node["status"],
            "updated": node["updated"],
            "assignee": node["assignee"],
            "comment_count": node["comment_count"],
            "parent": node["parent"],
            "children": node["children"],
            "deps_out": node["deps_out"],
            "deps_in": node["deps_in"],
            "blocks": node["blocks"],
            "blocked_by": node["blocked_by"],
            "owning_program": node.get("owning_program"),
            "team": node.get("team"),
        }

        if existing is None:
            manifest["nodes"][key] = new_node
        else:
            existing["type"] = new_node["type"]
            existing["summary"] = new_node["summary"]
            existing["status"] = new_node["status"]
            existing["updated"] = new_node["updated"]
            existing["assignee"] = new_node["assignee"]
            existing["comment_count"] = new_node["comment_count"]
            existing["parent"] = new_node["parent"]
            for child in new_node["children"]:
                if child not in existing["children"]:
                    existing["children"].append(child)
            existing["deps_out"] = new_node["deps_out"]
            existing["deps_in"] = new_node["deps_in"]
            existing["blocks"] = new_node["blocks"]
            existing["blocked_by"] = new_node["blocked_by"]
            if new_node["owning_program"]:
                existing["owning_program"] = new_node["owning_program"]
            if new_node["team"]:
                existing["team"] = new_node["team"]


def resolve_external_deps(manifest: dict, discovered: dict[str, dict]) -> int:
    """Fetch metadata for items referenced in deps but not yet in manifest."""
    external = set()
    for node in discovered.values():
        for dep_key in node["deps_out"] + node["deps_in"]:
            if dep_key not in manifest["nodes"]:
                external.add(dep_key)

    if not external:
        return 0

    print(f"\nResolving {len(external)} external dependencies...")
    resolved = fetch_by_key_parallel(list(external))

    for key, meta in resolved.items():
        manifest["nodes"][key] = {
            "type": meta["type"],
            "summary": meta["summary"],
            "status": meta["status"],
            "updated": meta["updated"],
            "assignee": meta["assignee"],
            "comment_count": meta["comment_count"],
            "parent": meta["parent"],
            "children": meta["children"],
            "deps_out": meta["deps_out"],
            "deps_in": meta["deps_in"],
            "blocks": meta["blocks"],
            "blocked_by": meta["blocked_by"],
            "owning_program": meta.get("owning_program"),
            "team": meta.get("team"),
        }

    missing = external - set(resolved.keys())
    for key in missing:
        print(f"  [WARN] Could not resolve: {key}", file=sys.stderr)
        manifest["nodes"][key] = {
            "type": "Unknown", "summary": "(unresolved)", "status": "Unknown",
            "updated": "", "assignee": "Unknown", "comment_count": 0,
            "parent": None, "children": [], "deps_out": [], "deps_in": [],
            "blocks": [], "blocked_by": [],
            "owning_program": None, "team": None,
        }

    print(f"  Resolved {len(resolved)} / {len(external)} dependencies")
    return len(external)


def ensure_bidirectional_deps(manifest: dict):
    """If A.deps_out has B, ensure B.deps_in has A. Same for blocks/blocked_by."""
    nodes = manifest["nodes"]
    for key, node in nodes.items():
        for dep_key in node.get("deps_out", []):
            if dep_key in nodes:
                if key not in nodes[dep_key].setdefault("deps_in", []):
                    nodes[dep_key]["deps_in"].append(key)
        for dep_key in node.get("deps_in", []):
            if dep_key in nodes:
                if key not in nodes[dep_key].setdefault("deps_out", []):
                    nodes[dep_key]["deps_out"].append(key)
        for dep_key in node.get("blocks", []):
            if dep_key in nodes:
                if key not in nodes[dep_key].setdefault("blocked_by", []):
                    nodes[dep_key]["blocked_by"].append(key)
        for dep_key in node.get("blocked_by", []):
            if dep_key in nodes:
                if key not in nodes[dep_key].setdefault("blocks", []):
                    nodes[dep_key]["blocks"].append(key)


def compute_delta(discovered: dict[str, dict], pre_state: dict[str, dict]) -> dict:
    """Compare discovered nodes against manifest's pre-crawl state."""
    new_keys = []
    changed_keys = []
    unchanged_keys = []

    for key in sorted(discovered.keys()):
        if key not in pre_state:
            new_keys.append(key)
        else:
            prev = pre_state[key]
            node = discovered[key]
            if (node["status"] != prev.get("status") or
                node["updated"] != prev.get("updated") or
                node["comment_count"] != prev.get("comment_count")):
                changed_keys.append(key)
            else:
                unchanged_keys.append(key)

    return {
        "first_crawl": len(pre_state) == 0,
        "new_keys": new_keys,
        "changed_keys": changed_keys,
        "unchanged_keys": unchanged_keys,
    }


def save_manifest(manifest: dict, path: Path):
    """Write manifest to disk."""
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Discover Jira hierarchy via acli")
    parser.add_argument("entry_point", help="Jira issue key (e.g. PROJ-1000)")
    parser.add_argument("--depth", type=int, default=20, help="Max traversal depth (default: 20)")
    args = parser.parse_args()

    # Load existing manifest (or create empty)
    manifest = load_manifest(MANIFEST_PATH)
    pre_state = {k: dict(v) for k, v in manifest["nodes"].items()}

    # Discover tree via BFS (combined children+metadata fetch)
    discovered = discover_tree(args.entry_point, args.depth)

    # Merge into manifest
    merge_into_manifest(manifest, discovered, args.entry_point)

    # Resolve external dependencies
    ext_count = resolve_external_deps(manifest, discovered)

    # Ensure bidirectional dep + blocking consistency
    ensure_bidirectional_deps(manifest)

    # Compute delta
    delta = compute_delta(discovered, pre_state)

    # Save
    save_manifest(manifest, MANIFEST_PATH)

    # Print summary
    print(f"\nManifest: {MANIFEST_PATH}")
    print(f"  Entry points: {', '.join(manifest['entry_points'])}")
    print(f"  Total nodes: {len(manifest['nodes'])}")
    print(f"  Discovered this run: {len(discovered)}")
    if ext_count:
        print(f"  External deps resolved: {ext_count}")

    type_counts: dict[str, int] = {}
    for node in discovered.values():
        t = node["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"    {t}: {c}")

    # Delta
    if delta["first_crawl"]:
        print(f"\nDelta: FIRST CRAWL — all {len(delta['new_keys'])} items are new")
    else:
        print(f"\nDelta: {len(delta['new_keys'])} new, {len(delta['changed_keys'])} changed, "
              f"{len(delta['unchanged_keys'])} unchanged")
        if delta["new_keys"]:
            print(f"  New: {', '.join(delta['new_keys'][:10])}{'...' if len(delta['new_keys']) > 10 else ''}")
        if delta["changed_keys"]:
            print(f"  Changed: {', '.join(delta['changed_keys'][:10])}{'...' if len(delta['changed_keys']) > 10 else ''}")


if __name__ == "__main__":
    main()
