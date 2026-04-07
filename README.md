# Tesla Skill for Claude

A Claude custom skill for Tesla owners using [MyTeslaMate](https://myteslamate.com).

Query your vehicles, control climate and charging, and analyze your driving and energy history — all through natural language.

## Requirements

- Claude.ai Pro / Max / Team / Enterprise with Skills enabled
- [MyTeslaMate](https://myteslamate.com) account with MCP server access
- MyTeslaMate MCP connected in your Claude.ai settings

## Installation — 3 steps, 2 minutes

### 1. Connect the MyTeslaMate MCP server in Claude.ai

Go to **Claude.ai → Settings → Integrations → Add integration** and enter:

```text
https://mcp.myteslamate.com/mcp
```

Authenticate with your MyTeslaMate account when prompted.

### 2. Install the skill

Download `tesla-skill.zip` from the [latest release](../../releases/latest), then go to
**Claude.ai → Settings → Features → Custom Skills → Upload Skill** and upload the zip file.

### 3. Done

Claude will automatically use the skill when you ask about your Tesla.

## Usage examples

```text
What's my battery level?
Lock my car
Set the AC to 22°C
How much did I charge last month?
Is my car plugged in?
Open the charge port
What's my Powerwall charge level?
Show me my energy consumption this week
```

## Claude Code (CLI) users

If you use Claude Code instead of claude.ai, add the MCP server and copy the skill:

```bash
# Add the MCP server (OAuth — a browser window will open to authenticate)
claude mcp add myteslamate --transport http "https://mcp.myteslamate.com/mcp"

# Copy the skill as a slash command
cp tesla-skill/SKILL.md ~/.claude/commands/tesla.md
```

Then use `/tesla what is my battery level?`

## How it works

The skill instructs Claude how to route requests within the MyTeslaMate MCP server:

- **`teslamate_*` tools** — fast read-only queries (no vehicle wake needed)
- **Fleet API tools** — commands and real-time vehicle control

```text
You → Claude + tesla-skill → MyTeslaMate MCP (OAuth)
                                  ↕
                         MyTeslaMate / TeslaMate
                                  ↕
                           Your Tesla vehicles
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
