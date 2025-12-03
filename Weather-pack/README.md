# Weather-Controlled Music System for Ableton Live

Control your music with real-time weather data. This Max for Live pack converts weather conditions into musical parameters via OSC.

## What This Does

Fetches live weather data (temperature, wind speed, rainfall, barometric pressure, humidity) and sends it to Ableton Live as automation-ready control signals. Map weather parameters to any instrument, effect, or device parameter for dynamic, location-responsive music.

## Quick Start

### 1. Get Your API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key (free tier: 1000 calls/day, more than enough)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests python-osc
```

### 3. Configure

Create a config file:
```bash
python weather_to_osc.py --create-config my_weather_config.json
```

Edit `my_weather_config.json` with your API key and location:
```json
{
  "api_key": "your_actual_api_key_here",
  "location": "San Francisco",
  "host": "127.0.0.1",
  "base_port": 7400,
  "poll_interval": 1800,
  "units": "imperial",
  "ranges": {
    "temp": {"min": 0, "max": 100, "unit": "F"},
    "wind": {"min": 0, "max": 25, "unit": "mph"},
    "rain": {"min": 0, "max": 5, "unit": "mm"},
    "pressure": {"min": 980, "max": 1040, "unit": "hPa"},
    "humidity": {"min": 0, "max": 100, "unit": "%"}
  }
}
```

### 4. Load Max for Live Devices

1. Open Ableton Live
2. Drag `WEATHER.amxd` onto a MIDI or Audio track
3. Drag the 5 TouchOSC receiver devices onto separate tracks:
   - Port 7400: Temperature
   - Port 7401: Wind Speed
   - Port 7402: Rainfall
   - Port 7403: Barometric Pressure
   - Port 7404: Humidity

### 5. Start the Bridge

```bash
python weather_to_osc.py --config my_weather_config.json
```

You should see:
```
2024-12-02 14:30:00 - INFO - Initialized OSC clients on 127.0.0.1:7400-7404
2024-12-02 14:30:00 - INFO - Polling San Francisco every 1800s using imperial units
2024-12-02 14:30:00 - INFO - Weather OSC Bridge started - press Ctrl+C to stop
2024-12-02 14:30:01 - INFO - Sent - Temp: 58.3F (0.58), Wind: 8.2mph (0.33), ...
```

### 6. Map Parameters

In Live's TouchOSC devices, click "Learn" on any parameter, then click "Map" to assign weather data to any instrument or effect parameter.

## Configuration Options

### Location Format

- City name: `"Seattle"`
- City, State: `"Austin, TX"`
- City, Country: `"Tokyo, JP"`
- Coordinates work too: Search your city on OpenWeatherMap to find exact coordinates

### Units

- `"imperial"`: Fahrenheit, mph
- `"metric"`: Celsius, m/s

### Poll Interval

Default: 1800 seconds (30 minutes)

Weather doesn't change rapidly enough to justify frequent polling. 30-60 minutes is optimal. Don't go below 600 seconds (10 min) or you'll waste API calls.

### Custom Ranges

Adjust `ranges` in config to match your climate:

```json
"ranges": {
  "temp": {"min": 20, "max": 90, "unit": "F"},  // Desert climate
  "wind": {"min": 0, "max": 40, "unit": "mph"}  // Windy location
}
```

Values outside min/max are clamped to 0.0-1.0 range.

## Command Line Usage

Without config file:
```bash
python weather_to_osc.py --api-key YOUR_KEY --location "Portland, OR"
```

Override config settings:
```bash
python weather_to_osc.py --config my_config.json --interval 3600 --verbose
```

## Musical Mapping Examples

### Ambient/Generative
- **Temperature** → Filter cutoff (warmer = brighter)
- **Humidity** → Reverb mix (humid = wetter sound)
- **Pressure** → Tempo/clock rate (high pressure = faster)
- **Wind** → Modulation depth/LFO rate
- **Rain** → Delay feedback/density

### Rhythmic
- **Temperature** → Hi-hat velocity
- **Wind** → Percussion randomization
- **Rain** → Trigger probability for fills
- **Pressure** → Kick drum tuning
- **Humidity** → Swing amount

### Synthesis
- **Temperature** → Oscillator tuning
- **Wind** → FM depth
- **Rain** → Noise level
- **Pressure** → Envelope attack/decay
- **Humidity** → Resonance

## Troubleshooting

### "Invalid API key"
- Check your API key is correct in config
- Verify your OpenWeatherMap account is activated (check email)
- New keys can take 10 minutes to activate

### "Location not found"
- Try "City, Country Code" format: "Berlin, DE"
- Search your city on openweathermap.org to verify spelling

### No data in Live
- Confirm Python script is running (check terminal output)
- Verify TouchOSC devices are on separate tracks with correct ports (7400-7404)
- Check firewall isn't blocking local OSC traffic
- Try `--verbose` flag to see detailed logs

### Values stuck at 0.0 or 1.0
- Weather is outside your configured min/max ranges
- Adjust ranges in config to match your climate
- Check actual values in terminal output (raw values shown in parentheses)

### "Request timeout" / Network errors
- Check internet connection
- OpenWeatherMap might be having issues (check status.openweathermap.org)
- Script will retry automatically

## Rate Limits

Free OpenWeatherMap tier: 1,000 calls/day

At 30-minute intervals: 48 calls/day (well under limit)

If you need faster updates or multiple locations, upgrade to paid tier.

## Advanced: Multiple Locations

Run multiple instances with different configs:

```bash
# Terminal 1 - Berlin weather on ports 7400-7404
python weather_to_osc.py --config berlin_config.json

# Terminal 2 - Tokyo weather on ports 7500-7504
python weather_to_osc.py --config tokyo_config.json
```

Edit `tokyo_config.json`:
```json
{
  "api_key": "...",
  "location": "Tokyo, JP",
  "base_port": 7500
}
```

## Architecture

```
OpenWeatherMap API
       ↓
Python Script (weather_to_osc.py)
       ↓
OSC Messages (127.0.0.1:7400-7404)
       ↓
TouchOSC Receivers (5 separate M4L devices)
       ↓
Ableton Live Parameters (automation-ready)
```

Each weather parameter gets its own port and device for independent mapping.

## File Structure

```
weather-pack/
├── weather_to_osc.py         # Python bridge script
├── requirements.txt           # Python dependencies
├── WEATHER.amxd              # Main weather display device
├── TouchOSC_7400.amxd        # Temperature receiver
├── TouchOSC_7401.amxd        # Wind receiver
├── TouchOSC_7402.amxd        # Rain receiver
├── TouchOSC_7403.amxd        # Pressure receiver
├── TouchOSC_7404.amxd        # Humidity receiver
├── README.md                  # This file
└── example_config.json        # Example configuration
```

## License

MIT License - use freely, commercially or otherwise

## Credits

Built with:
- [OpenWeatherMap API](https://openweathermap.org/api)
- [python-osc](https://pypi.org/project/python-osc/)
- Ableton Live & Max for Live

## Support

Issues, questions, improvements: [Your contact/repo info here]

## Version

1.0.0 - Initial release
