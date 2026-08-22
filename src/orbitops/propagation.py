from datetime import UTC, datetime

from sgp4.api import Satrec, jday
from skyfield.api import EarthSatellite, load, wgs84


def get_teme_cartesian(tle_line_1: str, tle_line_2: str) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float]
]:

    satellite = Satrec.twoline2rv(tle_line_1, tle_line_2)
    
    now = datetime.now(UTC)

    jd, fr = jday(
    now.year,
    now.month,
    now.day,
    now.hour,
    now.minute,
    now.second + now.microsecond / 1_000_000,
    )

    error, position, velocity = satellite.sgp4(jd, fr)

    return (position, velocity)

def get_geographic_position(
    tle_line_1: str,
    tle_line_2: str,
) -> tuple[float, float, float]:

    timescale = load.timescale()
    current_time = timescale.now()

    satellite = EarthSatellite(
        tle_line_1,
        tle_line_2,
        ts=timescale,
    )

    position = satellite.at(current_time)

    geographic = wgs84.geographic_position_of(position)

    latitude = geographic.latitude.degrees
    longitude = geographic.longitude.degrees
    altitude = geographic.elevation.km

    return latitude, longitude, altitude