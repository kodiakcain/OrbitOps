import pytest
import requests

from orbitops import api


# get_sat_info_omm
class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return [
            {
                "OBJECT_NAME": "ISS (ZARYA)",
                "NORAD_CAT_ID": 25544,
            }
        ]

# get_sat_info_omm
def test_get_sat_info_omm_string_catalog():
    with pytest.raises(TypeError):
        api.get_sat_info_omm("25544")


def test_get_sat_info_omm_negative_catalog():
    with pytest.raises(ValueError):
        api.get_sat_info_omm(-25544)


def test_get_sat_info_omm_short_catalog():
    with pytest.raises(ValueError):
        api.get_sat_info_omm(1234)


def test_get_sat_info_omm_long_catalog():
    with pytest.raises(ValueError):
        api.get_sat_info_omm(1234567)


# Fresh cache should be returned
def test_get_sat_info_omm_uses_fresh_cache(monkeypatch):
    cached_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }

    monkeypatch.setattr(
        api.cache,
        "cache_is_fresh",
        lambda catalog_number: True,
    )

    monkeypatch.setattr(
        api.cache,
        "load_omm",
        lambda catalog_number, data: cached_data,
    )

    result = api.get_sat_info_omm(25544)

    assert result == cached_data


# Fresh cache should prevent an HTTP request
def test_get_sat_info_omm_fresh_cache_no_request(monkeypatch):
    cached_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    monkeypatch.setattr(
        api.cache,
        "cache_is_fresh",
        lambda catalog_number: True,
    )

    monkeypatch.setattr(
        api.cache,
        "load_omm",
        lambda catalog_number, data: cached_data,
    )

    def fake_get(*args, **kwargs):
        raise AssertionError(
            "requests.get() should not have been called"
        )

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    result = api.get_sat_info_omm(25544)

    assert result == cached_data


# Stale/missing cache should fetch data
def test_get_sat_info_omm_fetches_data(monkeypatch):
    monkeypatch.setattr(
        api.cache,
        "cache_is_fresh",
        lambda catalog_number: False,
    )

    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )

    monkeypatch.setattr(
        api.cache,
        "save_omm",
        lambda catalog_number, data: None,
    )

    result = api.get_sat_info_omm(25544)

    assert result == {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }


# Fetched data should be saved to the cache
def test_get_sat_info_omm_saves_fetched_data(monkeypatch):
    monkeypatch.setattr(
        api.cache,
        "cache_is_fresh",
        lambda catalog_number: False,
    )

    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )

    saved = {}

    def fake_save_omm(catalog_number, data):
        saved["catalog_number"] = catalog_number
        saved["data"] = data

    monkeypatch.setattr(
        api.cache,
        "save_omm",
        fake_save_omm,
    )

    api.get_sat_info_omm(25544)

    assert saved["catalog_number"] == 25544

    assert saved["data"] == {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }


# Empty CelesTrak response should return an empty dictionary
def test_get_sat_info_omm_empty_response(monkeypatch):
    class EmptyResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return []

    monkeypatch.setattr(
        api.cache,
        "cache_is_fresh",
        lambda catalog_number: False,
    )

    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: EmptyResponse(),
    )

    result = api.get_sat_info_omm(25544)

    assert result == {}


# Network failure should return an empty dictionary
def test_get_sat_info_omm_request_failure(monkeypatch):
    monkeypatch.setattr(
        api.cache,
        "cache_is_fresh",
        lambda catalog_number: False,
    )

    def fake_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    result = api.get_sat_info_omm(25544)

    assert result == {}


# Network failure should print an error
def test_get_sat_info_omm_request_failure_message(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        api.cache,
        "cache_is_fresh",
        lambda catalog_number: False,
    )

    def fake_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    api.get_sat_info_omm(25544)

    captured = capsys.readouterr()

    assert "Failed to retrieve satellite data" in captured.out


# Verify the correct CelesTrak request is made
def test_get_sat_info_omm_correct_request(monkeypatch):
    monkeypatch.setattr(
        api.cache,
        "cache_is_fresh",
        lambda catalog_number: False,
    )

    request_data = {}

    def fake_get(url, params, timeout):
        request_data["url"] = url
        request_data["params"] = params
        request_data["timeout"] = timeout

        return FakeResponse()

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    monkeypatch.setattr(
        api.cache,
        "save_omm",
        lambda catalog_number, data: None,
    )

    api.get_sat_info_omm(25544)

    assert request_data["url"] == (
        "https://celestrak.org/NORAD/elements/gp.php"
    )

    assert request_data["params"] == {
        "CATNR": 25544,
        "FORMAT": "JSON",
    }

    assert request_data["timeout"] == 20

class FakeSatcatResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return [
            {
                "OBJECT_NAME": "ISS (ZARYA)",
                "NORAD_CAT_ID": 25544,
                "COUNTRY": "ISS",
            }
        ]


# get_satcat_data
def test_get_satcat_data_string_catalog():
    with pytest.raises(TypeError):
        api.get_satcat_data("25544")


def test_get_satcat_data_negative_catalog():
    with pytest.raises(ValueError):
        api.get_satcat_data(-25544)


def test_get_satcat_data_short_catalog():
    with pytest.raises(ValueError):
        api.get_satcat_data(1234)


def test_get_satcat_data_long_catalog():
    with pytest.raises(ValueError):
        api.get_satcat_data(1234567)


# Successful request should return first result
def test_get_satcat_data_returns_data(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: FakeSatcatResponse(),
    )

    result = api.get_satcat_data(25544)

    assert result == {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
        "COUNTRY": "ISS",
    }


# Empty response should return an empty dictionary
def test_get_satcat_data_empty_response(monkeypatch):
    class EmptyResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return []

    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: EmptyResponse(),
    )

    result = api.get_satcat_data(25544)

    assert result == {}


# Network failure should return an empty dictionary
def test_get_satcat_data_request_failure(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    result = api.get_satcat_data(25544)

    assert result == {}


# Network failure should print an error message
def test_get_satcat_data_request_failure_message(
    monkeypatch,
    capsys,
):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    api.get_satcat_data(25544)

    captured = capsys.readouterr()

    assert "Failed to retrieve satellite data" in captured.out


# Verify correct CelesTrak request
def test_get_satcat_data_correct_request(monkeypatch):
    request_data = {}

    def fake_get(url, params, timeout):
        request_data["url"] = url
        request_data["params"] = params
        request_data["timeout"] = timeout

        return FakeSatcatResponse()

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    api.get_satcat_data(25544)

    assert request_data["url"] == (
        "https://celestrak.org/satcat/records.php"
    )

    assert request_data["params"] == {
        "CATNR": 25544,
        "FORMAT": "JSON",
    }

    assert request_data["timeout"] == 20


# HTTP error from raise_for_status should be handled
def test_get_satcat_data_http_error(monkeypatch):
    class ErrorResponse:
        def raise_for_status(self):
            raise requests.HTTPError("404 Client Error")

    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: ErrorResponse(),
    )

    result = api.get_satcat_data(25544)

    assert result == {}

# search_by_name
class FakeSearchResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return [
            {
                "OBJECT_NAME": "ISS (ZARYA)",
                "NORAD_CAT_ID": 25544,
            },
            {
                "OBJECT_NAME": "UME-2 (ISS-B)",
                "NORAD_CAT_ID": 123456,
            },
        ]


def test_search_by_name_invalid_type():
    with pytest.raises(TypeError):
        api.search_by_name(25544)


def test_search_by_name_empty_string():
    with pytest.raises(ValueError):
        api.search_by_name("")


def test_search_by_name_too_long():
    with pytest.raises(ValueError):
        api.search_by_name("A" * 31)


def test_search_by_name_valid_one_character(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: FakeSearchResponse(),
    )

    result = api.search_by_name("A")

    assert len(result) == 2


def test_search_by_name_returns_results(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: FakeSearchResponse(),
    )

    result = api.search_by_name("ISS")

    assert result == [
        {
            "OBJECT_NAME": "ISS (ZARYA)",
            "NORAD_CAT_ID": 25544,
        },
        {
            "OBJECT_NAME": "UME-2 (ISS-B)",
            "NORAD_CAT_ID": 123456,
        },
    ]


def test_search_by_name_empty_results(monkeypatch):
    class EmptyResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return []

    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: EmptyResponse(),
    )

    result = api.search_by_name("ISS")

    assert result == []


