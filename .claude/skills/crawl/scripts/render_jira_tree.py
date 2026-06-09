"""
Render Jira Tree as formatted text output.

Reads the unified crawl-jira-manifest.json and outputs a clean, column-aligned tree.
Format: Key | Summary | Status | @Assignee | [Location] | Stories

Items sorted by natural key order (PROJECT-1, PROJECT-2, ..., PROJECT-10).

Usage:
    python render_jira_tree.py [--manifest PATH] [--entry-point KEY]

Examples:
    python render_jira_tree.py
    python render_jira_tree.py --entry-point PROJ-1000

Default manifest: .lore/manifests/crawl-jira-manifest.json
Default entry point: first in manifest's entry_points list
"""

import argparse
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MANIFEST_PATH = Path(".lore/manifests/crawl-jira-manifest.json")

# --- Config ---

OP_SHORT = {
    # Configure per instance: map owning program display names to short codes
    # "Program Display Name": "SHORT",
}

TEAM_SHORT = {
    # Configure per instance: map team names to short display codes
    # "Full Team Name": "Short",
}

# Column widths
COL_A = 30   # tree + type + key
COL_B = 42   # summary
COL_C = 18   # status
COL_D = 24   # assignee
COL_E = 16   # location
# Col F: stories (variable, at end)


# --- Helpers ---

def key_sort(key):
    """Natural sort for Jira keys: PROJECT-1 < PROJECT-2 < PROJECT-10."""
    parts = key.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return (parts[0], int(parts[1]))
    return (key, 0)


def short_op(op):
    if not op:
        return None
    return OP_SHORT.get(op, op)


def team_short(team_raw):
    if not team_raw:
        return None
    t = team_raw.replace("[DTT] ", "").replace("[Archived] ", "").strip()
    if t.startswith("team-"):
        t = t[5:]
    if "<PERSON" in t:
        return None
    return TEAM_SHORT.get(t, t)


def project_from_key(key):
    return key.split("-")[0] if "-" in key else "?"


def trunc(s, n):
    if len(s) <= n - 2:
        return s
    return s[:n - 3] + "\u2026"


def children_of(nodes, key):
    return sorted(
        [ck for ck in nodes.get(key, {}).get("children", []) if ck in nodes],
        key=key_sort
    )


def story_count(nodes, epic_key):
    kids = children_of(nodes, epic_key)
    done = sum(1 for k in kids if nodes[k]["status"] in ("Closed", "Done", "Resolved"))
    return len(kids), done


def blocking_deps_for(nodes, key):
    """Get items that block this node (blocked_by field)."""
    node = nodes.get(key, {})
    blocked_by = node.get("blocked_by", [])
    if not blocked_by:
        return None

    blocking = [dk for dk in blocked_by if dk in nodes]
    if not blocking:
        return None

    all_resolved = all(
        nodes.get(dk, {}).get("status", "") in ("Resolved", "Closed", "Done")
        for dk in blocking
    )

    if all_resolved:
        return f"\u26a1 {len(blocking)} blocking: {', '.join(sorted(blocking, key=key_sort))} (all Resolved)"
    else:
        parts = []
        for dk in sorted(blocking, key=key_sort):
            st = nodes.get(dk, {}).get("status", "?")
            parts.append(f"{dk} ({st})")
        return f"\u26a1 {len(blocking)} blocking: {', '.join(parts)}"


def tree_keys(nodes, root_key):
    """All keys reachable via parent/child from root."""
    visited = set()
    queue = [root_key]
    while queue:
        key = queue.pop(0)
        if key in visited or key not in nodes:
            continue
        visited.add(key)
        queue.extend(nodes[key].get("children", []))
    return visited


