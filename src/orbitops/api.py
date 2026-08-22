import requests
from typing import List

def get_sat_info_tle(catalog_number: int) -> List[str]:

    returnArr = []

    url = "https://celestrak.org/NORAD/elements/gp.php"

    params = {
        "CATNR": catalog_number,
        "FORMAT": "TLE"
    }

    try:
    
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.text.splitlines()

        for line in data:

            returnArr.append(line)

        return returnArr

    except requests.RequestException as error:

        print(f"Failed to retrieve satellite data: {error}")

        return []



