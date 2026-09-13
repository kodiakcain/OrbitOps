# OrbitOps

OrbitOps is a Python command-line toolkit for satellite tracking and basic orbital analysis using publicly available CelesTrak data.

It uses CelesTrak General Perturbations (GP) orbital data in Orbit Mean-Elements Message (OMM) JSON format and the SGP4 propagation model to calculate spacecraft positions, velocities, distances, ground tracks, and interactive orbital visualizations.

## Features

* Calculate current latitude, longitude, and altitude
* Display TEME Cartesian position and velocity
* View satellite catalog information
* Search satellites by name
* Calculate 3D distance between two spacecraft
* Continuously monitor a spacecraft's calculated position
* Generate predicted satellite ground tracks on a Mercator projection
* Export predicted ground-track data to CSV
* Generate interactive 3D satellite visualizations
* Display propagated spacecraft motion around a 3D Earth
* Cache CelesTrak OMM data locally to reduce repeated requests
* Inspect and clear cached orbital data
* Run the OrbitOps test suite from the command line
* Support modern CelesTrak GP data using OMM JSON
* Support NORAD catalog numbers beyond the legacy 5-digit TLE limit

## Installation

OrbitOps requires **Python 3.14 or later**.

Install from PyPI:

```bash
pip install orbitops
```

Then verify the installation:

```bash
orbitops help
```

OrbitOps can also be invoked directly through Python:

```bash
python -m orbitops help
```

### Windows: If `orbitops.exe` Is Blocked

Some Windows systems with Smart App Control, Device Guard, or other application-control policies enabled may block the Python-generated `orbitops.exe` command-line launcher.

You may see an error similar to:

```text
orbitops.exe was blocked by your organization's Device Guard policy.
```

This does not necessarily mean OrbitOps failed to install. Windows may be blocking the generated executable launcher rather than OrbitOps itself.

OrbitOps can be invoked without the generated launcher by running it as a Python module:

```cmd
python -m orbitops help
```

For example:

```cmd
python -m orbitops position 25544
```

or:

```cmd
python -m orbitops visualize 25544 60
```

The other option is to install and run OrbitOps inside a Python virtual environment.

#### 1. Create a folder for the environment

Open Command Prompt and choose where you want the environment:

```cmd
cd C:\Users\YourName\Projects
mkdir orbitops-env
cd orbitops-env
```

#### 2. Create a virtual environment

```cmd
py -3.14 -m venv .venv
```

This creates an isolated Python environment inside the `.venv` folder.

#### 3. Activate the virtual environment

In Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

Your prompt should now begin with `(.venv)`:

```text
(.venv) C:\Users\YourName\Projects\orbitops-env>
```

#### 4. Install OrbitOps

```cmd
python -m pip install orbitops
```

#### 5. Run OrbitOps

```cmd
orbitops help
```

For example:

```cmd
orbitops position 25544
```

or:

```cmd
orbitops visualize 25544 60
```

If the executable launcher is still blocked, use:

```cmd
python -m orbitops visualize 25544 60
```

#### 6. Leave the virtual environment when finished

```cmd
deactivate
```

When you want to use OrbitOps again, return to the environment folder and reactivate it:

```cmd
cd C:\Users\YourName\Projects\orbitops-env
.venv\Scripts\activate
```

You can then use the normal `orbitops` commands again:

```cmd
orbitops position 25544
```

You do **not** need to recreate or reinstall the environment each time. Simply activate the existing environment whenever you want to use OrbitOps.

Using a virtual environment is recommended because it keeps OrbitOps and its Python dependencies isolated from other Python applications on the system.

## Usage

OrbitOps uses NORAD Catalog Numbers to identify spacecraft.

For example, the International Space Station (ISS) has catalog number `25544`.

OrbitOps uses CelesTrak GP data in OMM JSON format, allowing it to work with both traditional 5-digit catalog numbers and newer catalog numbers that cannot be represented using the legacy TLE format.

### Position

Show the calculated latitude, longitude, and altitude of a spacecraft.

```bash
orbitops position 25544
```

Example:

```text
Geographic position of ISS (ZARYA)
--------------------
Latitude:  -32.7625°
Longitude: -54.1085°
Altitude:  432.53 km
```

### TEME State

Show the spacecraft's TEME Cartesian position and velocity.

```bash
orbitops teme 25544
```

Position is reported in kilometers and velocity in kilometers per second.

### Satellite Information

View catalog information for a spacecraft.

```bash
orbitops info 25544
```

This may include information such as the spacecraft name, NORAD catalog number, launch date, owner, inclination, apogee, and perigee.

### Search

Search the satellite catalog by name.

```bash
orbitops search ISS
```

You can also use broader searches:

```bash
orbitops search STARLINK
```

Broad searches may match many spacecraft. The current version of OrbitOps displays the first returned result.

### Distance

Calculate the current straight-line 3D distance between two spacecraft.

