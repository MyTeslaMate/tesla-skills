#!/usr/bin/env python3
"""
Tesla AI Agent — Anthropic SDK skill with OAuth authentication

Uses Dynamic Client Registration (DCR, RFC 7591) against the MyTeslaMate MCP
server.  On first run the skill registers itself, then runs the PKCE OAuth
flow via the MTM server (which proxies to Tesla).  The resulting MTM token is
cached locally and refreshed automatically on subsequent runs.

Usage:
    python tesla/tesla_skill.py "what is my battery level?"

Optional env vars:
    ANTHROPIC_API_KEY   — Anthropic API key (pay-as-you-go).
                          Omit when running inside Claude Code to use
                          subscription credentials instead.
    MTM_MCP_BASE_URL    — Base URL of the MTM MCP server
                          (default: https://mcp.myteslamate.com)
    MTM_CALLBACK_PORT   — Local callback port for OAuth redirect (default: 8085)
    MTM_TOKEN_CACHE     — Path to token cache file
                          (default: ~/.config/tesla-skill/token.json)
"""

import os
import sys
import json
import time
import secrets
import hashlib
import base64
import webbrowser
import urllib.parse
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests
import anthropic

# ---------------------------------------------------------------------------
# OAuth configuration
# ---------------------------------------------------------------------------
_MCP_BASE_URL = os.environ.get("MTM_MCP_BASE_URL", "https://mcp.myteslamate.com").rstrip("/")
_CALLBACK_PORT = int(os.environ.get("MTM_CALLBACK_PORT", "8085"))
_CALLBACK_URL = f"http://localhost:{_CALLBACK_PORT}/callback"
_TOKEN_CACHE = Path(
    os.environ.get("MTM_TOKEN_CACHE", Path.home() / ".config" / "tesla-skill" / "token.json")
)
_SCOPES = (
    "openid offline_access user_data vehicle_device_data vehicle_location "
    "vehicle_cmds vehicle_charging_cmds energy_device_data energy_cmds"
)

# Cached OAuth endpoints (populated by _discover_endpoints())
_oauth_endpoints: dict = {}

# ---------------------------------------------------------------------------
# System prompt — hidden from the end-user
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """\
You are a Tesla vehicle assistant with full control over the user's Tesla
vehicles and energy systems.

Rules:
- Prefer TeslaMate tools (server: teslamate) for read-only queries such as
  battery level, location, or historical stats — they are faster and cheaper.
- Use Tesla Fleet API tools (server: tesla_fleet_api) for commands such as
  lock/unlock, climate control, or charging management.
- Before executing potentially dangerous commands (remote start, unlock, data
  erase), briefly state what you are about to do and then proceed.
- Wake the vehicle automatically when a command requires it.
- Be concise and action-oriented. Users want results, not lengthy explanations.
- Always display units (%, °C/°F, km/mi) next to numeric values.
"""


# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------
def _pkce_pair() -> tuple[str, str]:
    """Return (code_verifier, code_challenge)."""
    verifier = secrets.token_urlsafe(96)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


# ---------------------------------------------------------------------------
# Local OAuth callback server
# ---------------------------------------------------------------------------
class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Captures the OAuth authorization code from the redirect URI."""
    result: dict = {}

    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _OAuthCallbackHandler.result = {
            "code": params.get("code", [None])[0],
            "state": params.get("state", [None])[0],
            "error": params.get("error", [None])[0],
        }
        body = (
            b"<html><body><h2>Authentication successful!</h2>"
            b"<p>You can close this tab and return to the terminal.</p>"
            b"</body></html>"
        )
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):  # silence request logs
        pass


# ---------------------------------------------------------------------------
# OAuth token management
# ---------------------------------------------------------------------------
def _discover_endpoints() -> dict:
    """Fetch OAuth endpoints from the MTM server's well-known metadata."""
    if _oauth_endpoints:
        return _oauth_endpoints
    url = f"{_MCP_BASE_URL}/.well-known/oauth-authorization-server"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    meta = resp.json()
    _oauth_endpoints.update(meta)
    return _oauth_endpoints


