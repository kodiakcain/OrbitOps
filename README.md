# OrbitOps

OrbitOps is a Python command-line tool for retrieving satellite catalog data, propagating spacecraft orbits, calculating real-time spacecraft positions, and performing basic orbital analysis using publicly available CelesTrak data.

OrbitOps uses satellite Two-Line Element (TLE) data together with the SGP4 propagation model to calculate spacecraft state vectors and geographic positions.

## Features

OrbitOps currently supports:

* Retrieving real-time calculated satellite positions
* Displaying TEME Cartesian position and velocity
* Retrieving satellite catalog information
* Searching the satellite catalog by spacecraft name
* Calculating the 3D distance between two spacecraft
* Continuously monitoring a spacecraft's position
* Querying spacecraft using NORAD Catalog Numbers

## Requirements

OrbitOps requires Python 3.14 or later.

Current Python dependencies:

```text
requests==2.34.2
sgp4==2.27
skyfield==1.55
```

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd OrbitOps
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

If developing OrbitOps locally, install the package in editable mode:

```bash
pip install -e .
```

If using `uv`:

```bash
uv sync
```

The `orbitops` command is registered through:

```toml
[project.scripts]
orbitops = "orbitops.cli:main"
```

After installation, commands can be run directly from the terminal:

```bash
orbitops <command> <arguments>
```

---

# Usage

Most OrbitOps commands identify spacecraft using their **NORAD Catalog Number**.

For example, the International Space Station has NORAD Catalog Number:

```text
25544
```

Therefore:

```bash
orbitops position 25544
```

requests the orbital data for the ISS and calculates its current geographic position.

## `position`

Calculate the current geographic position of a spacecraft.

### Usage

```bash
orbitops position <catalog_number>
```

### Example

```bash
orbitops position 25544
```

Example output:

```text
Geographic position of ISS (ZARYA)
--------------------
Latitude:  -32.7625°
Longitude: -54.1085°
Altitude:  432.53 km
```

The returned values represent:

* **Latitude** — angular position north or south of Earth's equator
* **Longitude** — angular position east or west around Earth
* **Altitude** — spacecraft altitude above Earth's surface in kilometers

The position is calculated locally using SGP4 propagation from the spacecraft's current TLE.

Because a TLE represents an orbital model rather than direct live telemetry, this should be interpreted as the spacecraft's **predicted current position**.

---

## `teme`

Display the current spacecraft state in the TEME Cartesian coordinate system.

### Usage

```bash
orbitops teme <catalog_number>
```

### Example

```bash
orbitops teme 25544
```

Example output:

```text
TEME Cartesian State of ISS (ZARYA)
--------------------

Position:
  X:   -4123.42 km
  Y:    2861.84 km
  Z:    4572.11 km

Velocity:
  X:      -5.214 km/s
  Y:      -3.847 km/s
  Z:       2.910 km/s
```

The spacecraft state contains two three-dimensional vectors:

```text
Position = (X, Y, Z)
Velocity = (VX, VY, VZ)
```

Position components are returned in:

```text
kilometers
```

Velocity components are returned in:

```text
kilometers per second
```

OrbitOps uses the SGP4 propagator to calculate the TEME state at the current UTC time.

---

## `info`

Retrieve satellite catalog information from CelesTrak.

### Usage

```bash
orbitops info <catalog_number>
```

### Example

```bash
orbitops info 25544
```

The command displays the catalog information returned for that spacecraft.

Information may include fields such as:

```text
OBJECT_NAME
OBJECT_ID
NORAD_CAT_ID
OBJECT_TYPE
OPS_STATUS_CODE
OWNER
LAUNCH_DATE
LAUNCH_SITE
DECAY_DATE
PERIOD
INCLINATION
APOGEE
PERIGEE
RCS
ORBIT_CENTER
```

Example:

```text
OBJECT_NAME: ISS (ZARYA)
OBJECT_ID: 1998-067A
NORAD_CAT_ID: 25544
OBJECT_TYPE: PAY
OPS_STATUS_CODE: +
OWNER: ISS
LAUNCH_DATE: 1998-11-20
PERIOD: 92.9
INCLINATION: 51.64
APOGEE: 423
PERIGEE: 417
```

