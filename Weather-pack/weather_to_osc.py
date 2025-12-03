#!/usr/bin/env python3
"""
Weather to OSC Bridge for Max for Live
Fetches weather data and sends to multiple OSC ports for musical control
"""

import requests
import time
import argparse
import logging
import sys
from pythonosc import udp_client
from pathlib import Path
import json

# Constants
DEFAULT_POLL_INTERVAL = 1800  # 30 minutes in seconds
API_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 5

# Default normalization ranges - can be overridden via config
DEFAULT_RANGES = {
    'temp': {'min': 0, 'max': 100, 'unit': 'F'},      # Fahrenheit
    'wind': {'min': 0, 'max': 25, 'unit': 'mph'},     # Miles per hour
    'rain': {'min': 0, 'max': 5, 'unit': 'mm'},       # Millimeters per hour
    'pressure': {'min': 980, 'max': 1040, 'unit': 'hPa'},  # Hectopascals
    'humidity': {'min': 0, 'max': 100, 'unit': '%'}   # Percentage
}

class WeatherOSCBridge:
    def __init__(self, api_key, location, host='127.0.0.1', base_port=7400, 
                 poll_interval=DEFAULT_POLL_INTERVAL, ranges=None, units='imperial'):
        self.api_key = api_key
        self.location = location
        self.host = host
        self.base_port = base_port
        self.poll_interval = poll_interval
        self.units = units
        self.ranges = ranges or DEFAULT_RANGES.copy()
        
        # Create OSC clients for each parameter
        self.clients = {
            'temp': udp_client.SimpleUDPClient(host, base_port),
            'wind': udp_client.SimpleUDPClient(host, base_port + 1),
            'rain': udp_client.SimpleUDPClient(host, base_port + 2),
            'pressure': udp_client.SimpleUDPClient(host, base_port + 3),
            'humidity': udp_client.SimpleUDPClient(host, base_port + 4),
            'monitor': udp_client.SimpleUDPClient(host, base_port + 5)  # For WEATHER display device
        }
        
        logging.info(f"Initialized OSC clients on {host}:{base_port}-{base_port + 5}")
        logging.info(f"Ports: 7400-7404 (individual params), 7405 (monitor display)")
        logging.info(f"Polling {location} every {poll_interval}s using {units} units")
    
    def normalize_value(self, value, param):
        """Normalize weather value to 0-1 range based on configured min/max"""
        config = self.ranges[param]
        normalized = (value - config['min']) / (config['max'] - config['min'])
        return max(0.0, min(1.0, normalized))  # Clamp to 0-1
    
    def fetch_weather(self):
        """Fetch weather data from OpenWeatherMap API with retry logic"""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': self.location,
            'appid': self.api_key,
            'units': self.units
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=API_TIMEOUT)
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.Timeout:
                logging.error(f"Request timeout (attempt {attempt + 1}/{MAX_RETRIES})")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    logging.error("Invalid API key - check your configuration")
                    sys.exit(1)
                elif e.response.status_code == 404:
                    logging.error(f"Location '{self.location}' not found")
                    sys.exit(1)
                else:
                    logging.error(f"HTTP error: {e.response.status_code}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Network error: {str(e)}")
            
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
        
        return None
    
    def parse_and_send(self, data):
        """Parse weather data and send normalized values via OSC"""
        try:
            # Extract raw values
            temp = data['main']['temp']
            wind = data['wind']['speed']
            rain = data.get('rain', {}).get('1h', 0)  # Rain in last hour, default 0
            pressure = data['main']['pressure']
            humidity = data['main']['humidity']
            
            # Normalize
            values = {
                'temp': self.normalize_value(temp, 'temp'),
                'wind': self.normalize_value(wind, 'wind'),
                'rain': self.normalize_value(rain, 'rain'),
                'pressure': self.normalize_value(pressure, 'pressure'),
                'humidity': self.normalize_value(humidity, 'humidity')
            }
            
            # Send OSC messages to individual ports (7400-7404 for TouchOSC devices)
            self.clients['temp'].send_message("/weather/temp", values['temp'])
            self.clients['wind'].send_message("/weather/wind", values['wind'])
            self.clients['rain'].send_message("/weather/rain", values['rain'])
            self.clients['pressure'].send_message("/weather/pressure", values['pressure'])
            self.clients['humidity'].send_message("/weather/humidity", values['humidity'])
            
            # Also send all messages to monitor port (7405 for WEATHER display device)
            self.clients['monitor'].send_message("/weather/temp", values['temp'])
            self.clients['monitor'].send_message("/weather/wind", values['wind'])
            self.clients['monitor'].send_message("/weather/rain", values['rain'])
            self.clients['monitor'].send_message("/weather/pressure", values['pressure'])
            self.clients['monitor'].send_message("/weather/humidity", values['humidity'])
            
            # Log with both raw and normalized values
            logging.info(
                f"Sent - Temp: {temp:.1f}{self.ranges['temp']['unit']} ({values['temp']:.2f}), "
                f"Wind: {wind:.1f}{self.ranges['wind']['unit']} ({values['wind']:.2f}), "
                f"Rain: {rain:.1f}{self.ranges['rain']['unit']} ({values['rain']:.2f}), "
                f"Pressure: {pressure:.0f}{self.ranges['pressure']['unit']} ({values['pressure']:.2f}), "
                f"Humidity: {humidity:.0f}{self.ranges['humidity']['unit']} ({values['humidity']:.2f})"
            )
            
            return True
            
        except KeyError as e:
            logging.error(f"Missing expected data field: {e}")
            return False
        except Exception as e:
            logging.error(f"Error processing weather data: {str(e)}")
            return False
    
    def run(self):
        """Main loop - fetch and send weather data"""
        logging.info("Weather OSC Bridge started - press Ctrl+C to stop")
        
        while True:
            data = self.fetch_weather()
            
            if data:
                self.parse_and_send(data)
            else:
                logging.warning("Failed to fetch weather data after retries")
            
            time.sleep(self.poll_interval)

