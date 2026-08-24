import sys
from datetime import UTC, datetime, timedelta

from rich.console import Console

from . import api, etc, propagation

console = Console()

VALID_COMMANDS = (
    "help",
    "--help",
    "-h",
    "teme",
    "position",
    "info",
    "search",
    "distance",
    "watch",
    "gtrack",
)


def main() -> None:
    """Main CLI tool, accepts commands."""

    try:
        # No command entered
        if len(sys.argv) == 1:
            etc.print_help_menu()
            return

        command = sys.argv[1]

        # Help command
        if command in ("help", "--help", "-h"):
            etc.print_help_menu()
            return

        # Invalid command
        if command not in VALID_COMMANDS:
            console.print(f"[bold red]Invalid command: {command}[/bold red]")
            console.print(
                "[dim yellow]Use 'orbitops help' to view available commands.[/dim yellow]"
            )
            return

        # Search requires a name
        if command == "search" and len(sys.argv) < 3:
            console.print("[bold red]Missing satellite name.[/bold red]")
            console.print("[dim yellow]Usage: orbitops search <name>[/dim yellow]")
            return

        # Distance requires two catalog numbers
        if command == "distance" and len(sys.argv) < 4:
            console.print(
                "[bold red]Two satellite catalog numbers are required.[/bold red]"
            )
            console.print(
                "[dim yellow]Usage: orbitops distance <CATNR1> <CATNR2>[/dim yellow]"
            )
            return

        # All remaining commands require one catalog number
        if command not in ("search", "distance"):
            if len(sys.argv) < 3:
                console.print("[bold red]Missing satellite catalog number.[/bold red]")
                console.print(
                    f"[dim yellow]Usage: orbitops {command} <CATNR>[/dim yellow]"
                )
                return

            try:
                catalog_number = int(sys.argv[2])

            except ValueError:
                console.print(
                    "[bold red]Satellite catalog number must be an integer.[/bold red]"
                )
                return

            sat_data = api.get_sat_info_tle(catalog_number)

            if not sat_data:
                console.print(
                    f"[dim yellow]No satellite found with catalog number "
                    f"{catalog_number}. [/dim yellow]"
                )
                return

            sat_name, tle_line1, tle_line2 = sat_data

        if command == "teme":
            position, velocity = propagation.get_teme_cartesian(tle_line1, tle_line2)

            print(f"\nTEME Cartesian State of {sat_name}")
            print("--------------------")

            print("Position:")
            print(f"  X: {position[0]:10.2f} km")
            print(f"  Y: {position[1]:10.2f} km")
            print(f"  Z: {position[2]:10.2f} km")

            print("Velocity:")
            print(f"  X: {velocity[0]:10.3f} km/s")
            print(f"  Y: {velocity[1]:10.3f} km/s")
            print(f"  Z: {velocity[2]:10.3f} km/s")

        if command == "position":
            print(f"\nGeographic position of {sat_name}")
            print("--------------------")

            latitude, longitude, altitude = propagation.get_geographic_position(
                tle_line1,
                tle_line2,
            )

            print(f"Latitude:  {latitude:.4f}°")
            print(f"Longitude: {longitude:.4f}°")
            print(f"Altitude:  {altitude:.2f} km")

        if command == "info":
            data = api.get_satcat_data(catalog_number)

            if not data:
                console.print(
                    f"[dim yellow]No satellite found with catalog number "
                    f"{catalog_number}. [/dim yellow]"
                )
                return

            for key, value in data.items():
                print(f"{key}: {value}")

        if command == "search":
            results = api.search_by_name(sys.argv[2])

            if not results:
                console.print(
                    f"[dim yellow]No satellites found matching "
                    f"'{sys.argv[2]}'.[/dim yellow]"
                )
                return

            data = results[0]

            for key, value in data.items():
                print(f"{key}: {value}")

        if command == "distance":
            try:
                catalog_number_1 = int(sys.argv[2])
                catalog_number_2 = int(sys.argv[3])

            except ValueError:
                console.print(
                    "[bold red]Satellite catalog numbers must be integers.[/bold red]"
                )
                return

            api.get_distance_sats(catalog_number_1, catalog_number_2)

        if command == "watch":
            api.watch(catalog_number)

        if command == "gtrack" and len(sys.argv) < 4:
            console.print(
                "[bold red]Catalog number and duration are required.[/bold red]"
            )
            console.print(
                "[dim yellow]Usage: orbitops gtrack <CATNR> <MINUTES>[/dim yellow]"
            )
            return
        
        if command == "gtrack":

            try:
                minutes = int(sys.argv[3])
            except ValueError:
                console.print("[bold red]Ground-track duration must be an integer in range 1-1440.[/bold red]")
                return

            start_time = datetime.now(UTC)

            times = []

            for minute in range(minutes + 1):
                times.append(start_time + timedelta(minutes=minute))

            ground_track = etc.generate_ground_track(tle_line1, tle_line2, times)

            etc.plot_ground_track(
                ground_track,
                sat_name,
                minutes,
                tle_line1,
                tle_line2,
            )

            if len(sys.argv) > 4 and sys.argv[4] == "--csv":

                etc.save_ground_track_csv(ground_track, f"{sat_name.strip()}-{datetime.now():%Y-%m-%d-%H-%M}.csv")

    except IndexError as error:
        console.print(
            f"[bold red]Invalid satellite catalog number (CATNR): {error}[/bold red]"
        )

    except KeyboardInterrupt:
        console.print("[dim yellow]\nOrbitOps stopped.[/dim yellow]")

    except Exception as error:
        console.print(f"[bold red]OrbitOps error: {error}[/bold red]")


if __name__ == "__main__":
    main()
