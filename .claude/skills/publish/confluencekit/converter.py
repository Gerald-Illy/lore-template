"""converter.py — Markdown to Confluence storage format converter.

Pure functions, no side effects. Converts standard markdown (headings, tables,
lists, bold, code, links, blockquotes) to Confluence storage XML.
"""

import re


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_inline(text: str) -> str:
    """Convert inline markdown (links, bold, code) to storage format."""
    links = []

    def stash_link(m):
        links.append((m.group(1), m.group(2)))
        return f"\x00L{len(links)-1}\x00"

    text = re.sub(r'\[([^\]]*)\]\(([^)]+)\)', stash_link, text)
    text = escape_xml(text)

    def restore_link(m):
        label, url = links[int(m.group(1))]
        return f'<a href="{url}">{label}</a>'

    text = re.sub(r'\x00L(\d+)\x00', restore_link, text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def md_to_storage(md: str) -> str:
    """Convert a markdown string to Confluence storage format XML."""
    lines = md.split('\n')
    out = []
    in_table = False
    header_done = False
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append('</ul>')
            in_list = False

    def close_table():
        nonlocal in_table, header_done
        if in_table:
            out.append('</tbody></table>')
            in_table = False
            header_done = False

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        i += 1

        if line.startswith('**Created by:**') or line.startswith('**Modified last by:**'):
            close_list()
            close_table()
            out.append(f'<p><em>{format_inline(line)}</em></p>')
            continue

        if re.match(r'^-{3,}$', line):
            close_list()
            close_table()
            out.append('<hr/>')
            continue

        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m and not in_table:
            close_list()
            close_table()
            lvl = len(m.group(1))
            out.append(f'<h{lvl}>{format_inline(m.group(2))}</h{lvl}>')
            continue

        if line.startswith('> '):
            close_list()
            close_table()
            out.append(f'<blockquote><p>{format_inline(line[2:])}</p></blockquote>')
            continue

        if line.startswith('|'):
            close_list()
            if re.match(r'^\|[\s\-\|:]+\|$', line):
                header_done = True
                continue
            if not in_table:
                out.append('<table><colgroup><col/></colgroup><tbody>')
                in_table = True
                header_done = False
            cells = [c.strip() for c in line[1:-1].split('|')]
            if not header_done:
                row = '<tr>' + ''.join(
                    f'<th><p>{format_inline(c)}</p></th>' for c in cells
                ) + '</tr>'
            else:
                row = '<tr>' + ''.join(
                    f'<td><p>{format_inline(c)}</p></td>' for c in cells
                ) + '</tr>'
            out.append(row)
            continue
        else:
            close_table()

        m = re.match(r'^\s*[-*]\s+(.+)$', raw)
        if m:
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'<li>{format_inline(m.group(1))}</li>')
            continue

        if not line:
            close_list()
            continue

        close_list()
        out.append(f'<p>{format_inline(line)}</p>')

    close_list()
    close_table()
    return '\n'.join(out)


def autogen_banner(github_repo: str, source_path: str) -> str:
    """Generate the auto-generated page info macro."""
    return (
        '<ac:structured-macro ac:name="info" ac:schema-version="1">'
        '<ac:parameter ac:name="title">Auto-generated page</ac:parameter>'
        '<ac:rich-text-body>'
        '<p>This page is generated from '
        f'<a href="{github_repo}/blob/main/{source_path}">'
        f'{source_path}</a> in '
        f'<a href="{github_repo}">{github_repo.split("/")[-1]}</a> on GitHub. '
        'Do not edit manually — changes will be overwritten on the next update.</p>'
        '</ac:rich-text-body>'
        '</ac:structured-macro>'
    )
