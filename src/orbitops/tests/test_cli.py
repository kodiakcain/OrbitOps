from datetime import timedelta

import pytest

from orbitops import cli

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

def test_main_no_command(monkeypatch):
    called = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops"],
    )

    monkeypatch.setattr(
        cli.etc,
        "print_help_menu",
        lambda: called.append(True),
    )

    cli.main()

    assert called == [True]


@pytest.mark.parametrize(
    "command",
    ["help", "--help", "-h"],
)
def test_main_help_commands(monkeypatch, command):
    called = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", command],
    )

    monkeypatch.setattr(
        cli.etc,
        "print_help_menu",
        lambda: called.append(True),
    )

    cli.main()

    assert called == [True]


# ---------------------------------------------------------------------------
# Invalid command
# ---------------------------------------------------------------------------

def test_main_invalid_command(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "invalid"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Invalid command: invalid" in captured.out
    assert "orbitops help" in captured.out


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def test_main_cache_missing_subcommand(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "cache"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Missing cache command." in captured.out
    assert "orbitops cache <info|clear> [CATNR]" in captured.out


def test_main_cache_invalid_subcommand(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "cache", "invalid"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "invalid is an invalid cache command." in captured.out


def test_main_cache_info_all(monkeypatch):
    called = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "cache", "info"],
    )

    monkeypatch.setattr(
        cli.cache,
        "print_cache",
        lambda: called.append(True),
    )

    cli.main()

    assert called == [True]


def test_main_cache_clear_all(monkeypatch):
    called = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "cache", "clear"],
    )

    monkeypatch.setattr(
        cli.cache,
        "clear_omm_all",
        lambda: called.append(True),
    )

    cli.main()

    assert called == [True]


def test_main_cache_info_specific(monkeypatch):
    received = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "cache", "info", "25544"],
    )

    monkeypatch.setattr(
        cli.cache,
        "print_cache_specific",
        lambda catalog_number: received.append(catalog_number),
    )

    cli.main()

    assert received == [25544]


def test_main_cache_clear_specific(monkeypatch):
    received = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "cache", "clear", "25544"],
    )

    monkeypatch.setattr(
        cli.cache,
        "clear_omm_specific",
        lambda catalog_number: received.append(catalog_number),
    )

    cli.main()

    assert received == [25544]


def test_main_cache_info_invalid_catalog(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "cache", "info", "abc"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "OrbitOps error:" in captured.out


def test_main_cache_clear_invalid_catalog(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "cache", "clear", "abc"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "OrbitOps error:" in captured.out


# ---------------------------------------------------------------------------
# Missing arguments
# ---------------------------------------------------------------------------

def test_main_search_missing_name(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "search"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Missing satellite name." in captured.out
    assert "orbitops search <name>" in captured.out


def test_main_distance_missing_catalogs(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "distance"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Two satellite catalog numbers are required." in captured.out


@pytest.mark.parametrize(
    "command",
    ["teme", "position", "info", "watch", "gtrack"],
)
def test_main_missing_catalog_number(
    monkeypatch,
    capsys,
    command,
):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", command],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Missing satellite catalog number." in captured.out


# ---------------------------------------------------------------------------
# Catalog parsing / lookup
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "command",
    ["teme", "position", "info", "watch", "gtrack"],
)
def test_main_invalid_catalog_number(
    monkeypatch,
    capsys,
    command,
):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", command, "abc"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Satellite catalog number must be an integer." in captured.out


def test_main_satellite_not_found(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "position", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: {},
    )

    cli.main()

    captured = capsys.readouterr()

    assert "No satellite found with catalog number 25544." in captured.out


# ---------------------------------------------------------------------------
# TEME
# ---------------------------------------------------------------------------

def test_main_teme(monkeypatch, capsys):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "teme", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        cli.propagation,
        "get_teme_cartesian",
        lambda data: (
            (1000.0, 2000.0, 3000.0),
            (1.0, 2.0, 3.0),
        ),
    )

    cli.main()

    captured = capsys.readouterr()

    assert "ISS (ZARYA) TEME Cartesian State" in captured.out
    assert "Position Component" in captured.out
    assert "Position" in captured.out
    assert "Velocity" in captured.out
    assert "1000.00 km" in captured.out
    assert "2000.00 km" in captured.out
    assert "3000.00 km" in captured.out
    assert "1.000 km/s" in captured.out
    assert "2.000 km/s" in captured.out
    assert "3.000 km/s" in captured.out

def test_main_teme_passes_omm_to_propagation(monkeypatch):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    received = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "teme", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    def fake_get_teme_cartesian(data):
        received.append(data)

        return (
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
        )

    monkeypatch.setattr(
        cli.propagation,
        "get_teme_cartesian",
        fake_get_teme_cartesian,
    )

    cli.main()

    assert received == [sat_data]


# ---------------------------------------------------------------------------
# Position
# ---------------------------------------------------------------------------

def test_main_position(monkeypatch, capsys):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "position", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        cli.propagation,
        "get_geographic_position",
        lambda data: (
            12.34567,
            -76.54321,
            415.678,
        ),
    )

    cli.main()

    captured = capsys.readouterr()

    assert "ISS (ZARYA)'s Position" in captured.out
    assert "Latitude" in captured.out
    assert "Longitude" in captured.out
    assert "Altitude" in captured.out
    assert "12.3457°" in captured.out
    assert "-76.5432°" in captured.out
    assert "415.68 km" in captured.out

def test_main_position_catalog_name_fallback(monkeypatch, capsys):
    sat_data = {
        "TEST": "DATA",
    }

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "position", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        cli.propagation,
        "get_geographic_position",
        lambda data: (
            0.0,
            0.0,
            400.0,
        ),
    )

    cli.main()

    captured = capsys.readouterr()

    assert "25544's Position" in captured.out
    assert "0.0000°" in captured.out
    assert "400.00 km" in captured.out

