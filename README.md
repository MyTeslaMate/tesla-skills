# Tesla Skill for Claude

A Claude custom skill for Tesla owners using [MyTeslaMate](https://myteslamate.com).

Query your vehicles, control climate and charging, and analyze your driving and energy history — all through natural language.

## Requirements

- Claude.ai Pro / Max / Team / Enterprise with Skills enabled
- [MyTeslaMate](https://myteslamate.com) account with MCP server access
- MyTeslaMate MCP connected in your Claude.ai settings

## Installation — 3 steps, 2 minutes

**1. Connect the MyTeslaMate MCP server in Claude.ai**

Go to **Claude.ai → Settings → Integrations → Add integration** and enter:

```
https://mcp.myteslamate.com/mcp
```

Authenticate with your MyTeslaMate account when prompted.

**2. Install the skill**

Download `tesla-skill.zip` from the [latest release](../../releases/latest), then go to:

**Claude.ai → Settings → Features → Custom Skills → Upload Skill**

Upload the zip file.

**3. Done**

Claude will automatically use the skill when you ask about your Tesla.

## Usage examples

```
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

If you use Claude Code instead of claude.ai, configure the MCP servers directly:

```bash
# Add MCP servers to your global config
claude mcp add tesla_fleet_api --transport http \
  "https://mcp.myteslamate.com/mcp?tags=tesla_fleet_api" \
  --header "Authorization: Bearer ${MTM_TOKEN}"

claude mcp add teslamate --transport http \
  "https://mcp.myteslamate.com/mcp?tags=teslamate" \
  --header "Authorization: Bearer ${MTM_TOKEN}"

# Copy the skill as a slash command
cp tesla-skill/SKILL.md ~/.claude/commands/tesla.md

# Set your token
export MTM_TOKEN=<your_myteslamate_token>
```

Then use `/tesla what is my battery level?`

## How it works

The skill instructs Claude to route requests between two MCP servers:

- **`teslamate`** — fast read-only queries (no vehicle wake needed)
- **`tesla_fleet_api`** — commands and real-time vehicle control

```
You → Claude + tesla-skill → teslamate MCP      (reads)
                           → tesla_fleet_api MCP (commands)
                                  ↕
                         MyTeslaMate / TeslaMate
                                  ↕
                           Your Tesla vehicles
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
