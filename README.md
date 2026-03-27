# tesla-skills

Claude Code skills for the [MyTeslaMate](https://myteslamate.com) ecosystem, powered by the [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python).

Each skill is a self-contained Python script that embeds its own **system prompt** and **MCP server configuration**, so the caller only needs to provide a natural-language query.

## Pattern

```
skill/
├── my_skill.py   ← Anthropic SDK agent (system prompt + MCP config hidden inside)
└── my_skill.md   ← Claude Code slash command that invokes the script
```

The `.md` file is a [Claude Code custom command](https://docs.anthropic.com/en/docs/claude-code/slash-commands). Drop it into `.claude/commands/` in your project (or `~/.claude/commands/` globally) and invoke it with `/my_skill <query>`.

## Available skills

### `tesla/` — Tesla vehicle & energy assistant

Connects to the [MyTeslaMate MCP server](https://mcp.myteslamate.com) and answers questions or executes commands across your Tesla vehicles and energy systems.

**Authentication:** OAuth 2.0 PKCE — on first run a browser window opens for Tesla login. The token is cached at `~/.config/tesla-skill/token.json` (mode 600) and refreshed automatically.

**Required env vars:**

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `MTM_CLIENT_ID` | MyTeslaMate OAuth client ID |

**Install:**

```bash
pip install anthropic requests

# Copy the command file into your project or home directory
cp tesla/tesla.md ~/.claude/commands/tesla.md
```

**Usage:**

```bash
# Direct CLI
python tesla/tesla_skill.py "what is my battery level?"

# Claude Code slash command (after installing tesla.md)
/tesla lock my car
/tesla set the AC to 22°C
/tesla how much did I charge last month?
```

---

## Template

The `template/` directory contains a minimal skeleton for building new skills:

```bash
cp template/skill_template.py myskill/myskill.py
cp template/skill_template.md myskill/myskill.md
# Edit myskill.py — set _SYSTEM_PROMPT and _mcp_servers()
```

## How it works

Skills use the Anthropic API's [remote MCP beta](https://docs.anthropic.com/en/docs/agents-and-tools/mcp) (`mcp-client-2025-04-04`). MCP tool calls are executed **server-side** by Anthropic — the script never sees raw tool payloads, keeping the implementation simple.

```
User query
  → tesla_skill.py
    → OAuth (browser, first run only)
    → anthropic.beta.messages.create(mcp_servers=[...])
      → Anthropic API ←→ mcp.myteslamate.com  (server-side)
    → text response
  → printed to stdout
```
