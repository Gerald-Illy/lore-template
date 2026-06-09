"""api.py — Confluence REST API helpers.

All functions take an ``auth`` dict with keys ``base_url``, ``email``, ``token``.
"""

import json
import base64
import urllib.request
import urllib.error
from pathlib import Path


def _headers(auth: dict) -> dict:
    """Build common request headers from auth dict."""
    creds = base64.b64encode(
        f"{auth['email']}:{auth['token']}".encode()
    ).decode()
    return {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def api(url: str, headers: dict, method: str = "GET", payload: dict | None = None):
    """Generic REST call. Returns (status_code, response_body)."""
    req = urllib.request.Request(url, headers=headers, method=method)
    if payload is not None:
        req.data = json.dumps(payload).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body


def get_page_version(auth: dict, page_id: str):
    """Resolve current page version. Returns (version_number, status) or (None, None)."""
    headers = _headers(auth)
    for status in ("current", "draft"):
        code, resp = api(
            f"{auth['base_url']}/wiki/rest/api/content/{page_id}"
            f"?status={status}&expand=version,space",
            headers,
        )
        if code == 200:
            return resp["version"]["number"], resp.get("status", status)
    return None, None


def publish_page(
    auth: dict,
    page_id: str,
    title: str,
    storage_body: str,
    version: int,
) -> tuple[int, dict | str]:
    """PUT updated content to an existing Confluence page."""
    headers = _headers(auth)
    payload = {
        "version": {"number": version},
        "title": title,
        "type": "page",
        "status": "current",
        "body": {
            "storage": {
                "value": storage_body,
                "representation": "storage",
            }
        },
    }
    return api(
        f"{auth['base_url']}/wiki/rest/api/content/{page_id}",
        headers,
        method="PUT",
        payload=payload,
    )


def create_subpage(
    auth: dict,
    parent_id: str,
    space_key: str,
    title: str,
    storage_body: str,
) -> tuple[int, dict | str]:
    """Create a new child page under parent_id."""
    headers = _headers(auth)
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "ancestors": [{"id": parent_id}],
        "body": {
            "storage": {
                "value": storage_body,
                "representation": "storage",
            }
        },
    }
    return api(
        f"{auth['base_url']}/wiki/rest/api/content",
        headers,
        method="POST",
        payload=payload,
    )


def delete_page(auth: dict, page_id: str) -> tuple[int, dict | str]:
    """Delete a Confluence page by ID."""
    headers = _headers(auth)
    req = urllib.request.Request(
        f"{auth['base_url']}/wiki/rest/api/content/{page_id}",
        headers={"Authorization": headers["Authorization"]},
        method="DELETE",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body


def upload_attachment(
    auth: dict, page_id: str, file_path: Path
) -> tuple[int, dict | str]:
    """Upload or replace a file attachment on a Confluence page."""
    filename = file_path.name
    data = file_path.read_bytes()
    boundary = "----------FormBoundaryXyZ"

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: text/html\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()

    auth_header = _headers(auth)["Authorization"]
    upload_headers = {
        "Authorization": auth_header,
        "X-Atlassian-Token": "no-check",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    check_url = (
        f"{auth['base_url']}/wiki/rest/api/content/{page_id}/child/attachment"
        f"?filename={filename}"
    )
    req = urllib.request.Request(
        check_url,
        headers={"Authorization": auth_header, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            results = json.loads(r.read().decode("utf-8")).get("results", [])
    except Exception:
        results = []

    if results:
        att_id = results[0]["id"]
        post_url = f"{auth['base_url']}/wiki/rest/api/content/{page_id}/child/attachment/{att_id}/data"
    else:
        post_url = f"{auth['base_url']}/wiki/rest/api/content/{page_id}/child/attachment"

    req = urllib.request.Request(
        post_url, data=body, headers=upload_headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_str = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body_str)
        except Exception:
            return e.code, body_str


def set_width(auth: dict, page_id: str, width: str = "wide"):
    """Set page display width. Values: 'default' (Narrow), 'wide', 'full-width' (Max)."""
    headers = _headers(auth)
    for key in ["content-appearance-published", "content-appearance-draft"]:
        code, _ = api(
            f"{auth['base_url']}/wiki/rest/api/content/{page_id}/property",
            headers,
            method="POST",
            payload={"key": key, "value": width},
        )
        if code == 409:
            _, prop = api(
                f"{auth['base_url']}/wiki/rest/api/content/{page_id}/property/{key}",
                headers,
            )
            v = prop.get("version", {}).get("number", 1)
            code, _ = api(
                f"{auth['base_url']}/wiki/rest/api/content/{page_id}/property/{key}",
                headers,
                method="PUT",
                payload={"key": key, "value": width, "version": {"number": v + 1}},
            )
        print(f"  {key}: HTTP {code}")