# ---------------------------------------------------------------------------
# Info
# ---------------------------------------------------------------------------

def test_main_info(monkeypatch, capsys):
    omm_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    satcat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
        "COUNTRY": "ISS",
    }

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "info", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: omm_data,
    )

    monkeypatch.setattr(
        cli.api,
        "get_satcat_data",
        lambda catalog_number: satcat_data,
    )

    cli.main()

    captured = capsys.readouterr()

    assert "ISS (ZARYA) Information" in captured.out
    assert "Property" in captured.out
    assert "Value" in captured.out
    assert "OBJECT_NAME" in captured.out
    assert "ISS (ZARYA)" in captured.out
    assert "NORAD_CAT_ID" in captured.out
    assert "25544" in captured.out
    assert "COUNTRY" in captured.out
    assert "ISS" in captured.out

def test_main_info_not_found(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "info", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: {
            "OBJECT_NAME": "ISS (ZARYA)",
        },
    )

    monkeypatch.setattr(
        cli.api,
        "get_satcat_data",
        lambda catalog_number: {},
    )

    cli.main()

    captured = capsys.readouterr()

    assert "No satellite found with catalog number 25544." in captured.out


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def test_main_search(monkeypatch, capsys):
    results = [
        {
            "OBJECT_NAME": "ISS (ZARYA)",
            "NORAD_CAT_ID": 25544,
        },
        {
            "OBJECT_NAME": "OTHER ISS RESULT",
            "NORAD_CAT_ID": 123456,
        },
    ]

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "search", "ISS"],
    )

    monkeypatch.setattr(
        cli.api,
        "search_by_name",
        lambda name: results,
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Results for Search ISS" in captured.out
    assert "Property" in captured.out
    assert "Value" in captured.out
    assert "OBJECT_NAME" in captured.out
    assert "ISS (ZARYA)" in captured.out
    assert "NORAD_CAT_ID" in captured.out
    assert "25544" in captured.out
    
def test_main_search_only_prints_first_result(monkeypatch, capsys):
    results = [
        {
            "OBJECT_NAME": "FIRST RESULT",
        },
        {
            "OBJECT_NAME": "SECOND RESULT",
        },
    ]

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "search", "ISS"],
    )

    monkeypatch.setattr(
        cli.api,
        "search_by_name",
        lambda name: results,
    )

    cli.main()

    captured = capsys.readouterr()

    assert "FIRST RESULT" in captured.out
    assert "SECOND RESULT" not in captured.out


def test_main_search_no_results(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "search", "NOTHING"],
    )

    monkeypatch.setattr(
        cli.api,
        "search_by_name",
        lambda name: [],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "No satellites found matching 'NOTHING'." in captured.out


# ---------------------------------------------------------------------------
# Distance
# ---------------------------------------------------------------------------

def test_main_distance(monkeypatch):
    received = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "distance", "25544", "123456"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_distance_sats",
        lambda first, second: received.append(
            (first, second)
        ),
    )

    cli.main()

    assert received == [(25544, 123456)]


def test_main_distance_first_invalid_catalog(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "distance", "abc", "123456"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Satellite catalog numbers must be integers." in captured.out


def test_main_distance_second_invalid_catalog(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "distance", "25544", "abc"],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Satellite catalog numbers must be integers." in captured.out


# ---------------------------------------------------------------------------
# Watch
# ---------------------------------------------------------------------------

def test_main_watch(monkeypatch):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    received = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "watch", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        cli.api,
        "watch",
        lambda catalog_number: received.append(catalog_number),
    )

    cli.main()

    assert received == [25544]


