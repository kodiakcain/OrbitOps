import sys

from . import api, etc, propagation

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
            print(f"Invalid command: {command}")
            print("Use 'orbitops help' to view available commands.")
            return

        # Search requires a name
        if command == "search" and len(sys.argv) < 3:
            print("Missing satellite name.")
            print("Usage: orbitops search <name>")
            return

        # Distance requires two catalog numbers
        if command == "distance" and len(sys.argv) < 4:
            print("Two satellite catalog numbers are required.")
            print("Usage: orbitops distance <CATNR1> <CATNR2>")
            return

        # All remaining commands require one catalog number
        if command not in ("search", "distance"):

            if len(sys.argv) < 3:
                print("Missing satellite catalog number.")
                print(f"Usage: orbitops {command} <CATNR>")
                return

            try:
                catalog_number = int(sys.argv[2])

            except ValueError:
                print("Satellite catalog number must be an integer.")
                return

            sat_data = api.get_sat_info_tle(catalog_number)

            if not sat_data:
                print(
                    f"No satellite found with catalog number "
                    f"{catalog_number}."
                )
                return

            sat_name, tle_line1, tle_line2 = sat_data

        if command == "teme":

            position, velocity = propagation.get_teme_cartesian(
                tle_line1,
                tle_line2
            )

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

            latitude, longitude, altitude = (
                propagation.get_geographic_position(
                    tle_line1,
                    tle_line2,
                )
            )

            print(f"Latitude:  {latitude:.4f}°")
            print(f"Longitude: {longitude:.4f}°")
            print(f"Altitude:  {altitude:.2f} km")

        if command == "info":

            data = api.get_satcat_data(catalog_number)

            if not data:
                print(
                    f"No satellite catalog information found for "
                    f"{catalog_number}."
                )
                return

            for key, value in data.items():
                print(f"{key}: {value}")

        if command == "search":

            results = api.search_by_name(sys.argv[2])

            if not results:
                print(
                    f"No satellites found matching "
                    f"'{sys.argv[2]}'."
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
                print("Satellite catalog numbers must be integers.")
                return

            api.get_distance_sats(
                catalog_number_1,
                catalog_number_2
            )

        if command == "watch":

            api.watch(catalog_number)

    except IndexError as error:
        print(f"Invalid satellite catalog number (CATNR): {error}")

    except KeyboardInterrupt:
        print("\nOrbitOps stopped.")

    except Exception as error:
        print(f"OrbitOps error: {error}")


if __name__ == "__main__":
    main()