```bash
orbitops distance 25544 69012
```

The result is reported in kilometers.

The distance is calculated from both spacecraft's propagated TEME Cartesian positions and represents their instantaneous 3D separation, not distance along Earth's surface.

### Watch

Continuously monitor the calculated geographic position of a spacecraft.

```bash
orbitops watch 25544
```

Example:

```text
ISS (ZARYA) | Lat: 38.2841° | Lon: -72.1832° | Alt: 421.72 km
```

Press `Ctrl+C` to stop.

### Ground Track

Generate a predicted ground-track visualization for a spacecraft over a specified number of minutes.

```bash
orbitops gtrack 25544 180
```

The ground track is displayed on a Mercator projection and includes predicted spacecraft positions over the requested time period.

The visualization includes orbital revolution coloring, UTC reference times, starting and ending positions, orbital period information, sampling information, and the orbital-element epoch used for propagation.

Ground tracks can be generated for durations from 1 to 1440 minutes.

#### CSV Export

Add the optional `--csv` flag to export the predicted ground-track data to a CSV file:

```bash
orbitops gtrack 25544 180 --csv
```

OrbitOps will prompt you to choose where the CSV file should be saved.

The exported CSV contains one row for each propagated ground-track sample with the following fields:

```text
timestamp_utc
latitude_deg
longitude_deg
altitude_km
```

Example:

```csv
timestamp_utc,latitude_deg,longitude_deg,altitude_km
2026-08-24T23:05:37Z,43.933809,49.375321,417.172
2026-08-24T23:06:37Z,45.822370,53.903829,417.493
2026-08-24T23:07:37Z,47.497425,58.746589,417.794
```

The CSV data is generated from the same propagated positions used to create the ground-track visualization.

### 3D Visualization

Generate an interactive 3D visualization of a spacecraft's predicted motion around Earth.

```bash
orbitops visualize 25544 60
```

The first argument is the spacecraft's NORAD Catalog Number and the second is the visualization duration in minutes.

For example:

```text
orbitops visualize 25544 180
```

generates a three-hour visualization for the International Space Station.

Visualization durations can range from 1 to 1440 minutes.

OrbitOps propagates the spacecraft's orbit over the requested period and generates an interactive HTML visualization containing:

* A rotatable and zoomable 3D Earth
* Land masses, coastlines, international borders, and latitude/longitude grid lines
* The spacecraft's predicted orbital path
* A 3D spacecraft model
* Animated spacecraft movement along the propagated path
* Play and pause controls
* A timeline slider for manually moving through the propagated positions
* UTC time for the currently displayed position
* Latitude, longitude, and altitude for the currently displayed position

After the visualization is generated, OrbitOps opens a Save As dialog so you can choose where the HTML file should be stored.

After saving, the visualization opens automatically in your default web browser.

The generated visualization is an HTML file and uses Three.js in the browser to render the interactive 3D scene. An internet connection may therefore be required when opening the visualization so the browser can load the required Three.js modules.

The spacecraft positions shown in the visualization are propagated from CelesTrak orbital elements using SGP4. They are predicted positions rather than live spacecraft telemetry.

### Cache

OrbitOps locally caches downloaded CelesTrak OMM data for up to two hours to reduce unnecessary repeated requests.

View all cached orbital data:

```bash
orbitops cache info
```

View cached data for a specific spacecraft:

```bash
orbitops cache info 25544
```

Clear cached data for a specific spacecraft:

```bash
orbitops cache clear 25544
```

Clear the entire OrbitOps cache:

```bash
orbitops cache clear
```

Cached orbital elements are still propagated locally to the current or requested time, so using cached data does not cause spacecraft positions to remain static.

### Test Suite

The OrbitOps source repository includes an automated pytest test suite for development and release verification.

When working from a development installation, run:

```bash
uv run pytest
```

The test suite verifies behavior across OrbitOps components, including API handling, caching, command-line behavior, orbital propagation utilities, ground-track generation, data validation, visualization utilities, and error handling.

## Command Reference

| Command       | Usage                                       | Description                                                |
| ------------- | ------------------------------------------- | ---------------------------------------------------------- |
| `position`    | `orbitops position <CATNR>`                 | Show latitude, longitude, and altitude                     |
| `teme`        | `orbitops teme <CATNR>`                     | Show TEME position and velocity                            |
| `info`        | `orbitops info <CATNR>`                     | Show satellite catalog information                         |
| `search`      | `orbitops search <name>`                    | Search satellites by name                                  |
| `distance`    | `orbitops distance <CATNR1> <CATNR2>`       | Calculate 3D spacecraft separation                         |
| `watch`       | `orbitops watch <CATNR>`                    | Continuously monitor spacecraft position                   |
| `gtrack`      | `orbitops gtrack <CATNR> <MINUTES> [--csv]` | Generate a predicted ground track with optional CSV export |
| `visualize`   | `orbitops visualize <CATNR> <MINUTES>`      | Generate an interactive 3D spacecraft visualization        |
| `cache info`  | `orbitops cache info [CATNR]`               | View cached orbital data                                   |
| `cache clear` | `orbitops cache clear [CATNR]`              | Clear cached orbital data                                  |
| `help`        | `orbitops help`                             | Display the help menu                                      |