def test_search_by_name_request_failure(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    result = api.search_by_name("ISS")

    assert result == []


def test_search_by_name_request_failure_message(
    monkeypatch,
    capsys,
):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    api.search_by_name("ISS")

    captured = capsys.readouterr()

    assert "Failed to retrieve satellite data" in captured.out


def test_search_by_name_http_error(monkeypatch):
    class ErrorResponse:
        def raise_for_status(self):
            raise requests.HTTPError("500 Server Error")

    monkeypatch.setattr(
        api.requests,
        "get",
        lambda *args, **kwargs: ErrorResponse(),
    )

    result = api.search_by_name("ISS")

    assert result == []


def test_search_by_name_correct_request(monkeypatch):
    request_data = {}

    def fake_get(url, params, timeout):
        request_data["url"] = url
        request_data["params"] = params
        request_data["timeout"] = timeout

        return FakeSearchResponse()

    monkeypatch.setattr(
        api.requests,
        "get",
        fake_get,
    )

    api.search_by_name("ISS")

    assert request_data["url"] == (
        "https://celestrak.org/satcat/records.php"
    )

    assert request_data["params"] == {
        "NAME": "ISS",
        "FORMAT": "JSON",
    }

    assert request_data["timeout"] == 20

# get_distance_sats

def test_get_distance_sats_first_string_catalog():
    with pytest.raises(TypeError):
        api.get_distance_sats("25544", 123456)


def test_get_distance_sats_first_negative_catalog():
    with pytest.raises(ValueError):
        api.get_distance_sats(-25544, 123456)


def test_get_distance_sats_first_short_catalog():
    with pytest.raises(ValueError):
        api.get_distance_sats(1234, 123456)


def test_get_distance_sats_first_long_catalog():
    with pytest.raises(ValueError):
        api.get_distance_sats(1234567, 123456)


def test_get_distance_sats_second_string_catalog():
    with pytest.raises(TypeError):
        api.get_distance_sats(25544, "123456")


def test_get_distance_sats_second_negative_catalog():
    with pytest.raises(ValueError):
        api.get_distance_sats(25544, -123456)


def test_get_distance_sats_second_short_catalog():
    with pytest.raises(ValueError):
        api.get_distance_sats(25544, 1234)


def test_get_distance_sats_second_long_catalog():
    with pytest.raises(ValueError):
        api.get_distance_sats(25544, 1234567)


def test_get_distance_sats_missing_first_satellite(
    monkeypatch,
    capsys,
):
    def fake_get_sat_info_omm(catalog_number):
        if catalog_number == 25544:
            return {}

        return {
            "OBJECT_NAME": "SECOND SATELLITE",
        }

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    api.get_distance_sats(25544, 123456)

    captured = capsys.readouterr()

    assert (
        "No valid OMM data found for catalog number 25544."
        in captured.out
    )


def test_get_distance_sats_missing_second_satellite(
    monkeypatch,
    capsys,
):
    def fake_get_sat_info_omm(catalog_number):
        if catalog_number == 25544:
            return {
                "OBJECT_NAME": "FIRST SATELLITE",
            }

        return {}

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    api.get_distance_sats(25544, 123456)

    captured = capsys.readouterr()

    assert (
        "No valid OMM data found for catalog number 123456."
        in captured.out
    )


def test_get_distance_sats_correct_distance(
    monkeypatch,
    capsys,
):
    first_data = {
        "OBJECT_NAME": "SAT ONE",
    }

    second_data = {
        "OBJECT_NAME": "SAT TWO",
    }

    def fake_get_sat_info_omm(catalog_number):
        if catalog_number == 25544:
            return first_data

        return second_data

    def fake_get_teme_cartesian(data):
        if data is first_data:
            return (
                (0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
            )

        return (
            (3.0, 4.0, 0.0),
            (0.0, 0.0, 0.0),
        )

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_teme_cartesian",
        fake_get_teme_cartesian,
    )

    api.get_distance_sats(25544, 123456)

    captured = capsys.readouterr()

    assert "5.000km" in captured.out


def test_get_distance_sats_prints_satellite_names(
    monkeypatch,
    capsys,
):
    first_data = {
        "OBJECT_NAME": "SAT ONE",
    }

    second_data = {
        "OBJECT_NAME": "SAT TWO",
    }

    def fake_get_sat_info_omm(catalog_number):
        if catalog_number == 25544:
            return first_data

        return second_data

    def fake_get_teme_cartesian(data):
        if data is first_data:
            return (
                (0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
            )

        return (
            (3.0, 4.0, 0.0),
            (0.0, 0.0, 0.0),
        )

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_teme_cartesian",
        fake_get_teme_cartesian,
    )

    api.get_distance_sats(25544, 123456)

    captured = capsys.readouterr()

    assert "SAT ONE" in captured.out
    assert "SAT TWO" in captured.out


def test_get_distance_sats_uses_catalog_number_when_name_missing(
    monkeypatch,
    capsys,
):
    first_data = {}
    second_data = {}

    # Need truthy dictionaries so they are treated as valid OMM data
    first_data["TEST"] = "A"
    second_data["TEST"] = "B"

    def fake_get_sat_info_omm(catalog_number):
        if catalog_number == 25544:
            return first_data

        return second_data

    def fake_get_teme_cartesian(data):
        if data is first_data:
            return (
                (0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
            )

        return (
            (1.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
        )

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_teme_cartesian",
        fake_get_teme_cartesian,
    )

    api.get_distance_sats(25544, 123456)

    captured = capsys.readouterr()

    assert "25544" in captured.out
    assert "123456" in captured.out


def test_get_distance_sats_passes_correct_data_to_propagation(
    monkeypatch,
):
    first_data = {
        "OBJECT_NAME": "SAT ONE",
    }

    second_data = {
        "OBJECT_NAME": "SAT TWO",
    }

    propagated = []

    def fake_get_sat_info_omm(catalog_number):
        if catalog_number == 25544:
            return first_data

        return second_data

    def fake_get_teme_cartesian(data):
        propagated.append(data)

        return (
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
        )

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_teme_cartesian",
        fake_get_teme_cartesian,
    )

    api.get_distance_sats(25544, 123456)

    assert propagated[0] == first_data
    assert propagated[1] == second_data

# watch

def test_watch_string_catalog():
    with pytest.raises(TypeError):
        api.watch("25544")


def test_watch_negative_catalog():
    with pytest.raises(ValueError):
        api.watch(-25544)


def test_watch_short_catalog():
    with pytest.raises(ValueError):
        api.watch(1234)


def test_watch_long_catalog():
    with pytest.raises(ValueError):
        api.watch(1234567)


def test_watch_missing_satellite(monkeypatch, capsys):
    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        lambda catalog_number: {},
    )

    api.watch(25544)

    captured = capsys.readouterr()

    assert (
        "No valid OMM data found for catalog number 25544."
        in captured.out
    )


