# Energy Systems Reference

Use the `tesla_fleet_api` MCP server for Powerwall and solar queries and commands.

## Powerwall queries

| Query | Tool | Returns |
|-------|------|---------|
| Battery charge level | `get_energy_site_live_status` | `percentage_charged` |
| Grid status | `get_energy_site_live_status` | `grid_status` (Active / Inactive) |
| Power flow (solar / battery / grid / home) | `get_energy_site_live_status` | `solar_power`, `battery_power`, `grid_power`, `load_power` in watts |
| Battery reserve setting | `get_energy_site_info` | `backup_reserve_percent` |
| Operating mode | `get_energy_site_info` | `default_real_mode` (self_consumption / backup / autonomous) |

## Powerwall commands

| Command | Tool | Notes |
|---------|------|-------|
| Set backup reserve | `set_backup_reserve_percent` | Value in % (0–100) |
| Set operating mode | `set_operating_mode` | `self_consumption`, `backup`, or `autonomous` |
| Go off-grid | `set_grid_import_export` | Use with caution |

## Solar queries

Solar power is returned as part of `get_energy_site_live_status` → `solar_power` (watts).

For historical solar production, use `get_energy_site_calendar_history`:
- `kind`: `power` (5-min intervals) or `energy` (daily/monthly totals)
- `period`: `day`, `month`, `year`, `lifetime`

## Typical patterns

**"What's my Powerwall level?"**
→ `get_energy_site_live_status` → return `percentage_charged`

**"How much solar did I produce today?"**
→ `get_energy_site_calendar_history` with `kind=energy`, `period=day`

**"Am I importing from the grid?"**
→ `get_energy_site_live_status` → check `grid_power` (positive = importing, negative = exporting)

**"Set my backup reserve to 20%"**
→ `set_backup_reserve_percent` with value `20`
