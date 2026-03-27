#!/usr/bin/env python3
"""
<Your Skill Name> — Anthropic SDK skill

Replace this docstring with your skill's description.

Usage:
    python template/skill_template.py "your query here"

Required env vars:
    ANTHROPIC_API_KEY     — Anthropic API key

Optional env vars:
    SKILL_MODEL           — Claude model to use (default: claude-opus-4-6)
"""

import os
import sys
import anthropic

# ---------------------------------------------------------------------------
# System prompt — customize this for your domain
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """\
You are a helpful assistant specialized in <your domain>.

Rules:
- <rule 1>
- <rule 2>
- Be concise and action-oriented.
"""

# ---------------------------------------------------------------------------
# MCP server config — add your MCP servers here
# ---------------------------------------------------------------------------
def _mcp_servers() -> list[dict]:
    """Return MCP server definitions. Use authorization_token for Bearer auth."""
    return [
        # Example: a remote HTTP MCP server with Bearer token auth
        # {
        #     "type": "url",
        #     "url": "https://your-mcp-server.example.com/mcp",
        #     "name": "my_server",
        #     "authorization_token": os.environ["MY_SERVER_TOKEN"],
        # },
    ]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
def run(query: str) -> str:
    """Send *query* to the agent and return the text response."""
    model = os.environ.get("SKILL_MODEL", "claude-opus-4-6")
    client = anthropic.Anthropic()

    kwargs: dict = {
        "model": model,
        "max_tokens": 4096,
        "system": _SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": query}],
    }

    servers = _mcp_servers()
    if servers:
        # Remote MCP servers are executed server-side by the Anthropic API.
        # No client-side tool loop needed.
        kwargs["mcp_servers"] = servers
        kwargs["betas"] = ["mcp-client-2025-04-04"]

    response = client.beta.messages.create(**kwargs) if servers else client.messages.create(**kwargs)

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
        print("Usage: skill_template.py <query>", file=sys.stderr)
        sys.exit(1)

    try:
        print(run(" ".join(sys.argv[1:])))
    except anthropic.APIError as exc:
        print(f"Anthropic API error: {exc}", file=sys.stderr)
        sys.exit(1)
