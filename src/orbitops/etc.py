import csv
import math
import subprocess
import sys
from datetime import datetime
from tkinter import filedialog

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from rich.console import Console
from skyfield.api import EarthSatellite, load, wgs84

console = Console()

def print_help_menu() -> None:
    """Print the help menu."""
    console.print("[bold cyan]=== OrbitOps Help Menu ===[/bold cyan]\n")

    print("position <CATNR>                     Show current latitude, longitude, and altitude")
    print("teme <CATNR>                         Show current TEME position and velocity")
    print("info <CATNR>                         Show satellite catalog information")
    print("search <name>                        Search for a satellite by name")
    print("distance <CATNR1> <CATNR2>           Show distance between two satellites")
    print("watch <CATNR>                        Continuously track a satellite's position")
    print("gtrack <CATNR> <minutes> [--csv]     Plot a ground track; optionally export CSV")
    print("cache info                           Show all cached satellite data")
    print("cache info <CATNR>                   Show cached data for one satellite")
    print("cache clear                          Clear all cached satellite data")
    print("cache clear <CATNR>                  Clear cached data for one satellite")
    print("test                                 Run the OrbitOps test suite")
    print("help                                 Show this help menu")

def generate_ground_track(omm_data: dict, times: list) -> list[tuple]:
    """Generate the grond track and return it."""

    if type(omm_data) is not dict:

        raise TypeError("OMM data must be a dict.")

    if type(times) is not list:

        raise TypeError("Times must be a list.")
    
    timescale = load.timescale()

    satellite = EarthSatellite.from_omm(
        timescale,
        omm_data,
    )

    ground_track = []

    for timestamp in times:
        skyfield_time = timescale.from_datetime(timestamp)

        position = satellite.at(skyfield_time)

        geographic = wgs84.geographic_position_of(position)

        ground_track.append(
            (
                timestamp,
                geographic.latitude.degrees,
                geographic.longitude.degrees,
                geographic.elevation.km,
            )
        )

    return ground_track

