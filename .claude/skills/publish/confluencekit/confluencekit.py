"""confluencekit.py — Publish markdown and HTML artifacts to Confluence pages.

Token is stored in the system keyring. On first run or when the token
expires, the user is guided through setup automatically.
"""

import getpass
import os
import sys
import uuid
from pathlib import Path
from xml.sax.saxutils import escape

from api import (
    _headers,
    api,
    get_page_version,
    publish_page,
    set_width,
    upload_attachment,
)
from converter import autogen_banner, md_to_storage

KEYRING_SERVICE = "confluencekit"
TOKEN_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"

# Forge HTML macro constants — configure per Confluence instance
# These IDs are specific to your Forge app installation
FORGE_EXT_KEY    = "YOUR_FORGE_EXTENSION_KEY"
FORGE_CLOUD_ID   = "YOUR_CLOUD_ID"
FORGE_ACCOUNT_ID = "YOUR_ACCOUNT_ID"
FORGE_SPACE_ID   = "YOUR_SPACE_ID"
FORGE_SPACE_KEY  = "YOUR_SPACE_KEY"


# ─── Token Management ────────────────────────────────────────────────────────


def _get_keyring():
    """Import keyring or return None with a helpful message."""
    try:
        import keyring
        return keyring
    except ImportError:
        print("NOTE: 'keyring' package not installed. Install with: pip install keyring")
        print("      Without it, you'll need to enter your token every time.\n")
        return None


def _resolve_token(email: str) -> str:
    """Resolve API token: keyring -> env var -> interactive prompt."""
    kr = _get_keyring()
    if kr:
        token = kr.get_password(KEYRING_SERVICE, email)
        if token:
            return token

    token = os.environ.get("ATLASSIAN_API_TOKEN")
    if token:
        return token

    return _interactive_token_setup(email)


def _interactive_token_setup(email: str) -> str:
    """Walk the user through token setup with clear instructions."""
    print()
    print("=" * 60)
    print("  Confluence API Token Setup")
    print("=" * 60)
    print()
    print("  To publish pages, you need an Atlassian API token.")
    print()
    print("  1. Open: " + TOKEN_URL)
    print("  2. Click 'Create API token'")
    print("  3. Name it 'My Project' (or anything you like)")
    print("  4. Copy the token and paste it below")
    print()
    token = getpass.getpass("  Paste your token here: ").strip()

    if not token:
        print("\n  No token entered. Exiting.")
        sys.exit(1)

    kr = _get_keyring()
    if kr:
        kr.set_password(KEYRING_SERVICE, email, token)
        print("\n  Token saved to system keyring. You won't need to enter it again.")
    else:
        print("\n  Token accepted (not saved — install 'keyring' to persist).")

    print()
    return token


def _handle_auth_failure(email: str) -> str:
    """Handle 401/403: explain what happened, get a new token."""
    print()
    print("=" * 60)
    print("  Token expired or invalid")
    print("=" * 60)
    print()
    print("  Your API token no longer works. This usually means")
    print("  it expired (tokens expire after 1 year).")
    print()
    print("  1. Open: " + TOKEN_URL)
    print("  2. Revoke the old token (if listed)")
    print("  3. Create a new one")
    print("  4. Paste it below")
    print()
    token = getpass.getpass("  Paste your new token here: ").strip()

    if not token:
        print("\n  No token entered. Exiting.")
        sys.exit(1)

    kr = _get_keyring()
    if kr:
        kr.set_password(KEYRING_SERVICE, email, token)
        print("\n  New token saved to system keyring.")
    else:
        print("\n  New token accepted (not saved — install 'keyring' to persist).")

    print()
    return token


