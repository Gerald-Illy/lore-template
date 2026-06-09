"""
Render Confluence Tree as formatted text output.

Reads the unified crawl-confluence-manifest.json and outputs a clean tree.
Format: Title | Version | Updated | Type

Usage:
    python render_confluence_tree.py [--manifest PATH] [--entry-point SPACE:KEY]

Default manifest: .lore/manifests/crawl-confluence-manifest.json
Default entry point: first in manifest's entry_points list
"""

import argparse
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MANIFEST_PATH = Path(".lore/manifests/crawl-confluence-manifest.json")

# Column widths
COL_A = 34   # tree indent + title prefix
COL_B = 50   # title
COL_C = 6    # version
COL_D = 12   # updated date
COL_E = 14   # type class


TYPE_ICONS = {
    "decision": "\u2696",
    "meeting-log": "\U0001F4C5",
    "reference": "\U0001F4D6",
    "requirements": "\U0001F4CB",
    "planning": "\U0001F4C8",
    "operational": "\u2699",
    "unknown": " ",
}


def trunc(s, n):
    if len(s) <= n - 2:
        return s
    return s[:n - 3] + "\u2026"


def date_short(iso: str) -> str:
    if not iso:
        return "?"
    return iso[:10]


def children_of(nodes, page_id):
    children = nodes.get(page_id, {}).get("children", [])
    valid = [c for c in children if c in nodes]
    return sorted(valid, key=lambda c: nodes[c].get("title", "").lower())


def tree_size(nodes, root_id):
    """Count all pages reachable from root."""
    visited = set()
    queue = [root_id]
    while queue:
        pid = queue.pop(0)
        if pid in visited or pid not in nodes:
            continue
        visited.add(pid)
        queue.extend(nodes[pid].get("children", []))
    return len(visited)


def render_subtree(nodes, page_id, prefix="", is_last=True, depth=0, max_depth=20):
    if depth > max_depth or page_id not in nodes:
        return

    node = nodes[page_id]
    title = node.get("title", "?")
    version = node.get("version", 0)
    updated = date_short(node.get("updated", ""))
    type_class = node.get("type_class", "unknown")

    if depth == 0:
        connector = ""
        child_prefix = ""
    else:
        connector = "\u2514\u2500 " if is_last else "\u251c\u2500 "
        child_prefix = prefix + ("   " if is_last else "\u2502  ")

    line_prefix = f"{prefix}{connector}"
    col_b = trunc(title, COL_B)
    col_c = f"v{version}"
    col_d = updated
    col_e = type_class

    children = children_of(nodes, page_id)
    child_count = f" ({len(children)})" if children else ""

    print(f"{line_prefix}{col_b}{child_count:<{6}}{col_c:<{COL_C}} {col_d:<{COL_D}} [{col_e}]")

    for i, child_id in enumerate(children):
        is_last_child = (i == len(children) - 1)
        render_subtree(nodes, child_id, child_prefix, is_last_child, depth + 1, max_depth)


def render(manifest_path: Path, entry_point: str | None):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    nodes = manifest["nodes"]

    if not entry_point:
        if not manifest.get("entry_points"):
            print("ERROR: No entry points in manifest", file=sys.stderr)
            sys.exit(1)
        entry_point = manifest["entry_points"][0]

    # Find root page(s) for this entry point
    if entry_point.startswith("space:"):
        # Entry point is a space — find root pages (no parent in manifest)
        roots = [pid for pid, n in nodes.items() if n.get("parent_id") not in nodes]
        roots.sort(key=lambda pid: nodes[pid].get("title", "").lower())
    else:
        # Entry point is a page ID
        if entry_point not in nodes:
            print(f"ERROR: Entry point {entry_point} not found in manifest", file=sys.stderr)
            sys.exit(1)
        roots = [entry_point]

    for root_id in roots:
        root = nodes[root_id]
        size = tree_size(nodes, root_id)
        print(f"Space: {entry_point} | Root: {root.get('title', '?')} | {size} pages")
        print()
        render_subtree(nodes, root_id)

    # Footer
    type_counts: dict[str, int] = {}
    for node in nodes.values():
        t = node.get("type_class", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    print()
    type_str = ", ".join(f"{t}: {c}" for t, c in sorted(type_counts.items(), key=lambda x: -x[1]))
    print(f"{len(nodes)} pages in manifest | {type_str}")


def main():
    parser = argparse.ArgumentParser(description="Render Confluence tree as formatted text")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH, help="Path to manifest JSON")
    parser.add_argument("--entry-point", type=str, default=None, help="Entry point (default: first in manifest)")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"ERROR: Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    render(args.manifest, args.entry_point)


if __name__ == "__main__":
    main()