def _dcr_register() -> str:
    """Register this skill via DCR (RFC 7591) and return the client_id."""
    meta = _discover_endpoints()
    reg_url = meta.get("registration_endpoint", f"{_MCP_BASE_URL}/register")
    resp = requests.post(reg_url, json={
        "client_name": "tesla-skill",
        "redirect_uris": [_CALLBACK_URL],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
        "scope": _SCOPES,
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()["client_id"]


def _login() -> dict:
    """Register via DCR, then run the PKCE OAuth flow against the MTM server."""
    meta = _discover_endpoints()
    auth_url_base = meta["authorization_endpoint"]
    token_url = meta["token_endpoint"]

    client_id = _dcr_register()
    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(16)

    auth_params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": _CALLBACK_URL,
        "scope": _SCOPES,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    })
    auth_url = f"{auth_url_base}?{auth_params}"

    # Start local callback server in a background thread
    _OAuthCallbackHandler.result = {}
    server = HTTPServer(("localhost", _CALLBACK_PORT), _OAuthCallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("Opening browser for Tesla authentication…", file=sys.stderr)
    if not webbrowser.open(auth_url):
        print(f"Could not open browser. Visit:\n  {auth_url}", file=sys.stderr)

    thread.join(timeout=120)
    server.server_close()

    result = _OAuthCallbackHandler.result
    if result.get("error"):
        raise RuntimeError(f"OAuth error: {result['error']}")
    if not result.get("code"):
        raise RuntimeError("No authorization code received (timed out?)")
    if result.get("state") != state:
        raise RuntimeError("OAuth state mismatch — possible CSRF. Aborting.")

    resp = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": _CALLBACK_URL,
        "code": result["code"],
        "code_verifier": verifier,
    }, timeout=30)
    resp.raise_for_status()

    token = resp.json()
    token["expires_at"] = time.time() + token.get("expires_in", 3600)
    # Persist client_id so refresh works without re-registering
    token["client_id"] = client_id
    return token


def _refresh(token: dict) -> dict:
    """Exchange a refresh token for a new access token."""
    meta = _discover_endpoints()
    token_url = meta["token_endpoint"]
    resp = requests.post(token_url, data={
        "grant_type": "refresh_token",
        "client_id": token["client_id"],
        "refresh_token": token["refresh_token"],
    }, timeout=30)
    resp.raise_for_status()
    new_token = resp.json()
    new_token["expires_at"] = time.time() + new_token.get("expires_in", 3600)
    new_token.setdefault("refresh_token", token["refresh_token"])
    new_token.setdefault("client_id", token["client_id"])
    return new_token


def _load_token() -> dict | None:
    if not _TOKEN_CACHE.exists():
        return None
    try:
        return json.loads(_TOKEN_CACHE.read_text())
    except (json.JSONDecodeError, KeyError):
        return None


def _save_token(token: dict) -> None:
    _TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    _TOKEN_CACHE.write_text(json.dumps(token))
    _TOKEN_CACHE.chmod(0o600)  # owner read/write only


def _get_access_token() -> str:
    """Return a valid access token, logging in or refreshing as needed."""
    # Fast path: static token already in the environment
    if os.environ.get("MTM_TOKEN"):
        return os.environ["MTM_TOKEN"]

    token = _load_token()

    # Still valid with >5 min headroom
    if token and time.time() < token.get("expires_at", 0) - 300:
        return token["access_token"]

    # Try to refresh (requires cached client_id from previous DCR)
    if token and token.get("refresh_token") and token.get("client_id"):
        print("Refreshing Tesla token…", file=sys.stderr)
        try:
            token = _refresh(token)
            _save_token(token)
            return token["access_token"]
        except Exception as exc:
            print(f"Token refresh failed ({exc}), re-authenticating…", file=sys.stderr)

    # Full login (DCR + PKCE)
    token = _login()
    _save_token(token)
    return token["access_token"]


# ---------------------------------------------------------------------------
# MCP server config — hidden from the end-user
# ---------------------------------------------------------------------------
def _mcp_servers(access_token: str) -> list[dict]:
    return [
        {
            "type": "url",
            "url": f"{_MCP_BASE_URL}/mcp?tags=tesla_fleet_api",
            "name": "tesla_fleet_api",
            "authorization_token": access_token,
        },
        {
            "type": "url",
            "url": f"{_MCP_BASE_URL}/mcp?tags=teslamate",
            "name": "teslamate",
            "authorization_token": access_token,
        },
    ]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
def run(query: str, model: str = "claude-opus-4-6") -> str:
    """Send *query* to the Tesla agent and return the text response."""
    access_token = _get_access_token()
    client = anthropic.Anthropic()

    response = client.beta.messages.create(
        model=model,
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": query}],
        mcp_servers=_mcp_servers(access_token),
        betas=["mcp-client-2025-04-04"],
    )

    # MCP tool calls/results are handled server-side by the Anthropic API.
    # We only return the final text answer.
    return "\n".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: tesla_skill.py <query>", file=sys.stderr)
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    try:
        print(run(query))
    except EnvironmentError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)
    except (requests.HTTPError, requests.ConnectionError) as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as exc:
        print(f"Anthropic API error: {exc}", file=sys.stderr)
        sys.exit(1)
