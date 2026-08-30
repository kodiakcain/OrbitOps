import csv
from datetime import UTC, datetime, timedelta

import pytest

from orbitops import etc

# ===========================================================================
# Fake Skyfield objects
# ===========================================================================


class FakeAngle:
    def __init__(self, degrees):
        self.degrees = degrees


class FakeElevation:
    def __init__(self, km):
        self.km = km


class FakeGeographic:
    def __init__(self, latitude, longitude, altitude):
        self.latitude = FakeAngle(latitude)
        self.longitude = FakeAngle(longitude)
        self.elevation = FakeElevation(altitude)


class FakePosition:
    pass


class FakeSatellite:
    def at(self, time):
        return FakePosition()


class FakeTimescale:
    def from_datetime(self, timestamp):
        return timestamp


# ===========================================================================
# print_help_menu()
# ===========================================================================


def test_print_help_menu_title(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "OrbitOps Help Menu" in captured.out


def test_print_help_menu_position(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "position <CATNR>" in captured.out


def test_print_help_menu_teme(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "teme <CATNR>" in captured.out


def test_print_help_menu_info(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "info <CATNR>" in captured.out


def test_print_help_menu_search(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "search <name>" in captured.out


def test_print_help_menu_distance(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "distance <CATNR1> <CATNR2>" in captured.out


def test_print_help_menu_watch(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "watch <CATNR>" in captured.out


def test_print_help_menu_gtrack(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "gtrack <CATNR> <minutes> [--csv]" in captured.out


def test_print_help_menu_cache_info(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "cache info" in captured.out


def test_print_help_menu_cache_info_specific(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "cache info <CATNR>" in captured.out


def test_print_help_menu_cache_clear(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "cache clear" in captured.out


def test_print_help_menu_cache_clear_specific(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "cache clear <CATNR>" in captured.out


def test_print_help_menu_help(capsys):
    etc.print_help_menu()

    captured = capsys.readouterr()

    assert "help" in captured.out


# ===========================================================================
# generate_ground_track()
# ===========================================================================


def test_generate_ground_track_invalid_omm_type():
    with pytest.raises(TypeError):
        etc.generate_ground_track(
            "not a dictionary",
            [],
        )


def test_generate_ground_track_invalid_times_type():
    with pytest.raises(TypeError):
        etc.generate_ground_track(
            {},
            "not a list",
        )


def test_generate_ground_track_empty_times(monkeypatch):
    monkeypatch.setattr(
        etc.load,
        "timescale",
        lambda: FakeTimescale(),
    )

    monkeypatch.setattr(
        etc.EarthSatellite,
        "from_omm",
        lambda timescale, omm_data: FakeSatellite(),
    )

    result = etc.generate_ground_track(
        {},
        [],
    )

    assert result == []


def test_generate_ground_track_returns_correct_points(monkeypatch):
    timescale = FakeTimescale()

    monkeypatch.setattr(
        etc.load,
        "timescale",
        lambda: timescale,
    )

    monkeypatch.setattr(
        etc.EarthSatellite,
        "from_omm",
        lambda timescale, omm_data: FakeSatellite(),
    )

    monkeypatch.setattr(
        etc.wgs84,
        "geographic_position_of",
        lambda position: FakeGeographic(
            38.123456,
            -77.654321,
            415.123,
        ),
    )

    start = datetime(
        2026,
        8,
        30,
        12,
        0,
        tzinfo=UTC,
    )

    times = [
        start,
        start + timedelta(minutes=1),
    ]

    result = etc.generate_ground_track(
        {"OBJECT_NAME": "TEST"},
        times,
    )

    assert len(result) == 2

    assert result[0] == (
        times[0],
        38.123456,
        -77.654321,
        415.123,
    )

    assert result[1] == (
        times[1],
        38.123456,
        -77.654321,
        415.123,
    )


def test_generate_ground_track_preserves_timestamps(monkeypatch):
    monkeypatch.setattr(
        etc.load,
        "timescale",
        lambda: FakeTimescale(),
    )

    monkeypatch.setattr(
        etc.EarthSatellite,
        "from_omm",
        lambda timescale, omm_data: FakeSatellite(),
    )

    monkeypatch.setattr(
        etc.wgs84,
        "geographic_position_of",
        lambda position: FakeGeographic(
            10.0,
            20.0,
            400.0,
        ),
    )

    start = datetime(
        2026,
        8,
        30,
        12,
        0,
        tzinfo=UTC,
    )

    times = [
        start,
        start + timedelta(minutes=1),
        start + timedelta(minutes=2),
    ]

    result = etc.generate_ground_track(
        {},
        times,
    )

    assert result[0][0] == times[0]
    assert result[1][0] == times[1]
    assert result[2][0] == times[2]


def test_generate_ground_track_calls_from_datetime(monkeypatch):
    received = []

    class TrackingTimescale:
        def from_datetime(self, timestamp):
            received.append(timestamp)
            return timestamp

    monkeypatch.setattr(
        etc.load,
        "timescale",
        lambda: TrackingTimescale(),
    )

    monkeypatch.setattr(
        etc.EarthSatellite,
        "from_omm",
        lambda timescale, omm_data: FakeSatellite(),
    )

    monkeypatch.setattr(
        etc.wgs84,
        "geographic_position_of",
        lambda position: FakeGeographic(
            10.0,
            20.0,
            400.0,
        ),
    )

    timestamp = datetime(
        2026,
        8,
        30,
        12,
        0,
        tzinfo=UTC,
    )

    etc.generate_ground_track(
        {},
        [timestamp],
    )

    assert received == [timestamp]


def test_generate_ground_track_passes_omm_to_skyfield(monkeypatch):
    received = {}

    omm_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    monkeypatch.setattr(
        etc.load,
        "timescale",
        lambda: FakeTimescale(),
    )

    def fake_from_omm(timescale, data):
        received["data"] = data
        return FakeSatellite()

    monkeypatch.setattr(
        etc.EarthSatellite,
        "from_omm",
        fake_from_omm,
    )

    etc.generate_ground_track(
        omm_data,
        [],
    )

    assert received["data"] == omm_data


# ===========================================================================
# plot_ground_track() validation
# ===========================================================================


def test_plot_ground_track_invalid_ground_track_type():
    with pytest.raises(TypeError):
        etc.plot_ground_track(
            "invalid",
            "ISS",
            60,
            {},
        )


def test_plot_ground_track_invalid_sat_name_type():
    with pytest.raises(TypeError):
        etc.plot_ground_track(
            [],
            25544,
            60,
            {},
        )


def test_plot_ground_track_invalid_minutes_type():
    with pytest.raises(TypeError):
        etc.plot_ground_track(
            [],
            "ISS",
            "60",
            {},
        )


def test_plot_ground_track_invalid_omm_type():
    with pytest.raises(TypeError):
        etc.plot_ground_track(
            [],
            "ISS",
            60,
            "invalid",
        )


def test_plot_ground_track_empty_sat_name():
    with pytest.raises(ValueError):
        etc.plot_ground_track(
            [],
            "",
            60,
            {},
        )


def test_plot_ground_track_name_over_30_characters():
    with pytest.raises(ValueError):
        etc.plot_ground_track(
            [],
            "A" * 31,
            60,
            {},
        )


def test_plot_ground_track_zero_minutes():
    with pytest.raises(ValueError):
        etc.plot_ground_track(
            [],
            "ISS",
            0,
            {},
        )


def test_plot_ground_track_negative_minutes():
    with pytest.raises(ValueError):
        etc.plot_ground_track(
            [],
            "ISS",
            -1,
            {},
        )


def test_plot_ground_track_over_1440_minutes():
    with pytest.raises(ValueError):
        etc.plot_ground_track(
            [],
            "ISS",
            1441,
            {},
        )


def test_plot_ground_track_empty_track(monkeypatch, capsys):
    etc.plot_ground_track(
        [],
        "ISS",
        60,
        {},
    )

    captured = capsys.readouterr()

    assert "No ground track found" in captured.out


# ===========================================================================
# save_ground_track_csv() validation
# ===========================================================================


def test_save_ground_track_csv_invalid_ground_track_type():
    with pytest.raises(TypeError):
        etc.save_ground_track_csv(
            "invalid",
            "track.csv",
        )


def test_save_ground_track_csv_invalid_filename_type():
    with pytest.raises(TypeError):
        etc.save_ground_track_csv(
            [],
            12345,
        )


def test_save_ground_track_csv_empty_filename():
    with pytest.raises(ValueError):
        etc.save_ground_track_csv(
            [],
            "",
        )


def test_save_ground_track_csv_filename_over_100_characters():
    with pytest.raises(ValueError):
        etc.save_ground_track_csv(
            [],
            "A" * 101,
        )


def test_save_ground_track_csv_100_character_filename(monkeypatch):
    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: "",
    )

    etc.save_ground_track_csv(
        [
            (
                datetime(
                    2026,
                    8,
                    30,
                    tzinfo=UTC,
                ),
                10.0,
                20.0,
                400.0,
            )
        ],
        "A" * 100,
    )


def test_save_ground_track_csv_empty_track(capsys):
    etc.save_ground_track_csv(
        [],
        "track.csv",
    )

    captured = capsys.readouterr()

    assert "No ground-track data available to export." in captured.out


def test_save_ground_track_csv_empty_track_does_not_open_dialog(
    monkeypatch,
):
    called = []

    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: called.append(True),
    )

    etc.save_ground_track_csv(
        [],
        "track.csv",
    )

    assert called == []


# ===========================================================================
# save_ground_track_csv() dialog
# ===========================================================================


def test_save_ground_track_csv_dialog_options(
    monkeypatch,
):
    dialog_data = {}

    def fake_dialog(**kwargs):
        dialog_data.update(kwargs)
        return ""

    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        fake_dialog,
    )

    ground_track = [
        (
            datetime(
                2026,
                8,
                30,
                12,
                0,
                tzinfo=UTC,
            ),
            10.0,
            20.0,
            400.0,
        )
    ]

    etc.save_ground_track_csv(
        ground_track,
        "ISS-track.csv",
    )

    assert dialog_data["title"] == "Save Ground Track CSV"
    assert dialog_data["defaultextension"] == ".csv"
    assert dialog_data["initialfile"] == "ISS-track.csv"

    assert (
        "CSV files",
        "*.csv",
    ) in dialog_data["filetypes"]


def test_save_ground_track_csv_cancel(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: "",
    )

    ground_track = [
        (
            datetime(
                2026,
                8,
                30,
                12,
                0,
                tzinfo=UTC,
            ),
            10.0,
            20.0,
            400.0,
        )
    ]

    etc.save_ground_track_csv(
        ground_track,
        "track.csv",
    )

    captured = capsys.readouterr()

    assert "CSV export cancelled." in captured.out


# ===========================================================================
# save_ground_track_csv() actual file output
# ===========================================================================


def test_save_ground_track_csv_creates_file(
    monkeypatch,
    tmp_path,
):
    file_path = tmp_path / "track.csv"

    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: str(file_path),
    )

    ground_track = [
        (
            datetime(
                2026,
                8,
                30,
                12,
                0,
                tzinfo=UTC,
            ),
            10.0,
            20.0,
            400.0,
        )
    ]

    etc.save_ground_track_csv(
        ground_track,
        "track.csv",
    )

    assert file_path.is_file()


def test_save_ground_track_csv_correct_header(
    monkeypatch,
    tmp_path,
):
    file_path = tmp_path / "track.csv"

    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: str(file_path),
    )

    ground_track = [
        (
            datetime(
                2026,
                8,
                30,
                12,
                0,
                tzinfo=UTC,
            ),
            10.0,
            20.0,
            400.0,
        )
    ]

    etc.save_ground_track_csv(
        ground_track,
        "track.csv",
    )

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.reader(file))

    assert rows[0] == [
        "timestamp_utc",
        "latitude_deg",
        "longitude_deg",
        "altitude_km",
    ]


def test_save_ground_track_csv_correct_data(
    monkeypatch,
    tmp_path,
):
    file_path = tmp_path / "track.csv"

    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: str(file_path),
    )

    timestamp = datetime(
        2026,
        8,
        30,
        12,
        34,
        56,
        tzinfo=UTC,
    )

    ground_track = [
        (
            timestamp,
            38.1234567,
            -77.7654321,
            415.12345,
        )
    ]

    etc.save_ground_track_csv(
        ground_track,
        "track.csv",
    )

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.reader(file))

    assert rows[1] == [
        "2026-08-30T12:34:56Z",
        "38.123457",
        "-77.765432",
        "415.123",
    ]


def test_save_ground_track_csv_multiple_rows(
    monkeypatch,
    tmp_path,
):
    file_path = tmp_path / "track.csv"

    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: str(file_path),
    )

    start = datetime(
        2026,
        8,
        30,
        12,
        0,
        tzinfo=UTC,
    )

    ground_track = [
        (
            start,
            10.0,
            20.0,
            400.0,
        ),
        (
            start + timedelta(minutes=1),
            11.0,
            21.0,
            401.0,
        ),
        (
            start + timedelta(minutes=2),
            12.0,
            22.0,
            402.0,
        ),
    ]

    etc.save_ground_track_csv(
        ground_track,
        "track.csv",
    )

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.reader(file))

    # Header + 3 data rows
    assert len(rows) == 4

    assert rows[1] == [
        "2026-08-30T12:00:00Z",
        "10.000000",
        "20.000000",
        "400.000",
    ]

    assert rows[2] == [
        "2026-08-30T12:01:00Z",
        "11.000000",
        "21.000000",
        "401.000",
    ]

    assert rows[3] == [
        "2026-08-30T12:02:00Z",
        "12.000000",
        "22.000000",
        "402.000",
    ]


def test_save_ground_track_csv_converts_numeric_values(
    monkeypatch,
    tmp_path,
):
    file_path = tmp_path / "track.csv"

    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: str(file_path),
    )

    ground_track = [
        (
            datetime(
                2026,
                8,
                30,
                12,
                0,
                tzinfo=UTC,
            ),
            "38.5",
            "-77.5",
            "415.5",
        )
    ]

    etc.save_ground_track_csv(
        ground_track,
        "track.csv",
    )

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.reader(file))

    assert rows[1] == [
        "2026-08-30T12:00:00Z",
        "38.500000",
        "-77.500000",
        "415.500",
    ]


def test_save_ground_track_csv_success_message(
    monkeypatch,
    tmp_path,
    capsys,
):
    file_path = tmp_path / "track.csv"

    monkeypatch.setattr(
        etc.filedialog,
        "asksaveasfilename",
        lambda **kwargs: str(file_path),
    )

    ground_track = [
        (
            datetime(
                2026,
                8,
                30,
                12,
                0,
                tzinfo=UTC,
            ),
            10.0,
            20.0,
            400.0,
        )
    ]

    etc.save_ground_track_csv(
        ground_track,
        "track.csv",
    )

    captured = capsys.readouterr()

    output = captured.out.replace("\n", "")

    assert "Ground track saved to:" in captured.out
    assert str(file_path) in output