Unlike `position`, this command primarily displays descriptive and catalog information about the spacecraft rather than its instantaneous location.

---

## `search`

Search the CelesTrak satellite catalog using a spacecraft name.

### Usage

```bash
orbitops search <name>
```

### Example

```bash
orbitops search ISS
```

The search command retrieves matching spacecraft and currently displays the first returned catalog match.

Example output:

```text
OBJECT_NAME: ISS (ZARYA)
OBJECT_ID: 1998-067A
NORAD_CAT_ID: 25544
OBJECT_TYPE: PAY
...
```

Search terms do not necessarily have to contain the spacecraft's complete catalog name.

For example:

```bash
orbitops search ISS
```

or:

```bash
orbitops search STARLINK
```

Broad search terms such as `STARLINK` may match many spacecraft.

The current implementation selects the first result returned by the search:

```python
data = api.search_by_name(sys.argv[2])[0]
```

Future versions may support displaying and filtering multiple search results.

---

## `distance`

Calculate the instantaneous three-dimensional Euclidean distance between two spacecraft.

### Usage

```bash
orbitops distance <catalog_number_1> <catalog_number_2>
```

### Example

```bash
orbitops distance 25544 69012
```

This retrieves the TLE for both spacecraft, propagates both orbits to their current TEME Cartesian positions, and calculates:

```text
distance = sqrt(
    (x2 - x1)^2 +
    (y2 - y1)^2 +
    (z2 - z1)^2
)
```

Because the SGP4 TEME position vectors are expressed in kilometers, the resulting distance is also expressed in:

```text
kilometers
```

The distance represents **straight-line 3D spacecraft separation**, not distance along Earth's surface.

For example:

```text
ISS (ZARYA) <-------- 13,357 km --------> Spacecraft B
```

Two low-Earth-orbit spacecraft can still be more than 13,000 km apart if they are located on substantially different sides of Earth.

---

## `watch`

Continuously calculate and display the current geographic position of a spacecraft.

### Usage

```bash
orbitops watch <catalog_number>
```

### Example

```bash
orbitops watch 25544
```

The command retrieves the spacecraft TLE and repeatedly propagates it forward using the current time.

Example output may resemble:

```text
ISS (ZARYA) | Lat: 38.2841° | Lon: -72.1832° | Alt: 421.72 km
```

The position is recalculated locally using SGP4.

OrbitOps does **not** need to repeatedly request new orbital data from CelesTrak for every position update. Once the current TLE has been downloaded, SGP4 can propagate the spacecraft locally.

Conceptually:

```text
CelesTrak
    |
    | Retrieve TLE
    v
OrbitOps
    |
    | SGP4 propagation
    |
    +--> Current position
    +--> +1 second
    +--> +2 seconds
    +--> +3 seconds
    +--> ...
```

This reduces unnecessary API traffic while allowing frequent position updates.

Use `Ctrl+C` to terminate the watch command.

---

# Command Reference

| Command    | Usage                                 | Description                                         |
| ---------- | ------------------------------------- | --------------------------------------------------- |
| `position` | `orbitops position <CATNR>`           | Calculate current latitude, longitude, and altitude |
| `teme`     | `orbitops teme <CATNR>`               | Display current TEME position and velocity          |
| `info`     | `orbitops info <CATNR>`               | Display CelesTrak satellite catalog information     |
| `search`   | `orbitops search <name>`              | Search the satellite catalog by name                |
| `distance` | `orbitops distance <CATNR1> <CATNR2>` | Calculate current 3D spacecraft separation          |
| `watch`    | `orbitops watch <CATNR>`              | Continuously monitor spacecraft geographic position |

---

# Examples

Track the International Space Station:

```bash
orbitops position 25544
```

Display its Cartesian state:

```bash
orbitops teme 25544
```

Retrieve its catalog information:

```bash
orbitops info 25544
```

Search for the ISS by name:

```bash
orbitops search ISS
```

Calculate the distance between two spacecraft:

```bash
orbitops distance 25544 69012
```

Continuously monitor the ISS:

