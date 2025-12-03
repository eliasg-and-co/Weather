# Quick Reference Card

## Setup (One Time)

```bash
# 1. Get API key from openweathermap.org
# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Create config
python3 weather_to_osc.py --create-config config.json

# 4. Edit config.json with your API key and location
```

## Running

```bash
python3 weather_to_osc.py --config config.json
```

## OSC Ports

| Port | Parameter | Default Range | Unit |
|------|-----------|---------------|------|
| 7400 | Temperature | 0-100 | °F |
| 7401 | Wind Speed | 0-25 | mph |
| 7402 | Rainfall | 0-5 | mm/hr |
| 7403 | Pressure | 980-1040 | hPa |
| 7404 | Humidity | 0-100 | % |

## Output Values

All parameters normalized to **0.0 - 1.0** range

- 0.0 = minimum value in configured range
- 1.0 = maximum value in configured range
- Values outside range are clamped

## Command Line Options

```bash
# Use config file
--config path/to/config.json

# Direct arguments (no config needed)
--api-key YOUR_KEY --location "City Name"

# Override config settings
--interval 3600        # Poll every hour
--units metric         # Use Celsius, m/s
--verbose              # Show debug info

# Create example config
--create-config myconfig.json
```

## Common Locations

```json
"location": "New York"           // City name
"location": "Austin, TX"         // City, State
"location": "Tokyo, JP"          // City, Country
```

## Polling Intervals

| Interval | Use Case |
|----------|----------|
| 600s (10 min) | Development/testing |
| 1800s (30 min) | **Default - recommended** |
| 3600s (1 hour) | Slow-changing ambient |

## Ableton Live Setup

1. Create 5 tracks
2. Add TouchOSC receiver to each track (ports 7400-7404)
3. Click "Learn" → "Map" to assign weather to parameters
4. Start Python script

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Invalid API key" | Check key in config, wait 10 min for activation |
| "Location not found" | Use "City, Country" format |
| No values in Live | Check Python script is running, verify ports |
| All 0.0 or 1.0 | Adjust ranges in config for your climate |
| Network timeout | Check internet, script will auto-retry |

## File Structure

```
weather-pack/
├── weather_to_osc.py      # Run this
├── config.json            # Your settings
├── requirements.txt       # Dependencies
├── WEATHER.amxd          # Optional monitor device
└── TouchOSC_*.amxd       # 5 receiver devices (7400-7404)
```

## Mapping Ideas

**Filter Cutoff** ← Temperature (warmer = brighter)  
**Reverb Mix** ← Humidity (humid = wetter)  
**LFO Rate** ← Wind (gusty = faster modulation)  
**Delay Feedback** ← Rain (rainy = more repeats)  
**Tempo** ← Pressure (high = faster)

## API Limits

Free tier: **1,000 calls/day**

At 30-min intervals: **48 calls/day** ✓

## Stop Script

Press `Ctrl+C` in terminal

## Version

1.0.0
