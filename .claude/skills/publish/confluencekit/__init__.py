"""confluencekit — Publish markdown and HTML artifacts to Confluence pages.

Uses system keyring for API token storage (no .env needed).

Usage from a per-artifact update-confluence.py::

    import sys
    from pathlib import Path

    def _repo_root():
        d = Path(__file__).resolve().parent
        while d != d.parent:
            if (d / "CLAUDE.md").exists():
                return d
            d = d.parent

    sys.path.insert(0, str(_repo_root() / ".claude" / "skills" / "publish" / "confluencekit"))
    from confluencekit import publish, embed_html, set_token

    # Publish markdown
    publish(
        page_id="123456",
        title="My Page Title",
        md_file=Path(__file__).parent / "artifact.md",
        base_url="https://your-instance.atlassian.net",
        email="user@company.com",
    )

    # Embed HTML via Forge macro
    embed_html("123456", Path(__file__).parent / "dashboard.html")

Token setup (one-time)::

    python -c "import keyring; keyring.set_password('confluencekit', 'you@company.com', 'YOUR_TOKEN')"
"""
