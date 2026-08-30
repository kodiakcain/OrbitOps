import math
import time

import requests
from rich.console import Console

from . import cache, propagation

console = Console()


def get_sat_info_omm(catalog_number: int) -> dict:
    """Returns the satellite name and data in OMM JSON format."""

    if cache.cache_is_fresh(catalog_number):
        return cache.load_omm(catalog_number, {})

    url = "https://celestrak.org/NORAD/elements/gp.php"

    params = {"CATNR": catalog_number, "FORMAT": "JSON"}

    try:
        with console.status("[bold green]Fetching satellite data..."):
            response = requests.get(
                url,
                params=params,
                timeout=20,
            )
            response.raise_for_status()

        data = response.json()

        if not data:
            return {}

        cache.save_omm(catalog_number, data[0])

        return data[0]

    except requests.RequestException as error:
        console.print(
            f"[bold red]Failed to retrieve satellite data: {error}[/bold red]"
        )

        return {}


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

    first_sat_data = get_sat_info_omm(catalog_num1)

    if not first_sat_data:
        console.print(
            f"[bold red]No valid OMM data found for catalog number "
            f"{catalog_num1}.[/bold red]"
        )
        return

    second_sat_data = get_sat_info_omm(catalog_num2)

    if not second_sat_data:
        console.print(
            f"[bold red]No valid OMM data found for catalog number "
            f"{catalog_num2}.[/bold red]"
        )
        return

    teme_first_sat = propagation.get_teme_cartesian(
        first_sat_data
    )[0]

    teme_second_sat = propagation.get_teme_cartesian(
        second_sat_data
    )[0]

    first_sat_name = (
        first_sat_data.get("OBJECT_NAME")
        or str(catalog_num1)
    )

    second_sat_name = (
        second_sat_data.get("OBJECT_NAME")
        or str(catalog_num2)
    )

    print(
        f"The distance between "
        f"{first_sat_name} and "
        f"{second_sat_name} is "
        f"{math.dist(teme_first_sat, teme_second_sat):.3f}km."
    )


def watch(catalog_number: int) -> None:
    """Returns the latitude, longitude, and altitude of a spacecraft."""

    sat_data = get_sat_info_omm(catalog_number)

    if not sat_data:
        console.print(
            f"[bold red]No valid OMM data found for catalog number "
            f"{catalog_number}.[/bold red]"
        )
        return

    sat_name = (
        sat_data.get("OBJECT_NAME")
        or str(catalog_number)
    )

    console.print("[dim yellow]Press 'Ctrl+C' to stop watching.[/dim yellow]")

    while True:
        latitude, longitude, altitude = propagation.get_geographic_position(
            sat_data,
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