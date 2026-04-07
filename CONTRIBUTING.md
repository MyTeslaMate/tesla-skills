# Contributing

Contributions are welcome — bug fixes, improved prompts, new reference docs, and better examples.

## Getting started

1. Fork the repository
2. Create a branch: `git checkout -b feat/your-change`
3. Make your changes
4. Open a pull request

## SKILL.md guidelines

- Keep it under 500 lines. Move detail to `references/` files.
- Frontmatter must contain exactly two fields: `name` and `description`.
- `name`: alphanumeric and hyphens only (e.g. `tesla-skill`)
- `description`: under 1024 characters, one sentence summary of what the skill does
- Use the `## References` section to list files in `references/` that should be loaded contextually.

```yaml
---
name: tesla-skill
description: One-sentence description of what the skill does.
---
```

## Commit format

Use [conventional commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | New capability or command pattern |
| `fix:` | Corrects wrong behavior or routing |
| `docs:` | README, CONTRIBUTING, references |
| `refactor:` | Restructures without changing behavior |
| `chore:` | CI, workflows, config |

Examples:

```
feat: add Powerwall energy query patterns
fix: correct vehicle wake routing for climate commands
docs: add seat heater reference examples
```

## References directory

Files in `references/` are included in the skill zip and can be loaded by Claude when relevant. Keep each file focused on a single topic area. Name them clearly:

- `references/vehicle-commands.md` — lock, climate, charging commands
- `references/energy-systems.md` — Powerwall, solar
- `references/teslamate-queries.md` — historical data queries

## Testing your changes

Before opening a PR, verify:

- [ ] `SKILL.md` frontmatter is valid (run `validate.yml` locally or push to a branch)
- [ ] SKILL.md is under 500 lines
- [ ] The skill produces correct responses for at least one read query and one command
- [ ] No broken links in Markdown files

## Releases

Releases are automated. Every push to `main`/`master` creates a new GitHub Release with an updated `tesla-skill.zip`. You do not need to manage versions manually.