# ---------------------------------------------------------------------------
# Ground track
# ---------------------------------------------------------------------------

def test_main_gtrack_missing_duration(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "gtrack", "25544"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: {
            "OBJECT_NAME": "ISS (ZARYA)",
        },
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Catalog number and duration are required." in captured.out
    assert "orbitops gtrack <CATNR> <MINUTES>" in captured.out


def test_main_gtrack_invalid_duration(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "gtrack", "25544", "abc"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: {
            "OBJECT_NAME": "ISS (ZARYA)",
        },
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Ground-track duration must be an integer" in captured.out


def test_main_gtrack_generates_track(monkeypatch):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    generated = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "gtrack", "25544", "10"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    def fake_generate_ground_track(data, times):
        generated.append(
            {
                "data": data,
                "times": times,
            }
        )

        return []

    monkeypatch.setattr(
        cli.etc,
        "generate_ground_track",
        fake_generate_ground_track,
    )

    monkeypatch.setattr(
        cli.etc,
        "plot_ground_track",
        lambda *args, **kwargs: None,
    )

    cli.main()

    assert generated[0]["data"] == sat_data
    assert len(generated[0]["times"]) == 11


def test_main_gtrack_times_are_one_minute_apart(monkeypatch):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    received_times = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "gtrack", "25544", "2"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    def fake_generate_ground_track(data, times):
        received_times.extend(times)

        return []

    monkeypatch.setattr(
        cli.etc,
        "generate_ground_track",
        fake_generate_ground_track,
    )

    monkeypatch.setattr(
        cli.etc,
        "plot_ground_track",
        lambda *args, **kwargs: None,
    )

    cli.main()

    assert len(received_times) == 3

    assert (
        received_times[1] - received_times[0]
        == timedelta(minutes=1)
    )

    assert (
        received_times[2] - received_times[1]
        == timedelta(minutes=1)
    )


def test_main_gtrack_plots_track(monkeypatch):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    fake_track = [
        ("point1",),
        ("point2",),
    ]

    plot_arguments = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "gtrack", "25544", "10"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        cli.etc,
        "generate_ground_track",
        lambda data, times: fake_track,
    )

    def fake_plot_ground_track(
        ground_track,
        sat_name,
        minutes,
        data,
    ):
        plot_arguments.append(
            (
                ground_track,
                sat_name,
                minutes,
                data,
            )
        )

    monkeypatch.setattr(
        cli.etc,
        "plot_ground_track",
        fake_plot_ground_track,
    )

    cli.main()

    assert plot_arguments == [
        (
            fake_track,
            "ISS (ZARYA)",
            10,
            sat_data,
        )
    ]


def test_main_gtrack_csv(monkeypatch):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    fake_track = [
        ("point1",),
    ]

    csv_arguments = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "orbitops",
            "gtrack",
            "25544",
            "10",
            "--csv",
        ],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        cli.etc,
        "generate_ground_track",
        lambda data, times: fake_track,
    )

    monkeypatch.setattr(
        cli.etc,
        "plot_ground_track",
        lambda *args, **kwargs: None,
    )

    def fake_save_ground_track_csv(
        ground_track,
        filename,
    ):
        csv_arguments.append(
            (
                ground_track,
                filename,
            )
        )

    monkeypatch.setattr(
        cli.etc,
        "save_ground_track_csv",
        fake_save_ground_track_csv,
    )

    cli.main()

    assert csv_arguments[0][0] == fake_track

    filename = csv_arguments[0][1]

    assert filename.startswith("ISS (ZARYA)-")
    assert filename.endswith(".csv")


def test_main_gtrack_without_csv_does_not_save_csv(monkeypatch):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    csv_called = []

    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "gtrack", "25544", "10"],
    )

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        cli.etc,
        "generate_ground_track",
        lambda data, times: [],
    )

    monkeypatch.setattr(
        cli.etc,
        "plot_ground_track",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        cli.etc,
        "save_ground_track_csv",
        lambda *args, **kwargs: csv_called.append(True),
    )

    cli.main()

    assert csv_called == []


# ---------------------------------------------------------------------------
# Exception handling
# ---------------------------------------------------------------------------

def test_main_keyboard_interrupt(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "position", "25544"],
    )

    def fake_get_sat_info_omm(catalog_number):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    cli.main()

    captured = capsys.readouterr()

    assert "OrbitOps stopped." in captured.out


def test_main_general_exception(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["orbitops", "position", "25544"],
    )

    def fake_get_sat_info_omm(catalog_number):
        raise RuntimeError("Something exploded")

    monkeypatch.setattr(
        cli.api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    cli.main()

    captured = capsys.readouterr()

    assert "OrbitOps error: Something exploded" in captured.out