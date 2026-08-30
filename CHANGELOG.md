# Changelog

All notable changes to OrbitOps will be documented in this file.

## [0.2.6] - 2026-08-30

### Fixed

- Fixed the pyprpoject.toml to include pytest.

## [0.2.5] - 2026-08-30

### Fixed

- Fixed the `orbitops tests` command to run pytest in a separate subprocess.
- Fixed inconsistent test behavior caused by Rich terminal formatting interfering with pytest output capture.
- Fixed the test command so the OrbitOps test suite runs consistently when invoked through the CLI.

## [0.2.4] - 2026-08-30

### Added

- Added comprehensive automated test coverage across OrbitOps.
- Added tests for API data retrieval and error handling.
- Added tests for local OMM caching and cache-management functionality.
- Added tests for command-line commands, argument handling, and error conditions.
- Added tests for ground-track generation and CSV export.
- Added tests for TEME and geographic propagation functionality.
- Added tests for future orbital propagation and SGP4 error handling.
- Added tests for input type and value validation throughout the application.
- Added `orbitops test` command for running the OrbitOps test suite from the command line.

### Changed

- Added consistent input validation across OrbitOps modules.
- Improved validation of catalog numbers, OMM data, time durations, ground-track data, filenames, and propagation intervals.
- Updated the OrbitOps help menu to document the new `test` command.
- Expanded development documentation with instructions for running pytest, Ruff, and Pyright.
- Updated documentation to describe the OrbitOps automated test suite.

## [0.2.3] - 2026-08-30

### Added

- Added local caching for CelesTrak OMM orbital data.
- Added a two-hour cache lifetime to reduce unnecessary repeated requests to CelesTrak.
- Added `orbitops cache info` for viewing all cached orbital data.
- Added `orbitops cache info <CATNR>` for viewing cached data for a specific spacecraft.
- Added `orbitops cache clear` for clearing the entire OrbitOps cache.
- Added `orbitops cache clear <CATNR>` for clearing cached data for a specific spacecraft.
- Added cross-platform cache directory handling using `platformdirs`.

### Changed

- Updated orbital data retrieval to use valid cached OMM data before issuing a new request to CelesTrak.
- Updated the OrbitOps help menu to document cache-management commands.
- Updated documentation to explain local orbital-data caching behavior.

## [0.2.2] - 2026-08-25

### Changed

- Refactored orbital data retrieval to use CelesTrak GP/OMM JSON data.
- Updated SGP4 and Skyfield propagation to initialize from OMM data.
- Updated position, TEME, distance, watch, and ground-track features to use OMM-based orbital data.

### Added

- Added support for newer 6-digit NORAD catalog numbers that cannot be represented in legacy TLE format.

## [0.2.1] - 2026-08-24

### Added

- Added optional CSV export for predicted satellite ground tracks.
- Added `--csv` option to the `gtrack` command.
- Added a save dialog for selecting the location of exported ground-track CSV files.
- Added UTC timestamps, latitude, longitude, and altitude data to ground-track CSV exports.

### Changed

- Updated the OrbitOps help menu to document the optional `--csv` ground-track export.
- Updated `gtrack` command usage to `orbitops gtrack <CATNR> <MINUTES> [--csv]`.
- Improved ground-track argument validation and error handling.

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