def plot_ground_track( ground_track: list[tuple], sat_name: str, minutes: int, omm_data: dict,) -> None:
    """Plots a satellite ground track on a Mercator projection."""

    if type(ground_track) is not list:

        raise TypeError("Ground track should be type list[tuple]")

    if type(sat_name) is not str:

        raise TypeError("Sat name should be a string.")

    if type(minutes) is not int:

        raise TypeError("Minutes should be an int.")

    if type(omm_data) is not dict:

        raise TypeError("OMM data should be a dict.")

    if len(sat_name) <= 0 or len(sat_name) > 30:

        raise ValueError("Satellite name must be between 1 and 30 digits.")

    if minutes <= 0 or minutes > 1440:

        raise ValueError("Minutes must be between 1 and 1440.")

    with console.status("[bold green]Creating ground track..."):

        # Safety check
        if not ground_track:
            console.print("[bold red]Internal orbitops error. No ground track found.[/bold red]")
            return

        if minutes > 1440:
            console.print("[bold red]Max minutes of 1440, try again.[/bold red]")
            return

        if minutes < 1:
            console.print("[bold red]Minutes must be in range 1-1440.[/bold red]")
            return

        # Create the satellite so we can determine orbital information.
        timescale = load.timescale()

        # Create Skyfield satellite object using spacecraft OMM data
        satellite = EarthSatellite.from_omm(
            timescale,
            omm_data,
        )

        # time = total angle / angular speed, using radians
        orbital_period_minutes = (2 * math.pi / satellite.model.no_kozai)

        # Create the window for the plot, specifying size in inches
        figure = plt.figure(figsize=(14, 8))

        # Set the window name
        figure.canvas.manager.set_window_title(f"Ground-Track-{sat_name.strip()}-{datetime.now():%Y-%m-%d-%H-%M}")

        # Set the plotting region within the figure, 1 row, 1 col, plot 1, use Cartopy Mercator projection
        axis = figure.add_subplot(1, 1, 1, projection=ccrs.Mercator(min_latitude=-85, max_latitude=85, ),)

        # Grab the start and end times
        start_time = ground_track[0][0]
        end_time = ground_track[-1][0]

        # Set the title for above the map
        axis.set_title(f"{sat_name.strip()} - {minutes} Minute Ground Track\n"f"{start_time:%Y-%m-%d %H:%M UTC} to "f"{end_time:%Y-%m-%d %H:%M UTC}")

        # Draw the outlines of continents
        axis.coastlines()

        # Draw the latitude and longitude gridlines
        axis.gridlines(draw_labels=True, linewidth=0.5,
        )

        # Calculate sampling interval
        if len(ground_track) > 1:
            sample_interval_seconds = (ground_track[1][0] - ground_track[0][0]).total_seconds()
        else:
            sample_interval_seconds = 0

        # Grab the epoch of the satellite
        tle_epoch = satellite.epoch.utc_datetime()

        # Build the box for the sat info
        info_text = (f"Orbital period: {orbital_period_minutes:.2f} min\n" f"Samples: {len(ground_track)}\n" f"Sample interval: {sample_interval_seconds:.0f} sec\n" f"TLE epoch: {tle_epoch:%Y-%m-%d %H:%M UTC}")

        # Position information in the box, using a bounding box
        axis.text( 0.01, 0.99, info_text, transform=axis.transAxes, fontsize=8, verticalalignment="top", horizontalalignment="left", bbox={"boxstyle": "round","facecolor": "white", "alpha": 0.8, },)

        # Store points for each predicted revolution
        orbits = {}

        # Extract all ground track information, time, lat, lon, and orbit number
        for point in ground_track:
            timestamp = point[0]
            latitude = float(point[1])
            longitude = float(point[2])

            elapsed_minutes = (timestamp - start_time).total_seconds() / 60

            # Store in proper orbit
            orbit_number = (int(elapsed_minutes // orbital_period_minutes) + 1)

            if orbit_number not in orbits:
                orbits[orbit_number] = []

            orbits[orbit_number].append((timestamp, latitude, longitude,))

        # Plot the revolutions
        for orbit_number, orbit in orbits.items():

            # Keep every segment of the same revolution the same color
            orbit_color = f"C{(orbit_number - 1) % 10}"

            # Storing all segments of orbit
            segments = []
            current_segment = []

            for point in orbit:
                timestamp, latitude, longitude = point

                # Split the plotted line when crossing the International Date Line.
                if current_segment:
                    previous_longitude = current_segment[-1][2]

                    # Detect the jump
                    if abs(longitude - previous_longitude) > 180:
                        segments.append(current_segment)
                        current_segment = []

                current_segment.append((timestamp,latitude, longitude))

            if current_segment:
                segments.append(current_segment)

            first_segment = True

            # Grab the lats and lons
            for segment in segments:
                latitudes = [
                    point[1]
                    for point in segment
                ]

                longitudes = [
                    point[2]
                    for point in segment
                ]

                # Plot the orbits, converting coordinates as needed
                axis.plot(longitudes, latitudes, color=orbit_color, linewidth=2, transform=ccrs.PlateCarree(), label=(f"Revolution {orbit_number}" if first_segment else None ),)

                first_segment = False

        # Starting point
        start_latitude = float(ground_track[0][1])
        start_longitude = float(ground_track[0][2])

        # Draw the start point
        axis.plot(start_longitude, start_latitude, marker="o", markersize=7, transform=ccrs.PlateCarree(),)

        # Add the start text
        axis.text(start_longitude, start_latitude, f" Start\n {start_time:%H:%M UTC}", fontsize=8, transform=ccrs.PlateCarree(),)

        # Ending point
        end_latitude = float(ground_track[-1][1])
        end_longitude = float(ground_track[-1][2])

        # Plot the marker for the end time
        axis.plot(end_longitude, end_latitude, marker="o", markersize=7, transform=ccrs.PlateCarree(),)

        axis.text(end_longitude, end_latitude, f" End\n {end_time:%H:%M UTC}", fontsize=8, transform=ccrs.PlateCarree(),)

        # Add the time markers every 15 minutes
        marker_interval_minutes = 15

        if sample_interval_seconds > 0:
            marker_interval_points = max(1, int(marker_interval_minutes * 60 / sample_interval_seconds),)
        else:
            marker_interval_points = 1

        # Plot the time markers
        for index, point in enumerate(ground_track):
            timestamp = point[0]
            latitude = float(point[1])
            longitude = float(point[2])

            if (
                index != 0
                and index != len(ground_track) - 1
                and index % marker_interval_points == 0
            ):
                axis.plot(
                    longitude,
                    latitude,
                    marker=".",
                    markersize=4,
                    transform=ccrs.PlateCarree(),
                )

                axis.text(
                    longitude,
                    latitude,
                    f" {timestamp:%H:%M}",
                    fontsize=7,
                    transform=ccrs.PlateCarree(),
                )

        # Add the legend to the lower left
        axis.legend(
            loc="lower left",
        )

    plt.show()

def save_ground_track_csv(ground_track: list[tuple], file_name: str,) -> None:
    """Ask the user for a location and save ground-track data as CSV."""

    if type(ground_track) is not list:

        raise TypeError("Ground track must be a list[tuple].")

    if type(file_name) is not str:

        raise TypeError("File name should be a string.")

    if len(file_name) <= 0 or len(file_name) > 100:

        raise ValueError("File name must be between 0 and 100 digits.")

    if not ground_track:
        console.print(
            "[bold red]No ground-track data available to export.[/bold red]"
        )
        return

    file_path = filedialog.asksaveasfilename(
        title="Save Ground Track CSV",
        defaultextension=".csv",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*"),
        ],
        initialfile=file_name,
    )

    # User pressed Cancel
    if not file_path:
        console.print("[dim yellow]CSV export cancelled.[/dim yellow]")
        return

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "timestamp_utc",
                "latitude_deg",
                "longitude_deg",
                "altitude_km",
            ]
        )

        for point in ground_track:
            timestamp = point[0]
            latitude = float(point[1])
            longitude = float(point[2])
            altitude = float(point[3])

            writer.writerow(
                [
                    timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    f"{latitude:.6f}",
                    f"{longitude:.6f}",
                    f"{altitude:.3f}",
                ]
            )

    console.print(
        f"[bold green]Ground track saved to:[/bold green] {file_path}"
    )

def run_pytest_tests() -> None:
    """Run the OrbitOps test suite."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
        ],
        check=False,
    )

    if result.returncode == 0:
        console.print("[bold green]All OrbitOps tests passed.[/bold green]")
    else:
        console.print("[bold red]OrbitOps tests failed.[/bold red]")

