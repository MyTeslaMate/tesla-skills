# tesla-skills

Claude Code skills for the [MyTeslaMate](https://myteslamate.com) ecosystem.

Each skill is a plain Markdown file that provides a system prompt and invokes the MyTeslaMate MCP servers — no Python, no OAuth flow.

## Pattern

```
skill/
└── my_skill.md   ← Claude Code slash command (system prompt only)
```

MCP servers are configured once in `~/.claude/mcp.json` and reused by all skills.

The `.md` file is a [Claude Code custom command](https://docs.anthropic.com/en/docs/claude-code/slash-commands). Drop it into `~/.claude/commands/` and invoke it with `/my_skill <query>`.

## Available skills

### `tesla/` — Tesla vehicle & energy assistant

Connects to the [MyTeslaMate MCP server](https://mcp.myteslamate.com) and answers questions or executes commands across your Tesla vehicles and energy systems.

**Authentication:** a static MTM API token set once as an environment variable. Retrieve your token from your MyTeslaMate account settings.

**Install:**

```bash
# 1. Register the MCP servers globally (once)
cat >> ~/.claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "tesla_fleet_api": {
      "type": "http",
      "url": "https://mcp.myteslamate.com/mcp?tags=tesla_fleet_api",
      "headers": { "Authorization": "Bearer ${MTM_TOKEN}" }
    },
    "teslamate": {
      "type": "http",
      "url": "https://mcp.myteslamate.com/mcp?tags=teslamate",
      "headers": { "Authorization": "Bearer ${MTM_TOKEN}" }
    }
  }
}
EOF

# 2. Copy the skill
cp tesla/tesla_simple.md ~/.claude/commands/tesla.md

# 3. Set your token (add to ~/.zshrc or ~/.profile)
export MTM_TOKEN=<your_myteslamate_token>
```

**Usage:**

```bash
/tesla what is my battery level?
/tesla lock my car
/tesla set the AC to 22°C
/tesla how much did I charge last month?
```

---

## Template

The `template/` directory contains a minimal skeleton for building new skills:

```bash
cp template/skill_template.md myskill/myskill.md
# Edit myskill.md — write your system prompt and reference your MCP servers
```

## How it works

Claude Code loads the MCP servers from `~/.claude/mcp.json` at startup and makes their tools available to all sessions. The skill `.md` file simply provides a system prompt and forwards the user's query — Claude handles the rest.

```
User query  →  /tesla <query>
               └── tesla.md  (system prompt)
                     └── Claude Code  ←→  mcp.myteslamate.com  (MTM_TOKEN)
                           └── text response
```
