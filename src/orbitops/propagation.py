from datetime import UTC, datetime, timedelta

from sgp4.api import Satrec, jday
from skyfield.api import EarthSatellite, load, wgs84


def get_teme_cartesian(
    tle_line_1: str, tle_line_2: str
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:

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


def propogate_future(tle1: str, tle2: str, minutes: int, step_seconds: int = 60):
    """Returns timestamped future location data of a given spacecraft"""

    satellite = Satrec.twoline2rv(tle1, tle2)

    start_time = datetime.now(UTC)

    results = []

    total_seconds = minutes * 60

    for seconds in range(0, total_seconds + 1, step_seconds):
        target_time = start_time + timedelta(seconds=seconds)

        jd, fr = jday(
            target_time.year,
            target_time.month,
            target_time.day,
            target_time.hour,
            target_time.minute,
            target_time.second + target_time.microsecond / 1_000_000,
        )

        error, position, velocity = satellite.sgp4(jd, fr)

        if error != 0:
            continue

        results.append(
            (
                target_time,
                position,
                velocity,
            )
        )

    print(results)

    return results
