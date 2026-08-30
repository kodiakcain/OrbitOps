import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from platformdirs import user_cache_path
from rich.console import Console

CACHE_DIR: Path = user_cache_path("OrbitOps", ensure_exists=True)
CACHE_LIFETIME = timedelta(hours=2)

console = Console()

def get_cache_path(catalog_number: int) -> Path:
    """Gets the OS-specific cache path for a given CATNR"""

    return CACHE_DIR / f"{catalog_number}.json"

def cache_exists(catalog_number: int) -> bool:
    """Checks if a cache exists for a given CATNR"""

    return get_cache_path(catalog_number).is_file()

def cache_is_fresh(catalog_number: int) -> bool:
    """Checks if the cache is within the 2 hour timeframe"""

    path = get_cache_path(catalog_number)

    if not cache_exists(catalog_number):

        return False

    modified_time = datetime.fromtimestamp(
        path.stat().st_mtime,
        tz=UTC,
    )

    age = datetime.now(UTC) - modified_time

    return age < CACHE_LIFETIME

def save_omm(catalog_number: int, data: dict) -> None:
    """Save the OMM data to the CATNR-specific cache file"""
    path = get_cache_path(catalog_number)

    if not cache_is_fresh(catalog_number):

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

def load_omm(catalog_number: int, data: dict) -> dict:
    """Main use for saving/loading data"""
    path = get_cache_path(catalog_number)

    if cache_exists(catalog_number):

        with open(path, "r", encoding="utf-8") as file:

            return json.load(file)

    else:

        save_omm(catalog_number, data)

        return data

def clear_omm_specific(catalog_number: int) -> None:
    """Clear a specific CATNR cache data"""
    path = get_cache_path(catalog_number)

    if cache_exists(catalog_number):
        path.unlink()

        console.print(f"[bold green]Removed cache data for CATNR {catalog_number}.[/bold green]")

    else:

        console.print("[bold red]CATNR not in cache.[/bold red]")

def clear_omm_all() -> None:
    """Clear the entire cache"""

    file_count = 0

    for file in CACHE_DIR.glob("*.json"):

        if file.is_file():

            file_count += 1

            file.unlink()

    if file_count == 0:

        console.print("[yellow]Cache already empty.[/yellow]")

    else:

        console.print("[bold green]Cache Cleared![/bold green]")

def print_cache() -> None:
    """Print all cache files."""

    file_count = 0

    for file in CACHE_DIR.glob("*.json"):

        if file.is_file():

            file_count += 1

            with open(file, "r", encoding="utf-8") as cache_file:
                print(cache_file.read())

    if file_count == 0:

        console.print("[yellow]Cache is empty.[/yellow]")

def print_cache_specific(catalog_number: int) -> None:
    """Print a specific CATNR cache"""
    path = get_cache_path(catalog_number)

    if cache_exists(catalog_number):

        with open(path, "r", encoding="utf-8") as cache_file:
            print(cache_file.read())

        console.print(f"[bold green]Retrieved cache data for CATNR {catalog_number}.[/bold green]")

    else:

        console.print("[bold red]CATNR not in cache.[/bold red]")
            




    