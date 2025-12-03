# Changelog

All notable changes to the Weather-Controlled Music System will be documented here.

## [1.0.0] - 2024-12-02

### Added
- Initial public release
- Python OSC bridge with OpenWeatherMap API integration
- Configuration file support (JSON)
- Command-line interface with arguments
- Error handling and retry logic
- Logging with configurable verbosity
- Support for imperial and metric units
- Configurable normalization ranges for different climates
- 5 weather parameters: temperature, wind speed, rainfall, pressure, humidity
- Automatic value clamping to 0.0-1.0 range
- Example configuration file generator
- Comprehensive README with mapping examples
- Installation guide
- MIT License

### Weather Parameters
- Temperature: Configurable range, default 0-100°F
- Wind Speed: Configurable range, default 0-25 mph
- Rainfall: Configurable range, default 0-5mm/hr
- Barometric Pressure: Configurable range, default 980-1040 hPa
- Humidity: Configurable range, default 0-100%

### Technical Details
- OSC output on ports 7400-7404 (configurable base port)
- 30-minute default polling interval (configurable)
- 3 retry attempts with 5-second delays
- 10-second API timeout
- Normalized output values (0.0-1.0)

### Known Limitations
- Requires separate TouchOSC receiver devices in Ableton Live
- Free API tier limited to 1,000 calls/day
- Main WEATHER.amxd device is basic (no parameter exposure, no visual status)

## [Unreleased] - Future Improvements

### Planned Features
- Enhanced Max for Live main device with:
  - Live parameter exposure for automation
  - Visual connection status indicator
  - Built-in mapping interface
  - Display of raw and normalized values
  - Error state display
- Support for weather forecasts (predict parameter changes)
- Historical weather data logging
- Multiple location support in single script
- GUI configuration tool (no command line required)
- Standalone Max application (no Ableton required)
- Additional weather parameters:
  - UV index
  - Cloud coverage
  - Visibility
  - Sunrise/sunset times
- Preset mapping templates for common use cases
- Integration with other weather APIs (Weather Underground, Dark Sky)

### Known Issues to Address
- Main device doesn't show connection status
- No built-in way to test OSC connectivity
- TouchOSC devices need manual port configuration
- No preset save/recall for normalization ranges