```bash
orbitops watch 25544
```

---

# How OrbitOps Works

OrbitOps combines publicly available orbital data with local orbital propagation.

The basic workflow is:

```text
NORAD Catalog Number
        |
        v
     CelesTrak
        |
        | TLE / catalog data
        v
      OrbitOps
        |
        v
       SGP4
        |
        +-------------------+
        |                   |
        v                   v
 TEME Cartesian       Geographic
   coordinates          position
        |                   |
        v                   v
  X, Y, Z, Vx, Vy, Vz   Lat/Lon/Alt
```

## CelesTrak

CelesTrak provides the orbital and catalog data used by OrbitOps.

OrbitOps currently retrieves TLE data from:

```text
https://celestrak.org/NORAD/elements/gp.php
```

Satellite catalog information is retrieved from:

```text
https://celestrak.org/satcat/records.php
```

## SGP4

OrbitOps uses the Simplified General Perturbations 4 model, or **SGP4**, to propagate spacecraft orbits.

A TLE contains the orbital parameters needed by SGP4 to estimate the spacecraft's position and velocity at a specified time.

OrbitOps can therefore use one set of orbital data to calculate:

```text
position now
position 10 seconds from now
position 1 minute from now
position 30 minutes from now
...
```

without making a new HTTP request for every calculation.

---

# Coordinate Systems

OrbitOps currently exposes two useful representations of spacecraft position.

## TEME Cartesian Coordinates

The `teme` command represents the spacecraft as:

```text
X
Y
Z
```

relative to Earth's center.

It also provides:

```text
VX
VY
VZ
```

representing spacecraft velocity.

Cartesian coordinates are particularly useful for calculations such as spacecraft-to-spacecraft distance.

## Geographic Coordinates

The `position` and `watch` commands represent the spacecraft using:

```text
Latitude
Longitude
Altitude
```

These coordinates are more useful for understanding where the spacecraft is relative to Earth's surface.

---

# Accuracy

OrbitOps does not receive live spacecraft telemetry.

Positions are calculated using:

```text
CelesTrak orbital data
        +
SGP4 propagation
```

The resulting positions are predictions based on the latest available orbital elements.

Accuracy depends on factors including:

* Age of the TLE
* Spacecraft orbit
* Atmospheric drag
* Maneuvers performed after the orbital elements were generated
* Time elapsed from the TLE epoch

OrbitOps should therefore be used for:

* Educational purposes
* Satellite tracking
* Orbital visualization
* General orbital analysis
* Pass and ground-track experimentation

It should not be used for:

* Spacecraft navigation
* Collision avoidance
* Rendezvous operations
* Safety-critical mission operations
* Precision orbit determination

---

# Project Structure

A simplified OrbitOps structure may look like:

```text
OrbitOps/
├── src/
│   └── orbitops/
│       ├── __init__.py
│       ├── cli.py
│       ├── api.py
│       └── propogation.py
├── tests/
├── pyproject.toml
├── requirements.txt
└── README.md
```

### `cli.py`

Handles command-line arguments and command routing.

### `api.py`

Handles communication with CelesTrak and higher-level satellite data operations.

### `propogation.py`

Handles orbital propagation and coordinate calculations.

---

# Development

Install development dependencies using:

```bash
uv sync
```

Development tools include:

```text
pytest
pyright
ruff
```

Run tests:

```bash
pytest
```

Run Ruff:

```bash
ruff check .
```

Run Pyright:

```bash
pyright
```

---

# Current Status

OrbitOps is under active development.

Current functionality includes:

```text
✓ TEME state calculation
✓ Geographic position calculation
✓ Satellite catalog lookup
✓ Name search
✓ Spacecraft distance calculation
✓ Continuous position monitoring
```

Potential future capabilities include:

```text
Ground station management
Satellite pass prediction
Ground-track prediction
Saved spacecraft
Multiple-spacecraft tracking
JSON/CSV export
Interactive 3D globe visualization
```

---

# Disclaimer

OrbitOps is an independent educational and analytical project.

Satellite positions are calculated from publicly available orbital elements and should not be interpreted as authoritative spacecraft telemetry or mission-operational data.