def _resolve_auth(email: str = None, base_url: str = None) -> dict:
    """Build auth dict from email + resolved token."""
    if not base_url:
        base_url = os.environ.get("CONFLUENCE_BASE_URL")
    if not base_url:
        print("ERROR: No base_url provided and CONFLUENCE_BASE_URL not set.")
        print("       Pass base_url explicitly or set the environment variable.")
        sys.exit(1)
    if not email:
        email = os.environ.get("ATLASSIAN_EMAIL")
    if not email:
        print("ERROR: No email provided and ATLASSIAN_EMAIL not set.")
        sys.exit(1)
    token = _resolve_token(email)
    return {"base_url": base_url, "email": email, "token": token}


def set_token(email: str) -> None:
    """Manually store or replace an API token in the system keyring."""
    _interactive_token_setup(email)


# ─── Mode 1: Publish Markdown ────────────────────────────────────────────────


def publish(
    page_id: str,
    title: str,
    md_file: Path,
    base_url: str = None,
    email: str = None,
    html_file: Path | None = None,
    github_repo: str | None = None,
    source_path: str | None = None,
    width: str = "wide",
) -> None:
    """Publish a markdown artifact to a Confluence page."""
    if not md_file.exists():
        print(f"ERROR: Cannot find source file:\n  {md_file}")
        return

    print(f"Reading {md_file.name} ...")
    md = md_file.read_text(encoding="utf-8")

    auth = _resolve_auth(email, base_url)
    print(f"\nTarget page : {auth['base_url']}/wiki (ID {page_id})")
    print(f"Account     : {auth['email']}")

    print("\nLooking up page ...")
    version, current_status = get_page_version(auth, page_id)

    if version is None:
        code, _ = api(
            f"{auth['base_url']}/wiki/rest/api/content/{page_id}",
            _headers(auth),
        )
        if code in (401, 403):
            token = _handle_auth_failure(auth["email"])
            auth["token"] = token
            version, current_status = get_page_version(auth, page_id)

    if version is None:
        print("ERROR: Page not found. Check page_id and credentials.")
        return

    print(f"  Found: status={current_status}, version={version}")
    new_version = version if current_status == "draft" else version + 1

    embed_macro = ""
    if html_file and html_file.exists():
        print(f"\nUploading {html_file.name} ({html_file.stat().st_size // 1024} KB) ...")
        code, resp = upload_attachment(auth, page_id, html_file)
        att_url = f"{auth['base_url']}/wiki/download/attachments/{page_id}/{html_file.name}"
        if code in (200, 201):
            embed_macro = (
                '<ac:structured-macro ac:name="panel" ac:schema-version="1">'
                '<ac:parameter ac:name="title">Presentation</ac:parameter>'
                '<ac:parameter ac:name="borderStyle">solid</ac:parameter>'
                '<ac:parameter ac:name="borderColor">#0073e6</ac:parameter>'
                '<ac:parameter ac:name="titleBGColor">#0073e6</ac:parameter>'
                '<ac:parameter ac:name="titleColor">#ffffff</ac:parameter>'
                "<ac:rich-text-body>"
                f'<p><a href="{att_url}">&#9654; Open slideshow</a> '
                "&nbsp;&nbsp; The interactive HTML presentation opens directly in your browser.</p>"
                "</ac:rich-text-body>"
                "</ac:structured-macro>"
            )
            print(f"  Uploaded OK -> {att_url}")
        else:
            print(f"  Upload failed ({code}) — adding link only")
            embed_macro = f'<p><strong>Presentation:</strong> <a href="{att_url}">Open slideshow</a></p>'
    elif html_file:
        print(f"  {html_file.name} not found — skipping embed")

    banner = ""
    if github_repo and source_path:
        banner = autogen_banner(github_repo, source_path) + "\n"

    storage = banner + embed_macro + "\n" + md_to_storage(md)
    print(f"Storage format: {len(storage)} chars")

    print(f"\nPublishing version {new_version} ...")
    code, resp = publish_page(auth, page_id, title, storage, new_version)

    if code == 200:
        webui = resp.get("_links", {}).get("webui", "")
        print(f"\nDone! Page live at:")
        print(f"  {auth['base_url']}/wiki{webui}")
        set_width(auth, page_id, width)
    elif code in (401, 403):
        token = _handle_auth_failure(auth["email"])
        auth["token"] = token
        code, resp = publish_page(auth, page_id, title, storage, new_version)
        if code == 200:
            webui = resp.get("_links", {}).get("webui", "")
            print(f"\nDone! Page live at:")
            print(f"  {auth['base_url']}/wiki{webui}")
            set_width(auth, page_id, width)
        else:
            _print_error(code, resp)
    else:
        _print_error(code, resp)