## How It Works

OrbitOps retrieves publicly available General Perturbations (GP) orbital data from CelesTrak in OMM JSON format.

For position calculations, OrbitOps retrieves a spacecraft's orbital elements and uses SGP4 to propagate its orbit to the requested time.

```text
CelesTrak
    |
    | GP / OMM JSON
    v
Local OrbitOps cache
    |
    | SGP4
    v
Calculated spacecraft state
    |
    +--> TEME position and velocity
    |
    +--> Latitude / Longitude / Altitude
    |
    +--> Predicted ground track
    |
    +--> Interactive 3D visualization
```

OrbitOps uses the OMM fields provided by CelesTrak to initialize the SGP4 propagation model. This avoids reliance on the legacy fixed-width TLE representation and allows OrbitOps to support newer NORAD catalog numbers beyond the traditional 5-digit TLE limit.

Downloaded OMM data is cached locally for up to two hours. If valid cached data is available, OrbitOps reuses it instead of issuing another request to CelesTrak.

For continuous tracking and visualization, the orbital data does not need to be downloaded for every propagated point. OrbitOps retrieves or loads the orbital elements and performs subsequent propagation locally.

For the 3D visualization, the propagated geographic coordinates are converted into 3D Cartesian coordinates and embedded into a generated HTML document. The browser then renders the Earth, orbital path, spacecraft model, and animation using Three.js.

## Data and Accuracy

OrbitOps does **not** receive live spacecraft telemetry.

Positions are calculated from publicly available CelesTrak GP orbital elements using SGP4. They should therefore be treated as **calculated or predicted positions**, not authoritative spacecraft positions.

Accuracy can be affected by factors including:

* Age of the orbital elements
* Atmospheric drag
* Spacecraft maneuvers
* Spacecraft orbit
* Time elapsed from the orbital-element epoch

The 3D visualization displays propagated positions produced from the same underlying orbital data and should not be interpreted as a real-time mission visualization or authoritative spacecraft telemetry display.

OrbitOps is intended for educational, informational, satellite-tracking, visualization, and general orbital-analysis purposes.

## Testing

OrbitOps includes an automated pytest test suite covering the major components of the application.

From the development environment, the complete test suite can be run with:

```bash
uv run pytest
```

Additional development checks can be run with:

```bash
uv run ruff check .
uv run pyright
uv run pytest
```

These checks are used to verify code quality, static typing, input validation, command behavior, caching logic, API handling, propagation utilities, visualization utilities, and other application functionality.

A built wheel can also be installed into a clean virtual environment to verify that OrbitOps and its packaged resources work independently of the source repository.

For example:

```bash
python -m venv release-test
```

Activate the environment and install the built wheel:

```bash
pip install dist/orbitops-0.2.7-py3-none-any.whl
```

Then verify the installed package:

```bash
orbitops help
orbitops position 25544
orbitops visualize 25544 30
```

The Python module entry point can also be tested with:

```bash
python -m orbitops help
```

Passing software tests does not imply precision orbit determination or certify OrbitOps for operational spacecraft use.

## Development

Clone the repository:

```bash
git clone <repository-url>
cd OrbitOps
```

Install the development environment:

```bash
uv sync
```

Run OrbitOps:

```bash
uv run orbitops position 25544
```

Generate a 3D visualization:

```bash
uv run orbitops visualize 25544 60
```

Run the complete test suite:

```bash
uv run pytest
```

Run code-quality and type checks:

```bash
uv run ruff check .
uv run pyright
```

Build the package:

```bash
uv build
```

Verify the built distribution:

```bash
uv run twine check dist/*
```

## License

OrbitOps is licensed under the MIT License.

See the `LICENSE` file for the full license terms.

## Disclaimer

OrbitOps is provided for educational, informational, and general satellite tracking purposes only.

OrbitOps does not provide authoritative spacecraft telemetry, precision orbit determination, or mission-operational data. Satellite positions and other orbital information produced by OrbitOps are calculated from publicly available orbital elements using mathematical propagation models and may contain errors or become inaccurate over time.

OrbitOps is not intended for spacecraft navigation, collision avoidance, rendezvous operations, launch operations, flight safety, mission-critical decision-making, or any other safety-critical application.

Users are responsible for independently verifying any data produced by OrbitOps before relying on it for operational purposes.

THE SOFTWARE AND ALL OUTPUT GENERATED BY THE SOFTWARE ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. USE OF ORBITOPS AND RELIANCE ON ITS OUTPUT IS AT THE USER'S OWN RISK.