def render(manifest_path: Path, entry_point: str | None):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    nodes = manifest["nodes"]

    if not entry_point:
        if not manifest.get("entry_points"):
            print("ERROR: No entry points in manifest", file=sys.stderr)
            sys.exit(1)
        entry_point = manifest["entry_points"][0]

    if entry_point not in nodes:
        print(f"ERROR: Entry point {entry_point} not found in manifest", file=sys.stderr)
        sys.exit(1)

    root = nodes[entry_point]
    op_root = short_op(root.get("owning_program")) or project_from_key(entry_point)

    # Header
    col_a = f"VP  {entry_point}"
    col_b = trunc(root["summary"], COL_B)
    col_c = root["status"]
    col_e = f"[{op_root}]"
    print(f"{col_a:<{COL_A}}{col_b:<{COL_B}}{col_c:<{COL_C}}{'':<{COL_D}}{col_e}")
    print("\u2502")

    vis = children_of(nodes, entry_point)

    for vi_idx, vi_key in enumerate(vis):
        vi = nodes[vi_key]
        is_last_vi = (vi_idx == len(vis) - 1)
        br = "\u2514" if is_last_vi else "\u251c"
        co = " " if is_last_vi else "\u2502"

        op = short_op(vi.get("owning_program")) or project_from_key(vi_key)
        assignee = vi.get("assignee", "Unassigned")
        a_str = f"@{assignee}" if assignee != "Unassigned" else ""

        epics = [k for k in children_of(nodes, vi_key) if nodes[k]["type"] == "Epic"]
        has_children = bool(epics)

        col_a = f"{br}\u2500 VI  {vi_key}"
        col_b = trunc(vi["summary"], COL_B)
        col_c = vi["status"]
        col_d = a_str
        col_e = f"[{op}]"
        print(f"{col_a:<{COL_A}}{col_b:<{COL_B}}{col_c:<{COL_C}}{col_d:<{COL_D}}{col_e}")

        for ep_idx, ep_key in enumerate(epics):
            ep = nodes[ep_key]
            is_last_ep = (ep_idx == len(epics) - 1)
            eb = "\u2514" if is_last_ep else "\u251c"

            proj = project_from_key(ep_key)
            team = team_short(ep.get("team"))
            loc = f"{proj}/{team}" if team else proj

            assignee = ep.get("assignee", "Unassigned")
            a_str = f"@{assignee}" if assignee != "Unassigned" else ""

            sc, done = story_count(nodes, ep_key)
            story_str = ""
            if sc:
                if done == sc:
                    story_str = f"\u2190 {sc} stories (all closed)"
                elif done == 0:
                    story_str = f"\u2190 {sc} stories"
                else:
                    story_str = f"\u2190 {sc} stories ({done} closed)"

            col_a = f"{co}   {eb}\u2500 Epic {ep_key}"
            col_b = trunc(ep["summary"], COL_B)
            col_c = ep["status"]
            col_d = a_str
            col_e = f"[{loc}]"
            col_f = story_str
            print(f"{col_a:<{COL_A}}{col_b:<{COL_B}}{col_c:<{COL_C}}{col_d:<{COL_D}}{col_e:<{COL_E}} {col_f}")

            bd = blocking_deps_for(nodes, ep_key)
            if bd:
                print(f"{co}      {bd}")

        if has_children and not is_last_vi:
            print(f"{co}")

    # Footer
    tk = tree_keys(nodes, entry_point)
    vi_count = sum(1 for k in children_of(nodes, entry_point) if nodes[k]["type"] == "ValueIncrement")
    ep_count = sum(1 for k in tk if nodes[k]["type"] == "Epic")
    print()
    print(f"{len(tk)} items in tree | {vi_count} VIs | {ep_count} Epics | {len(nodes)} total in manifest")


def main():
    parser = argparse.ArgumentParser(description="Render Jira tree as formatted text")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH, help="Path to manifest JSON")
    parser.add_argument("--entry-point", type=str, default=None, help="Entry point key (default: first in manifest)")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"ERROR: Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    render(args.manifest, args.entry_point)


if __name__ == "__main__":
    main()