# ─── Mode 2: Embed HTML via Forge Macro ──────────────────────────────────────


def _forge_html_body(page_id: str, next_version: int, html_escaped: str, layout: str = "full-width") -> str:
    """Build Forge HTML macro storage format XML."""
    local_id = str(uuid.uuid4())
    node = (
        f'<ac:adf-node type="extension">'
        f'<ac:adf-attribute key="extension-key">{FORGE_EXT_KEY}</ac:adf-attribute>'
        f'<ac:adf-attribute key="extension-type">com.atlassian.ecosystem</ac:adf-attribute>'
        f'<ac:adf-attribute key="parameters">'
        f'<ac:adf-parameter key="local-id">{local_id}</ac:adf-parameter>'
        f'<ac:adf-parameter key="extension-id">ari:cloud:ecosystem::extension/{FORGE_EXT_KEY}</ac:adf-parameter>'
        f'<ac:adf-parameter key="extension-title">HTML</ac:adf-parameter>'
        f'<ac:adf-parameter key="layout">extension</ac:adf-parameter>'
        f'<ac:adf-parameter key="forge-environment">PRODUCTION</ac:adf-parameter>'
        f'<ac:adf-parameter key="embedded-macro-context">'
        f'<ac:adf-parameter key="extension-data">'
        f'<ac:adf-parameter key="type">macro</ac:adf-parameter>'
        f'<ac:adf-parameter key="content"><ac:adf-parameter key="id">{page_id}</ac:adf-parameter>'
        f'<ac:adf-parameter key="type">page</ac:adf-parameter>'
        f'<ac:adf-parameter key="version" type="integer">{next_version}</ac:adf-parameter></ac:adf-parameter>'
        f'<ac:adf-parameter key="space"><ac:adf-parameter key="key">{FORGE_SPACE_KEY}</ac:adf-parameter>'
        f'<ac:adf-parameter key="id">{FORGE_SPACE_ID}</ac:adf-parameter></ac:adf-parameter>'
        f'</ac:adf-parameter></ac:adf-parameter>'
        f'<ac:adf-parameter key="context-ids">'
        f'<ac:adf-parameter-value>ari:cloud:confluence:{FORGE_CLOUD_ID}:workspace/40dd1ef9-fedf-445d-b410-f7d6702d9d77</ac:adf-parameter-value>'
        f'</ac:adf-parameter>'
        f'<ac:adf-parameter key="account-id">{FORGE_ACCOUNT_ID}</ac:adf-parameter>'
        f'<ac:adf-parameter key="cloud-id">{FORGE_CLOUD_ID}</ac:adf-parameter>'
        f'</ac:adf-parameter>'
        f'<ac:adf-parameter key="guest-params">'
        f'<ac:adf-parameter key="script" />'
        f'<ac:adf-parameter key="embed-h-t-m-l">{html_escaped}</ac:adf-parameter>'
        f'<ac:adf-parameter key="height" /><ac:adf-parameter key="find" />'
        f'<ac:adf-parameter key="replace" />'
        f'<ac:adf-parameter key="timeout">30000</ac:adf-parameter>'
        f'<ac:adf-parameter key="encoding">UTF-8</ac:adf-parameter>'
        f'<ac:adf-parameter key="output">html</ac:adf-parameter>'
        f'</ac:adf-parameter></ac:adf-attribute>'
        f'<ac:adf-attribute key="text">HTML</ac:adf-attribute>'
        f'<ac:adf-attribute key="layout">{layout}</ac:adf-attribute>'
        f'<ac:adf-attribute key="local-id">{local_id}</ac:adf-attribute>'
        f'</ac:adf-node>'
    )
    return f"<ac:adf-extension>{node}<ac:adf-fallback>{node}</ac:adf-fallback></ac:adf-extension>"