def test_watch_prints_stop_message(monkeypatch, capsys):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_geographic_position",
        lambda data: (10.0, 20.0, 400.0),
    )

    def fake_sleep(seconds):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        api.time,
        "sleep",
        fake_sleep,
    )

    with pytest.raises(KeyboardInterrupt):
        api.watch(25544)

    captured = capsys.readouterr()

    assert "Press 'Ctrl+C' to stop watching." in captured.out


def test_watch_prints_position(monkeypatch, capsys):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_geographic_position",
        lambda data: (
            12.34567,
            -76.54321,
            415.678,
        ),
    )

    def fake_sleep(seconds):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        api.time,
        "sleep",
        fake_sleep,
    )

    with pytest.raises(KeyboardInterrupt):
        api.watch(25544)

    captured = capsys.readouterr()

    assert "ISS (ZARYA)" in captured.out
    assert "Lat: 12.3457°" in captured.out
    assert "Lon: -76.5432°" in captured.out
    assert "Alt: 415.68 km" in captured.out


def test_watch_uses_catalog_number_when_name_missing(
    monkeypatch,
    capsys,
):
    sat_data = {
        "TEST": "DATA",
    }

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_geographic_position",
        lambda data: (
            10.0,
            20.0,
            400.0,
        ),
    )

    def fake_sleep(seconds):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        api.time,
        "sleep",
        fake_sleep,
    )

    with pytest.raises(KeyboardInterrupt):
        api.watch(25544)

    captured = capsys.readouterr()

    assert "25544" in captured.out


def test_watch_passes_correct_data_to_propagation(
    monkeypatch,
):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    received_data = []

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    def fake_get_geographic_position(data):
        received_data.append(data)

        return (
            10.0,
            20.0,
            400.0,
        )

    monkeypatch.setattr(
        api.propagation,
        "get_geographic_position",
        fake_get_geographic_position,
    )

    def fake_sleep(seconds):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        api.time,
        "sleep",
        fake_sleep,
    )

    with pytest.raises(KeyboardInterrupt):
        api.watch(25544)

    assert received_data[0] == sat_data


def test_watch_sleeps_one_second(monkeypatch):
    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    sleep_values = []

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        lambda catalog_number: sat_data,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_geographic_position",
        lambda data: (
            10.0,
            20.0,
            400.0,
        ),
    )

    def fake_sleep(seconds):
        sleep_values.append(seconds)
        raise KeyboardInterrupt

    monkeypatch.setattr(
        api.time,
        "sleep",
        fake_sleep,
    )

    with pytest.raises(KeyboardInterrupt):
        api.watch(25544)

    assert sleep_values == [1]


def test_watch_gets_omm_once(monkeypatch):
    call_count = 0

    sat_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
    }

    def fake_get_sat_info_omm(catalog_number):
        nonlocal call_count

        call_count += 1

        return sat_data

    monkeypatch.setattr(
        api,
        "get_sat_info_omm",
        fake_get_sat_info_omm,
    )

    monkeypatch.setattr(
        api.propagation,
        "get_geographic_position",
        lambda data: (
            10.0,
            20.0,
            400.0,
        ),
    )

    def fake_sleep(seconds):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        api.time,
        "sleep",
        fake_sleep,
    )

    with pytest.raises(KeyboardInterrupt):
        api.watch(25544)

    assert call_count == 1