def load_config(config_path):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config file: {e}")
        sys.exit(1)

def create_example_config(path):
    """Create example configuration file"""
    config = {
        "api_key": "YOUR_OPENWEATHERMAP_API_KEY_HERE",
        "location": "New York",
        "host": "127.0.0.1",
        "base_port": 7400,
        "poll_interval": 1800,
        "units": "imperial",
        "ranges": DEFAULT_RANGES
    }
    
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created example config at: {path}")
    print("Edit this file with your API key and location, then run:")
    print(f"  python weather_to_osc.py --config {path}")

def main():
    parser = argparse.ArgumentParser(
        description='Weather to OSC Bridge for Max for Live',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use config file (recommended)
  python weather_to_osc.py --config weather_config.json
  
  # Command line arguments
  python weather_to_osc.py --api-key YOUR_KEY --location "San Francisco"
  
  # Create example config file
  python weather_to_osc.py --create-config weather_config.json
  
Get your free API key at: https://openweathermap.org/api
        """
    )
    
    parser.add_argument('--config', type=str, help='Path to JSON config file')
    parser.add_argument('--create-config', type=str, metavar='PATH',
                       help='Create example config file at specified path')
    parser.add_argument('--api-key', type=str, help='OpenWeatherMap API key')
    parser.add_argument('--location', type=str, help='City name or "City,Country"')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='OSC host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=7400, help='OSC base port (default: 7400)')
    parser.add_argument('--interval', type=int, default=1800, help='Poll interval in seconds (default: 1800)')
    parser.add_argument('--units', choices=['imperial', 'metric'], default='imperial',
                       help='Temperature units (default: imperial)')
    parser.add_argument('--verbose', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handle config file creation
    if args.create_config:
        create_example_config(args.create_config)
        sys.exit(0)
    
    # Load configuration
    if args.config:
        config = load_config(args.config)
        api_key = config.get('api_key')
        location = config.get('location')
        host = config.get('host', '127.0.0.1')
        base_port = config.get('base_port', 7400)
        poll_interval = config.get('poll_interval', 1800)
        units = config.get('units', 'imperial')
        ranges = config.get('ranges', DEFAULT_RANGES)
    else:
        # Use command line arguments
        api_key = args.api_key
        location = args.location
        host = args.host
        base_port = args.port
        poll_interval = args.interval
        units = args.units
        ranges = DEFAULT_RANGES
    
    # Validate required parameters
    if not api_key or not location:
        parser.error("Must provide either --config file or both --api-key and --location")
    
    if api_key == "YOUR_OPENWEATHERMAP_API_KEY_HERE":
        logging.error("Please replace YOUR_OPENWEATHERMAP_API_KEY_HERE with your actual API key")
        sys.exit(1)
    
    # Create and run bridge
    try:
        bridge = WeatherOSCBridge(
            api_key=api_key,
            location=location,
            host=host,
            base_port=base_port,
            poll_interval=poll_interval,
            ranges=ranges,
            units=units
        )
        bridge.run()
    
    except KeyboardInterrupt:
        logging.info("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()