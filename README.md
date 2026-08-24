# OrbitOps

OrbitOps is a Python command-line toolkit for satellite tracking and basic orbital analysis using publicly available CelesTrak data.

It uses Two-Line Element (TLE) data and the SGP4 propagation model to calculate spacecraft positions, velocities, and distances.

## Features

- Calculate current latitude, longitude, and altitude

- Display TEME Cartesian position and velocity

- View satellite catalog information

- Search satellites by name

- Calculate 3D distance between two spacecraft

- Continuously monitor a spacecraft's calculated position

- Generate predicted satellite ground tracks on a Mercator projection

- Export predicted ground-track data to CSV

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

## Usage

OrbitOps uses NORAD Catalog Numbers to identify spacecraft.

For example, the International Space Station (ISS) has catalog number `25544`.

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

The visualization includes orbital revolution coloring, UTC reference times, starting and ending positions, orbital period information, sampling information, and the TLE epoch used for propagation.

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

## Command Reference

| Command | Usage | Description |
| --- | --- | --- |
| `position` | `orbitops position <CATNR>` | Show latitude, longitude, and altitude |
| `teme` | `orbitops teme <CATNR>` | Show TEME position and velocity |
| `info` | `orbitops info <CATNR>` | Show satellite catalog information |
| `search` | `orbitops search <name>` | Search satellites by name |
| `distance` | `orbitops distance <CATNR1> <CATNR2>` | Calculate 3D spacecraft separation |
| `watch` | `orbitops watch <CATNR>` | Continuously monitor spacecraft position |
| `gtrack` | `orbitops gtrack <CATNR> <MINUTES> [--csv]` | Generate a predicted ground track with optional CSV export |
| `help` | `orbitops help` | Display the help menu |

## How It Works

OrbitOps retrieves publicly available orbital data from CelesTrak.

For position calculations, OrbitOps retrieves a spacecraft's TLE and uses SGP4 to propagate its orbit to the current time.

```text
CelesTrak
    |
    | TLE
    v
OrbitOps
    |
    | SGP4
    v
Calculated spacecraft state
    |
    +--> TEME position and velocity
    |
    +--> Latitude / Longitude / Altitude
```

For continuous tracking, the TLE does not need to be downloaded every second. OrbitOps retrieves the orbital elements and performs subsequent propagation locally.

## Data and Accuracy

OrbitOps does **not** receive live spacecraft telemetry.

Positions are calculated from publicly available orbital elements using SGP4. They should therefore be treated as **calculated or predicted positions**, not authoritative spacecraft positions.

Accuracy can be affected by factors including:

- Age of the orbital elements

- Atmospheric drag

- Spacecraft maneuvers

- Spacecraft orbit

- Time elapsed from the TLE epoch

OrbitOps is intended for educational, informational, satellite-tracking, visualization, and general orbital-analysis purposes.

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

## License

OrbitOps is licensed under the MIT License.

See the `LICENSE` file for the full license terms.

## Disclaimer

OrbitOps is provided for educational, informational, and general satellite tracking purposes only.

OrbitOps does not provide authoritative spacecraft telemetry, precision orbit determination, or mission-operational data. Satellite positions and other orbital information produced by OrbitOps are calculated from publicly available orbital elements using mathematical propagation models and may contain errors or become inaccurate over time.

OrbitOps is not intended for spacecraft navigation, collision avoidance, rendezvous operations, launch operations, flight safety, mission-critical decision-making, or any other safety-critical application.

Users are responsible for independently verifying any data produced by OrbitOps before relying on it for operational purposes.

THE SOFTWARE AND ALL OUTPUT GENERATED BY THE SOFTWARE ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. USE OF ORBITOPS AND RELIANCE ON ITS OUTPUT IS AT THE USER'S OWN RISK.