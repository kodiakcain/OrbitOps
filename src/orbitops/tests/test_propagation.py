from datetime import UTC, datetime

import pytest

from orbitops import propagation

# ===========================================================================
# get_teme_cartesian()
# ===========================================================================


def test_get_teme_cartesian_invalid_omm_type():
    with pytest.raises(TypeError):
        propagation.get_teme_cartesian("invalid")


def test_get_teme_cartesian_list_omm():
    with pytest.raises(TypeError):
        propagation.get_teme_cartesian([])


def test_get_teme_cartesian_none_omm():
    with pytest.raises(TypeError):
        propagation.get_teme_cartesian(None)


def test_get_teme_cartesian_returns_position_velocity(monkeypatch):
    expected_position = (
        1000.0,
        2000.0,
        3000.0,
    )

    expected_velocity = (
        1.0,
        2.0,
        3.0,
    )

    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                expected_position,
                expected_velocity,
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.get_teme_cartesian(
        {},
    )

    assert result == (
        expected_position,
        expected_velocity,
    )


def test_get_teme_cartesian_initializes_with_omm_data(
    monkeypatch,
):
    omm_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    received = {}

    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    fake_satellite = FakeSatellite()

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: fake_satellite,
    )

    def fake_initialize(satellite, data):
        received["satellite"] = satellite
        received["data"] = data

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        fake_initialize,
    )

    propagation.get_teme_cartesian(
        omm_data,
    )

    assert received["satellite"] is fake_satellite
    assert received["data"] == omm_data


def test_get_teme_cartesian_calls_sgp4(monkeypatch):
    received = {}

    class FakeSatellite:
        def sgp4(self, jd, fr):
            received["jd"] = jd
            received["fr"] = fr

            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    propagation.get_teme_cartesian(
        {},
    )

    assert "jd" in received
    assert "fr" in received


# ===========================================================================
# get_geographic_position()
# ===========================================================================


def test_get_geographic_position_invalid_omm_type():
    with pytest.raises(TypeError):
        propagation.get_geographic_position("invalid")


def test_get_geographic_position_list_omm():
    with pytest.raises(TypeError):
        propagation.get_geographic_position([])


def test_get_geographic_position_none_omm():
    with pytest.raises(TypeError):
        propagation.get_geographic_position(None)


def test_get_geographic_position_returns_coordinates(
    monkeypatch,
):
    class FakeAngle:
        def __init__(self, degrees):
            self.degrees = degrees

    class FakeElevation:
        def __init__(self, km):
            self.km = km

    class FakeGeographic:
        latitude = FakeAngle(38.1234)
        longitude = FakeAngle(-77.5678)
        elevation = FakeElevation(415.25)

    class FakeSatellite:
        def at(self, time):
            return "fake-position"

    class FakeTimescale:
        def now(self):
            return "fake-time"

    monkeypatch.setattr(
        propagation.load,
        "timescale",
        lambda: FakeTimescale(),
    )

    monkeypatch.setattr(
        propagation.EarthSatellite,
        "from_omm",
        lambda timescale, data: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.wgs84,
        "geographic_position_of",
        lambda position: FakeGeographic(),
    )

    result = propagation.get_geographic_position(
        {},
    )

    assert result == (
        38.1234,
        -77.5678,
        415.25,
    )


def test_get_geographic_position_passes_omm_data(
    monkeypatch,
):
    omm_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    received = {}

    class FakeAngle:
        degrees = 0.0

    class FakeElevation:
        km = 400.0

    class FakeGeographic:
        latitude = FakeAngle()
        longitude = FakeAngle()
        elevation = FakeElevation()

    class FakeSatellite:
        def at(self, time):
            return "fake-position"

    class FakeTimescale:
        def now(self):
            return "fake-time"

    monkeypatch.setattr(
        propagation.load,
        "timescale",
        lambda: FakeTimescale(),
    )

    def fake_from_omm(timescale, data):
        received["timescale"] = timescale
        received["data"] = data

        return FakeSatellite()

    monkeypatch.setattr(
        propagation.EarthSatellite,
        "from_omm",
        fake_from_omm,
    )

    monkeypatch.setattr(
        propagation.wgs84,
        "geographic_position_of",
        lambda position: FakeGeographic(),
    )

    propagation.get_geographic_position(
        omm_data,
    )

    assert received["data"] == omm_data


