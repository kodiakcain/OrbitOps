from . import api
import sys

def main():

    catalog_number = int(sys.argv[1])

    sat_data = api.get_sat_info_tle(catalog_number)


    try: 
        sat_name = sat_data[0]
        sat_change = sat_data[1]
        sat_orbit = sat_data[2]

        print(sat_name)
        print(sat_change)
        print(sat_orbit)

    except IndexError as e:

        print(f"Invalid satellite catalog number (CATNR): {e}")
    
if __name__ == "__main__":
    main()