# Vehicle Commands Reference

Use the `tesla_fleet_api` MCP server for all commands below. Wake the vehicle first if needed.

## Door & security

| Command | Tool | Notes |
|---------|------|-------|
| Lock doors | `door_lock` | — |
| Unlock doors | `door_unlock` | Confirm before executing |
| Open frunk | `actuate_trunk` `front` | Irreversible while driving |
| Open trunk | `actuate_trunk` `rear` | — |
| Enable Sentry mode | `set_sentry_mode` `true` | — |
| Disable Sentry mode | `set_sentry_mode` `false` | — |
| Enable valet mode | `set_valet_mode` `true` | Requires PIN |
| Remote start | `remote_start_drive` | Ask for confirmation — security risk |

## Climate

| Command | Tool | Notes |
|---------|------|-------|
| Start climate | `auto_conditioning_start` | — |
| Stop climate | `auto_conditioning_stop` | — |
| Set temperature | `set_temps` | Provide driver + passenger temp in °C |
| Set seat heater | `remote_seat_heater_request` | Level 0–3 |
| Set steering wheel heater | `remote_steering_wheel_heater_request` | on/off |
| Start defrost | `set_preconditioning_max` `true` | — |
| Stop defrost | `set_preconditioning_max` `false` | — |

## Charging

| Command | Tool | Notes |
|---------|------|-------|
| Open charge port | `charge_port_door_open` | — |
| Close charge port | `charge_port_door_close` | — |
| Start charging | `charge_start` | Vehicle must be plugged in |
| Stop charging | `charge_stop` | — |
| Set charge limit | `set_charge_limit` | Value in % (e.g. 80) |
| Set charging amps | `set_charging_amps` | Value in amps |
| Schedule charge | `set_scheduled_charging` | Provide time in minutes since midnight |

## Windows & sunroof

| Command | Tool | Notes |
|---------|------|-------|
| Vent windows | `window_control` `vent` | — |
| Close windows | `window_control` `close` | — |

## Wake

| Command | Tool | Notes |
|---------|------|-------|
| Wake vehicle | `wake_up` | Required before commands if vehicle is asleep |

## Homelink

| Command | Tool | Notes |
|---------|------|-------|
| Trigger Homelink | `trigger_homelink` | Vehicle must be in range of the garage |
