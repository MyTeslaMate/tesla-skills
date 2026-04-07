# TeslaMate Queries Reference

Use the `teslamate` MCP server for all read-only and historical queries. These are fast and do not wake the vehicle.

## Current state

| Query | What to ask for | Notes |
|-------|-----------------|-------|
| Battery level | `battery_level`, `usable_battery_level` | In % |
| Estimated range | `est_battery_range`, `rated_battery_range` | In km or mi |
| Charge state | `charging_state` | Charging / Stopped / Disconnected / Complete |
| Plugged in | `plugged_in` | true/false |
| Charge limit | `charge_limit_soc` | In % |
| Location | `latitude`, `longitude`, `geofence` | Named location if in a geofence |
| Odometer | `odometer` | Total distance |
| Speed | `speed` | Current speed (0 if parked) |
| State | `state` | online / asleep / charging / driving |
| Doors | `doors_open`, `trunk_open`, `frunk_open` | true/false |
| Windows | `windows_open` | true/false |
| Software version | `version` | e.g. 2024.38.1 |
| Outside temperature | `outside_temp` | In °C |
| Inside temperature | `inside_temp` | In °C |
| Tire pressure | `tpms_*` | Front/rear left/right in bar |

## Charging history

Query charging sessions with filters:

- Date range: `start_date` / `end_date`
- Returns per session: start/end time, duration, energy added (kWh), cost, location, charge added (%)

**"How much did I charge last month?"**
→ filter sessions by last month → sum `charge_energy_added`

**"What was my average charge duration?"**
→ filter sessions → average `duration_min`

**"Where do I charge most often?"**
→ group sessions by `address` or `geofence` → count

## Driving history

Query drives with filters:

- Returns per drive: start/end time, distance, duration, start/end location, energy consumed, efficiency

**"How far did I drive this week?"**
→ filter drives by this week → sum `distance`

**"What's my average efficiency?"**
→ filter drives → average `efficiency` (Wh/km or Wh/mi)

**"Show me my trips this month"**
→ filter drives by this month → list with distance and locations

## Statistics

**"What's my total distance driven?"**
→ query lifetime odometer or sum all drives

**"How much have I charged in total?"**
→ sum `charge_energy_added` across all charging sessions

**"What's my longest trip?"**
→ query drives sorted by distance descending, limit 1
