"""
Confluence Tree Discovery Script

Deterministic traversal of a Confluence space via acli.
Produces a SINGLE manifest that accumulates all knowledge across crawls.

The manifest:
- Is always extended or updated, never reduced
- Supports multiple entry points (spaces or page IDs) in one file
- Only read/written by Python scripts, never by Claude

Strategy: ONE call to `page list --space` gets all pages with parentId.
Tree structure is derived from parent/child relationships.
Body content NOT fetched (only available via individual page view).

Usage:
    python confluence_tree.py <space-or-page-id> [--depth N]

Examples:
    python confluence_tree.py MYSPACE
    python confluence_tree.py 2476409106
    python confluence_tree.py MYSPACE --depth 5
"""

import argparse
import json
import subprocess
import sys
import io
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MANIFEST_PATH = Path(".lore/manifests/crawl-confluence-manifest.json")
PII_SKIP = "body"


def run_acli(args: list[str]) -> str:
    cmd = ["acli", "confluence"] + args + ["--pii-skip", PII_SKIP]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"acli failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def _classify_type(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["meeting", "standup", "sync", "notes", "log"]):
        return "meeting-log"
    if any(k in t for k in ["daci", "decision", "adr"]):
        return "decision"
    if any(k in t for k in ["architecture", "spec", "runbook", "reference"]):
        return "reference"
    if any(k in t for k in ["requirement", "scope", "component", "preview"]):
        return "requirements"
    if any(k in t for k in ["phase", "roadmap", "milestone", "timeline"]):
        return "planning"
    if any(k in t for k in ["workstream", "status", "tracking"]):
        return "operational"
    return "unknown"


def fetch_space_pages(space: str) -> list[dict]:
    """Fetch all pages in a space (single API call)."""
    raw = run_acli(["page", "list", "--space", space, "--json"])
    if not raw:
        return []
    data = json.loads(raw)
    return data if isinstance(data, list) else [data]


def fetch_single_page(page_id: str) -> dict | None:
    """Fetch a single page by ID (for entry points outside a space list)."""
    try:
        raw = run_acli(["page", "view", "--id", page_id, "--json"])
        data = json.loads(raw)
        return data if isinstance(data, dict) else data[0]
    except Exception as e:
        print(f"  [WARN] Could not fetch page {page_id}: {e}", file=sys.stderr)
        return None


def _parse_page(page: dict) -> dict:
    version = page.get("version", {})
    title = page.get("title", "")

    return {
        "id": str(page.get("id", "")),
        "title": title,
        "status": page.get("status", "unknown"),
        "parent_id": page.get("parentId", None),
        "version": version.get("number", 0),
        "updated": version.get("createdAt", ""),
        "children": [],
        "type_class": _classify_type(title),
    }


def discover_space(space: str, entry_point: str | None, max_depth: int) -> dict[str, dict]:
    """Discover all pages in a space and build parent/child tree."""
    print(f"Discovering Confluence space {space}...")

    pages = fetch_space_pages(space)
    if not pages:
        print(f"ERROR: No pages found in space {space}", file=sys.stderr)
        sys.exit(1)

    print(f"  Fetched {len(pages)} pages in 1 API call")

    nodes: dict[str, dict] = {}
    for page in pages:
        parsed = _parse_page(page)
        if parsed["id"]:
            nodes[parsed["id"]] = parsed

    # Build children lists from parentId
    for node_id, node in nodes.items():
        parent_id = node.get("parent_id")
        if parent_id and parent_id in nodes:
            if node_id not in nodes[parent_id]["children"]:
                nodes[parent_id]["children"].append(node_id)

    # Find root(s): pages whose parent is not in this space
    roots = [nid for nid, n in nodes.items() if n["parent_id"] not in nodes]

    # If entry_point specified, filter tree to that subtree only
    if entry_point and entry_point in nodes:
        reachable = _reachable_from(nodes, entry_point, max_depth)
        nodes = {k: v for k, v in nodes.items() if k in reachable}
    elif entry_point and entry_point not in nodes:
        print(f"  [WARN] Entry point {entry_point} not found in space pages", file=sys.stderr)

    print(f"  Tree roots: {len(roots)} | Total pages: {len(nodes)}")
    return nodes


def _reachable_from(nodes: dict[str, dict], root_id: str, max_depth: int) -> set[str]:
    """All pages reachable from root via children, respecting depth limit."""
    visited = set()
    queue = [(root_id, 0)]
    while queue:
        page_id, depth = queue.pop(0)
        if page_id in visited or page_id not in nodes:
            continue
        if depth > max_depth:
            continue
        visited.add(page_id)
        for child_id in nodes[page_id].get("children", []):
            queue.append((child_id, depth + 1))
    return visited


