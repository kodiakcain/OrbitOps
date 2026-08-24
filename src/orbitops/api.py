import math
import time

import requests
from rich.console import Console

from . import propagation

console = Console()


def get_sat_info_tle(catalog_number: int) -> list[str]:
    """Returns the satellite name and data in TLE format."""

    returnArr = []

    url = "https://celestrak.org/NORAD/elements/gp.php"

    params = {"CATNR": catalog_number, "FORMAT": "TLE"}

    try:
        with console.status("[bold green]Fetching satellite data..."):
            response = requests.get(
                url,
                params=params,
                timeout=20,
            )
            response.raise_for_status()

        data = response.text.splitlines()

        if len(data) < 3:
            return []

        for line in data:
            returnArr.append(line)

        return returnArr

    except requests.RequestException as error:
        console.print(
            f"[bold red]Failed to retrieve satellite data: {error}[/bold red]"
        )

        return []


def get_satcat_data(catalog_number: int) -> dict:
    """Returns information about a given spacecraft."""

    url = "https://celestrak.org/satcat/records.php"

    params = {"CATNR": catalog_number, "FORMAT": "JSON"}

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20,
        )
        response.raise_for_status()

        data = response.json()

        if not data:
            return {}

        return data[0]

    except requests.RequestException as error:
        console.print(
            f"[bold red]Failed to retrieve satellite data: {error}[/bold red]"
        )

        return {}


def search_by_name(name: str) -> list[dict]:
    """Searches Celestrack by name, returns most relevant results."""

    url = "https://celestrak.org/satcat/records.php"

    params = {
        "NAME": name,
        "FORMAT": "JSON",
    }

    try:
        with console.status(f"[bold green]Searching for {name}..."):
            response = requests.get(
                url,
                params=params,
                timeout=20,
            )
            response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        console.print(
            f"[bold red]Failed to retrieve satellite data: {error}[/bold red]"
        )

        return []


def get_distance_sats(catalog_num1: int, catalog_num2: int) -> None:
    """Returns the 3D Euclidean distance between two spacecraft."""

    url = "https://celestrak.org/NORAD/elements/gp.php"

    params = {"CATNR": catalog_num1, "FORMAT": "TLE"}

    params2 = {"CATNR": catalog_num2, "FORMAT": "TLE"}

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20,
        )
        response.raise_for_status()

        first_sat_data = response.text.splitlines()

        if len(first_sat_data) < 3:
            console.print(
                f"[bold red]No valid TLE found for catalog number "
                f"{catalog_num1}.[/bold red]"
            )
            return

        tle_1_first_sat = first_sat_data[1]
        tle_2_first_sat = first_sat_data[2]

        teme_first_sat = propagation.get_teme_cartesian(
            tle_1_first_sat, tle_2_first_sat
        )[0]

        response2 = requests.get(
            url,
            params=params2,
            timeout=20,
        )
        response2.raise_for_status()

        second_sat_data = response2.text.splitlines()

        if len(second_sat_data) < 3:
            console.print(
                f"[bold red]No valid TLE found for catalog number "
                f"{catalog_num2}.[/bold red]"
            )
            return

        tle_1_second_sat = second_sat_data[1]
        tle_2_second_sat = second_sat_data[2]

        teme_second_sat = propagation.get_teme_cartesian(
            tle_1_second_sat, tle_2_second_sat
        )[0]

        print(
            f"The distance between "
            f"{first_sat_data[0].strip()} and "
            f"{second_sat_data[0].strip()} is "
            f"{math.dist(teme_first_sat, teme_second_sat):.3f}km."
        )

    except requests.RequestException as error:
        console.print(
            f"[bold red]Failed to retrieve satellite data: {error}[/bold red]"
        )


def watch(catalog_number: int) -> None:
    """Returns the latitude, longitude, and altitude of a spacecraft."""

    sat_data = get_sat_info_tle(catalog_number)

    if len(sat_data) < 3:
        console.print(
            f"[bold red]No valid TLE found for catalog number "
            f"{catalog_number}.[/bold red]"
        )
        return

    sat_name, tle_line1, tle_line2 = sat_data

    console.print("[dim yellow]Press 'Ctrl+C' to stop watching.[/dim yellow]")

    while True:
        latitude, longitude, altitude = propagation.get_geographic_position(
            tle_line1,
            tle_line2,
        )

        print(
            f"\r{sat_name} | "
            f"Lat: {latitude:.4f}° | "
            f"Lon: {longitude:.4f}° | "
            f"Alt: {altitude:.2f} km",
            end="",
            flush=True,
        )

        time.sleep(1)