def test_get_geographic_position_uses_current_time(
    monkeypatch,
):
    received = {}

    class FakeAngle:
        degrees = 0.0

    class FakeElevation:
        km = 400.0

    class FakeGeographic:
        latitude = FakeAngle()
        longitude = FakeAngle()
        elevation = FakeElevation()

    class FakeSatellite:
        def at(self, time):
            received["time"] = time

            return "fake-position"

    class FakeTimescale:
        def now(self):
            return "current-time"

    monkeypatch.setattr(
        propagation.load,
        "timescale",
        lambda: FakeTimescale(),
    )

    monkeypatch.setattr(
        propagation.EarthSatellite,
        "from_omm",
        lambda timescale, data: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.wgs84,
        "geographic_position_of",
        lambda position: FakeGeographic(),
    )

    propagation.get_geographic_position(
        {},
    )

    assert received["time"] == "current-time"


# ===========================================================================
# propogate_future()
# ===========================================================================


def test_propogate_future_invalid_omm_type():
    with pytest.raises(TypeError):
        propagation.propogate_future(
            "invalid",
            60,
        )


def test_propogate_future_invalid_minutes_type():
    with pytest.raises(TypeError):
        propagation.propogate_future(
            {},
            "60",
        )


def test_propogate_future_zero_minutes():
    with pytest.raises(ValueError):
        propagation.propogate_future(
            {},
            0,
        )


def test_propogate_future_negative_minutes():
    with pytest.raises(ValueError):
        propagation.propogate_future(
            {},
            -1,
        )


def test_propogate_future_over_1440_minutes():
    with pytest.raises(ValueError):
        propagation.propogate_future(
            {},
            1441,
        )


def test_propogate_future_one_minute_valid(monkeypatch):
    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        1,
    )

    assert len(result) == 2


def test_propogate_future_1440_minutes_valid(monkeypatch):
    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        1440,
        3600,
    )

    assert len(result) == 25


def test_propogate_future_invalid_step_seconds_type():
    with pytest.raises(TypeError):
        propagation.propogate_future(
            {},
            60,
            "60",
        )


def test_propogate_future_zero_step_seconds():
    with pytest.raises(ValueError):
        propagation.propogate_future(
            {},
            60,
            0,
        )


def test_propogate_future_negative_step_seconds():
    with pytest.raises(ValueError):
        propagation.propogate_future(
            {},
            60,
            -1,
        )


def test_propogate_future_default_step(monkeypatch):
    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        2,
    )

    assert len(result) == 3


def test_propogate_future_custom_step(monkeypatch):
    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        2,
        30,
    )

    assert len(result) == 5


def test_propogate_future_returns_position_velocity(
    monkeypatch,
):
    position = (
        1000.0,
        2000.0,
        3000.0,
    )

    velocity = (
        1.0,
        2.0,
        3.0,
    )

    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                position,
                velocity,
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        1,
        60,
    )

    assert result[0][1] == position
    assert result[0][2] == velocity

    assert result[1][1] == position
    assert result[1][2] == velocity


def test_propogate_future_returns_datetimes(
    monkeypatch,
):
    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        1,
        60,
    )

    assert type(result[0][0]) is datetime
    assert type(result[1][0]) is datetime


def test_propogate_future_timestamps_are_utc(
    monkeypatch,
):
    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        1,
        60,
    )

    assert result[0][0].tzinfo is UTC
    assert result[1][0].tzinfo is UTC


def test_propogate_future_timestamp_spacing(
    monkeypatch,
):
    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        2,
        30,
    )

    assert (
        result[1][0] - result[0][0]
    ).total_seconds() == 30

    assert (
        result[2][0] - result[1][0]
    ).total_seconds() == 30


def test_propogate_future_skips_sgp4_errors(
    monkeypatch,
):
    call_count = 0

    class FakeSatellite:
        def sgp4(self, jd, fr):
            nonlocal call_count

            call_count += 1

            if call_count == 2:
                return (
                    1,
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                )

            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        2,
        60,
    )

    # 3 propagation attempts, but the second has an error.
    assert call_count == 3
    assert len(result) == 2


def test_propogate_future_all_sgp4_errors(
    monkeypatch,
):
    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                1,
                (0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
            )

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: FakeSatellite(),
    )

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        lambda satellite, data: None,
    )

    result = propagation.propogate_future(
        {},
        2,
        60,
    )

    assert result == []


def test_propogate_future_initializes_with_omm_data(
    monkeypatch,
):
    omm_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    received = {}

    class FakeSatellite:
        def sgp4(self, jd, fr):
            return (
                0,
                (1.0, 2.0, 3.0),
                (4.0, 5.0, 6.0),
            )

    fake_satellite = FakeSatellite()

    monkeypatch.setattr(
        propagation,
        "Satrec",
        lambda: fake_satellite,
    )

    def fake_initialize(satellite, data):
        received["satellite"] = satellite
        received["data"] = data

    monkeypatch.setattr(
        propagation.omm,
        "initialize",
        fake_initialize,
    )

    propagation.propogate_future(
        omm_data,
        1,
    )

    assert received["satellite"] is fake_satellite
    assert received["data"] == omm_data