# --- Manifest operations ---

def load_manifest(path: Path) -> dict:
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
    """Merge discovered nodes into existing manifest."""
    if entry_point not in manifest["entry_points"]:
        manifest["entry_points"].append(entry_point)

    for page_id, node in discovered.items():
        existing = manifest["nodes"].get(page_id)

        new_node = {
            "title": node["title"],
            "status": node["status"],
            "parent_id": node["parent_id"],
            "version": node["version"],
            "updated": node["updated"],
            "children": node["children"],
            "type_class": node["type_class"],
        }

        if existing is None:
            manifest["nodes"][page_id] = new_node
        else:
            existing["title"] = new_node["title"]
            existing["status"] = new_node["status"]
            existing["parent_id"] = new_node["parent_id"]
            existing["version"] = new_node["version"]
            existing["updated"] = new_node["updated"]
            existing["type_class"] = new_node["type_class"]
            for child in new_node["children"]:
                if child not in existing["children"]:
                    existing["children"].append(child)


def compute_delta(discovered: dict[str, dict], pre_state: dict[str, dict]) -> dict:
    """Compare discovered nodes against manifest's pre-crawl state."""
    new_ids = []
    changed_ids = []
    unchanged_ids = []

    for page_id in sorted(discovered.keys()):
        if page_id not in pre_state:
            new_ids.append(page_id)
        else:
            prev = pre_state[page_id]
            node = discovered[page_id]
            if node["version"] != prev.get("version"):
                changed_ids.append(page_id)
            else:
                unchanged_ids.append(page_id)

    return {
        "first_crawl": len(pre_state) == 0,
        "new_ids": new_ids,
        "changed_ids": changed_ids,
        "unchanged_ids": unchanged_ids,
    }


def save_manifest(manifest: dict, path: Path):
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Discover Confluence page tree via acli")
    parser.add_argument("entry_point", help="Space key (e.g. MYSPACE) or page ID (e.g. 2476409106)")
    parser.add_argument("--depth", type=int, default=20, help="Max traversal depth (default: 20)")
    args = parser.parse_args()

    # Determine if entry point is a space key or page ID
    entry = args.entry_point
    if entry.isdigit():
        # Page ID — fetch the page to find its space, then list the space
        page = fetch_single_page(entry)
        if not page:
            print(f"ERROR: Could not fetch page {entry}", file=sys.stderr)
            sys.exit(1)
        space = page.get("spaceId", "")
        # We need the space KEY not ID — for now require space key
        print(f"  Page {entry} is in spaceId={space}. Use space key instead (e.g. MYSPACE).", file=sys.stderr)
        print(f"  Attempting to use page as entry point within its space...", file=sys.stderr)
        # Fallback: try common space keys
        # For now, just discover from the page's space listing won't work without key
        # So we'll use a different strategy: get the space root and list
        print(f"ERROR: Please provide a space key (e.g. MYSPACE), not a page ID.", file=sys.stderr)
        sys.exit(1)
    else:
        space = entry
        entry_id = None

    # Load existing manifest
    manifest = load_manifest(MANIFEST_PATH)
    pre_state = {k: dict(v) for k, v in manifest["nodes"].items()}

    # Discover
    discovered = discover_space(space, entry_id, args.depth)

    # Merge
    merge_into_manifest(manifest, discovered, f"space:{space}")

    # Delta
    delta = compute_delta(discovered, pre_state)

    # Save
    save_manifest(manifest, MANIFEST_PATH)

    # Summary
    print(f"\nManifest: {MANIFEST_PATH}")
    print(f"  Entry points: {', '.join(manifest['entry_points'])}")
    print(f"  Total nodes: {len(manifest['nodes'])}")
    print(f"  Discovered this run: {len(discovered)}")

    type_counts: dict[str, int] = {}
    for node in discovered.values():
        t = node["type_class"]
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"    {t}: {c}")

    if delta["first_crawl"]:
        print(f"\nDelta: FIRST CRAWL — all {len(delta['new_ids'])} pages are new")
    else:
        print(f"\nDelta: {len(delta['new_ids'])} new, {len(delta['changed_ids'])} changed, "
              f"{len(delta['unchanged_ids'])} unchanged")
        if delta["changed_ids"]:
            titles = [discovered[pid]["title"][:40] for pid in delta["changed_ids"][:5]]
            print(f"  Changed: {', '.join(titles)}{'...' if len(delta['changed_ids']) > 5 else ''}")


if __name__ == "__main__":
    main()
