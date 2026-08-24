# Changelog

All notable changes to OrbitOps will be documented in this file.

## [0.2.0] - 2026-08-23

### Added

- Added predicted satellite ground-track generation.

- Added Mercator-projection ground-track visualization using Matplotlib and Cartopy.

- Added color-coded orbital revolution visualization.

- Added UTC reference markers along predicted ground tracks.

- Added ground-track start and end position markers.

- Added orbital period information to ground-track visualizations.

- Added TLE epoch and sampling information to ground-track visualizations.

- Added `gtrack` command for generating predicted ground tracks over a specified time period.

### Changed

- Updated the OrbitOps help menu with the new ground-track command.

- Expanded orbital visualization capabilities using propagated TLE data.

## [0.1.1] - 2026-08-23

### Added

- Added Rich-powered CLI output and formatting.

- Added loading spinners while fetching satellite data.

- Added search status indicators.

### Changed

- Improved CLI error and warning messages.

- Improved help menu formatting.

- Added HTTP request timeouts for improved reliability.

## [0.1.0] - 2026-08-22

### Added

- Initial release of OrbitOps.

- Added satellite lookup using NORAD catalog numbers.

- Added real-time geographic position calculations.

- Added TEME position and velocity calculations.

- Added satellite catalog information and name search.

- Added satellite-to-satellite distance calculations.

- Added continuous satellite position monitoring.