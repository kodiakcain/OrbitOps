from . import api
from . import propogation
import sys
import math

def main() -> None:
    """Main CLI tool, accepts commands."""

    try:

        command = sys.argv[1]

        if str(sys.argv[1]) != "search" and str(sys.argv[1]) != "distance":

            catalog_number = int(sys.argv[2])

            sat_data = api.get_sat_info_tle(catalog_number)

            sat_name, tle_line1, tle_line2 = sat_data 

        if str(command) == "teme":

            position, velocity = propogation.get_teme_cartesian(tle_line1, tle_line2)

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

        if str(command) == "position":

            print(f"\nGeographic position of {sat_name}")
            print("--------------------")

            latitude, longitude, altitude = propogation.get_geographic_position(
                tle_line1,
                tle_line2,
            )

            print(f"Latitude:  {latitude:.4f}°")
            print(f"Longitude: {longitude:.4f}°")
            print(f"Altitude:  {altitude:.2f} km")

        if str(command) == "info":

            data = api.get_satcat_data(catalog_number)

            for key, value in data.items():
                print(f"{key}: {value}")

        if str(command) == "search":

            data = api.search_by_name(sys.argv[2])[0]

            for key, value in data.items():

                print(f"{key}: {value}")

        if str(command) == "distance":

            api.get_distance_sats(int(sys.argv[2]), int(sys.argv[3]))

        if str(command) == "watch": 

            api.watch(catalog_number)

    except IndexError as e:

        print(f"Invalid satellite catalog number (CATNR): {e}")
    
if __name__ == "__main__":
    main()