def embed_html(
    page_id: str,
    html_file: Path | str,
    base_url: str = None,
    email: str = None,
) -> None:
    """Embed an HTML file into a Confluence page via the bobswift Forge HTML macro."""
    html_file = Path(html_file)
    if not html_file.exists():
        print(f"ERROR: HTML file not found: {html_file}")
        return

    auth = _resolve_auth(email, base_url)

    print(f"Reading {html_file.name} ({html_file.stat().st_size // 1024} KB) ...")
    html_content = html_file.read_text(encoding="utf-8")
    html_escaped = escape(html_content)

    print(f"Looking up page {page_id} ...")
    version, current_status = get_page_version(auth, page_id)

    if version is None:
        code, _ = api(
            f"{auth['base_url']}/wiki/rest/api/content/{page_id}",
            _headers(auth),
        )
        if code in (401, 403):
            token = _handle_auth_failure(auth["email"])
            auth["token"] = token
            version, current_status = get_page_version(auth, page_id)

    if version is None:
        print("ERROR: Page not found. Check page_id and credentials.")
        return

    next_version = version + 1
    storage = _forge_html_body(page_id, next_version, html_escaped)

    # Get title for the update
    headers = _headers(auth)
    _, page_data = api(f"{auth['base_url']}/wiki/rest/api/content/{page_id}?expand=title", headers)
    title = page_data.get("title", "Untitled") if isinstance(page_data, dict) else "Untitled"

    print(f"Embedding HTML into '{title}' (v{next_version}) ...")
    code, result = publish_page(auth, page_id, title, storage, next_version)

    if code == 200:
        print(f"  HTTP {code} — v{result.get('version', {}).get('number', '?')}")
        set_width(auth, page_id, "full-width")
        print(f"  URL: {auth['base_url']}/wiki/spaces/{FORGE_SPACE_KEY}/pages/{page_id}")
    elif code in (401, 403):
        token = _handle_auth_failure(auth["email"])
        auth["token"] = token
        code, result = publish_page(auth, page_id, title, storage, next_version)
        if code == 200:
            print(f"  HTTP {code} — v{result.get('version', {}).get('number', '?')}")
            set_width(auth, page_id, "full-width")
            print(f"  URL: {auth['base_url']}/wiki/spaces/{FORGE_SPACE_KEY}/pages/{page_id}")
        else:
            _print_error(code, result)
    else:
        _print_error(code, result)


# ─── Utilities ────────────────────────────────────────────────────────────────


def _print_error(code, resp):
    """Print a formatted error message."""
    print(f"\nERROR ({code}):")
    if isinstance(resp, dict):
        import json
        print(json.dumps(resp, indent=2))
    else:
        print(resp)


# ─── CLI ─────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    if "--set-token" in sys.argv:
        email_arg = None
        for i, arg in enumerate(sys.argv):
            if arg == "--email" and i + 1 < len(sys.argv):
                email_arg = sys.argv[i + 1]
        if not email_arg:
            email_arg = input("Email: ")
        set_token(email_arg)
    elif "--embed" in sys.argv:
        # python confluencekit.py --embed <page_id> <html_file>
        args = [a for a in sys.argv[1:] if a != "--embed"]
        if len(args) < 2:
            print("Usage: python confluencekit.py --embed <page_id> <html_file>")
            sys.exit(1)
        embed_html(args[0], args[1])
    else:
        print("Usage:")
        print("  python confluencekit.py --set-token --email you@company.com")
        print("  python confluencekit.py --embed <page_id> <html_file>")
        print("  (normally called via update-confluence.py in your artifact folder)")
