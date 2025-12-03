# Installation Guide

## Prerequisites

- Ableton Live 9.0 or higher
- Python 3.7 or higher
- Internet connection
- OpenWeatherMap API key (free)

## Step-by-Step Installation

### 1. Install Python (if not already installed)

**macOS:**
```bash
# Check if Python 3 is installed
python3 --version

# If not installed, install via Homebrew
brew install python3
```

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer, check "Add Python to PATH"
3. Verify: Open Command Prompt, type `python --version`

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Install Python Dependencies

Navigate to the weather pack folder and run:

```bash
pip3 install -r requirements.txt
```

Or install manually:
```bash
pip3 install requests python-osc
```

### 3. Get OpenWeatherMap API Key

1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Click "Sign Up" (or "Sign In" if you have an account)
3. After signing in, go to API Keys section
4. Copy your API key (or generate a new one)
5. **Note:** New API keys can take 10 minutes to activate

### 4. Create Configuration File

```bash
python3 weather_to_osc.py --create-config my_weather_config.json
```

Edit `my_weather_config.json`:
- Replace `YOUR_OPENWEATHERMAP_API_KEY_HERE` with your actual API key
- Change `"location"` to your city

Save the file.

### 5. Install Max for Live Devices

**Option A: Direct Installation**
1. Copy all `.amxd` files to:
   - **Mac:** `~/Music/Ableton/User Library/Presets/MIDI Effects/Max MIDI Effect/`
   - **Windows:** `Documents\Ableton\User Library\Presets\MIDI Effects\Max MIDI Effect\`

2. Or create a subfolder: `...Max MIDI Effect/Weather Pack/`

**Option B: Drag and Drop**
1. Open Ableton Live
2. Drag `.amxd` files directly onto tracks
3. Save as default preset if desired

### 6. Set Up Ableton Live Session

1. Create 5 MIDI or Audio tracks
2. Add the TouchOSC receiver devices:
   - Track 1: Temperature (port 7400)
   - Track 2: Wind (port 7401)
   - Track 3: Rain (port 7402)
   - Track 4: Pressure (port 7403)
   - Track 5: Humidity (port 7404)

3. Optionally add the main WEATHER.amxd device for visual monitoring

### 7. Test the System

**Terminal 1 - Start the Python bridge:**
```bash
python3 weather_to_osc.py --config my_weather_config.json
```

You should see:
```
2024-12-02 14:30:00 - INFO - Initialized OSC clients on 127.0.0.1:7400-7404
2024-12-02 14:30:00 - INFO - Polling New York every 1800s using imperial units
2024-12-02 14:30:01 - INFO - Sent - Temp: 58.3F (0.58), Wind: 8.2mph (0.33), ...
```

**Ableton Live:**
- Check the number boxes in TouchOSC devices update with values
- Values should be between 0.0 and 1.0

### 8. Map to Parameters

In any TouchOSC device:
1. Click the "Learn" button
2. Click "Map" 
3. Adjust any parameter on any device in Live
4. The weather data is now controlling that parameter

## Verification Checklist

- [ ] Python 3 installed (`python3 --version`)
- [ ] Dependencies installed (`pip3 list | grep -E "requests|python-osc"`)
- [ ] API key obtained from OpenWeatherMap
- [ ] Config file created and edited with API key
- [ ] Max devices loaded in Ableton Live
- [ ] Python script running without errors
- [ ] Values updating in Live (0.0-1.0 range)
- [ ] Successfully mapped weather parameter to a Live parameter

## Common Installation Issues

### "pip3: command not found"
- Python pip not installed
- **Fix:** `python3 -m ensurepip --upgrade`

### "Permission denied" when installing packages
- Need administrator privileges
- **Fix:** `pip3 install --user -r requirements.txt`

### Max devices won't load in Live
- Max for Live not installed (comes with Live Suite, or separate purchase)
- **Fix:** Install Max for Live from Ableton

### OSC not receiving in Live
- Firewall blocking local traffic
- **Fix (Mac):** System Preferences → Security → Firewall → Allow Ableton
- **Fix (Windows):** Windows Defender → Allow Ableton through firewall

### Python script crashes immediately
- Check API key is correct
- Check location spelling
- **Fix:** Run with `--verbose` flag to see detailed errors

## Uninstallation

To remove:
1. Delete `.amxd` files from Ableton User Library
2. Uninstall Python packages: `pip3 uninstall requests python-osc`
3. Delete weather pack folder

## Upgrading

When new version is released:
1. Stop the Python script (Ctrl+C)
2. Replace `weather_to_osc.py` with new version
3. Update dependencies: `pip3 install -r requirements.txt --upgrade`
4. Replace `.amxd` files in Ableton
5. Check README for any config changes
6. Restart the system

## Getting Help

If stuck:
1. Run with verbose logging: `python3 weather_to_osc.py --config my_config.json --verbose`
2. Check troubleshooting section in README.md
3. Verify all checklist items above
4. Check OpenWeatherMap API status: [status.openweathermap.org](https://status.openweathermap.org)
