import sys
from datetime import UTC, datetime, timedelta

from rich.console import Console
from rich.table import Table

from . import api, cache, etc, propagation, visualization

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
    "cache",
    "tests",
    "visualize"
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

        if command == "tests":

            etc.run_pytest_tests()
            return

        # Caching command
        if command == "cache":

            if len(sys.argv) < 3:
            
                console.print("[bold red]Missing cache command.[/bold red]")
                console.print("[dim yellow]Usage: orbitops cache <info|clear> [CATNR][/dim yellow]")

                return

            if sys.argv[2] not in ["info", "clear"]:

                console.print(f"[bold red]{sys.argv[2]} is an invalid cache command.[/bold red]")

                return

            if str(sys.argv[2]) == "info" and len(sys.argv) == 3:

                cache.print_cache()

                return

            if str(sys.argv[2]) == "clear" and len(sys.argv) == 3:

                cache.clear_omm_all()

                return

            if str(sys.argv[2]) == "clear" and len(sys.argv) == 4:
            
                cache.clear_omm_specific(int(sys.argv[3]))

                return

            if str(sys.argv[2]) == "info" and len(sys.argv) == 4:
            
                cache.print_cache_specific(int(sys.argv[3]))

                return

        if command == "visualize":

            if len(sys.argv) < 4:
                console.print(
                    "[bold red]Catalog number and duration are required.[/bold red]"
                )
                console.print(
                    "[dim yellow]Usage: orbitops visualize <CATNR> <MINUTES>[/dim yellow]"
                )
                return

            try:
                catalog_number = int(sys.argv[2])
                minutes = int(sys.argv[3])

            except ValueError:
                console.print(
                    "[bold red]Catalog number and duration must be integers.[/bold red]"
                )
                return

            if minutes < 1 or minutes > 1440:
                console.print(
                    "[bold red]Visualization duration must be in range 1-1440 minutes.[/bold red]"
                )
                return

            sat_data = api.get_sat_info_omm(catalog_number)

            if not sat_data:
                console.print(
                    f"[dim yellow]No satellite found with catalog number "
                    f"{catalog_number}.[/dim yellow]"
                )
                return

            sat_name = (
                sat_data.get("OBJECT_NAME")
                or str(catalog_number)
            )

            start_time = datetime.now(UTC)

            times = []

            for minute in range(minutes + 1):
                times.append(
                    start_time + timedelta(minutes=minute)
                )

            ground_track = etc.generate_ground_track(
                sat_data,
                times,
            )

            figure = visualization.generate_3d_globe(
                ground_track,
                sat_name,
                catalog_number,
            )

            visualization.save_and_open_globe(figure, f"{sat_name}-visualization-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html")

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

            sat_data = api.get_sat_info_omm(catalog_number)

            if not sat_data:
                console.print(
                    f"[dim yellow]No satellite found with catalog number "
                    f"{catalog_number}. [/dim yellow]"
                )
                return

            sat_name = (
                sat_data.get("OBJECT_NAME")
                or str(catalog_number)
            )

        if command == "teme":
            position, velocity = propagation.get_teme_cartesian(sat_data)

            table = Table(title=f"{sat_name.strip()} TEME Cartesian State", show_lines=True)

            table.add_column("Position Component", style="green")
            table.add_column("Position", style="cyan")
            table.add_column("Velocity", style="magenta")

            table.add_row("X", f"{position[0]:10.2f} km", f"{velocity[0]:10.3f} km/s")
            table.add_row("Y", f"{position[1]:10.2f} km", f"{velocity[1]:10.3f} km/s")
            table.add_row("Z", f"{position[2]:10.2f} km", f"{velocity[2]:10.3f} km/s")

            console.print(table)

        if command == "position":

            latitude, longitude, altitude = propagation.get_geographic_position(
                sat_data,
            )

            table = Table(title=f"{sat_name.strip()}'s Position", show_lines=True)
            table.add_column("Latitude", style="cyan")
            table.add_column("Longitude", style="magenta")
            table.add_column("Altitude", style="green")

            table.add_row(f"{latitude:.4f}°", f"{longitude:.4f}°", f"{altitude:.2f} km")

            console.print(table)

        if command == "info":
            data = api.get_satcat_data(catalog_number)

            if not data:
                console.print(
                    f"[dim yellow]No satellite found with catalog number "
                    f"{catalog_number}. [/dim yellow]"
                )
                return

            table = Table(title=f"{sat_name.strip()} Information", show_lines=True)

            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            for key, value in data.items():
                table.add_row(str(key), str(value))

            console.print(table)

        if command == "search":
            results = api.search_by_name(sys.argv[2])

            if not results:
                console.print(
                    f"[dim yellow]No satellites found matching "
                    f"'{sys.argv[2]}'.[/dim yellow]"
                )
                return

            data = results[0]

            table=Table(title=f"Results for Search {str(sys.argv[2]).strip()}", show_lines=True)

            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            for key, value in data.items():
                table.add_row(str(key), str(value))

            console.print(table)

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

            ground_track = etc.generate_ground_track(sat_data, times)

            etc.plot_ground_track(
                ground_track,
                sat_name,
                minutes,
                sat_data,
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