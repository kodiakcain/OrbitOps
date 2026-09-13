import json
import os
from datetime import UTC, datetime, timedelta

import pytest

from orbitops import cache


# get_cache_path
def test_get_cache_path():
    path = cache.get_cache_path(25544)

    assert path.name == "25544.json"

def test_get_cache_path_six():
    path = cache.get_cache_path(123456)

    assert path.name == "123456.json"

def test_cache_path_short():

    with pytest.raises(ValueError):

        cache.get_cache_path(1234)

def test_cache_path_long():

    with pytest.raises(ValueError):

        cache.get_cache_path(1234567)

def test_cache_path_str():

    with pytest.raises(TypeError):

        cache.get_cache_path("abc")

def test_cache_path_neg():

    with pytest.raises(ValueError):

        cache.get_cache_path(-25544)

# cache_exists
def test_cache_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"
    path.touch()

    assert cache.cache_exists(25544) is True

def test_cache_does_not_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    assert cache.cache_exists(25544) is False

def test_cache_exists_str():

    with pytest.raises(TypeError):

        cache.cache_exists("abc")

def test_cache_exists_short():

    with pytest.raises(ValueError):

        cache.cache_exists(1234)

def test_cache_exists_long():

    with pytest.raises(ValueError):

        cache.cache_exists(1234567)

def test_cache_exists_neg():

    with pytest.raises(ValueError):

        cache.cache_exists(-25544)

# cache_is_fresh
def test_cache_is_fresh_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    assert cache.cache_is_fresh(25544) is False


def test_cache_is_fresh_current_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"
    path.touch()

    assert cache.cache_is_fresh(25544) is True


def test_cache_is_fresh_old_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"
    path.touch()

    old_time = datetime.now(UTC) - timedelta(hours=3)

    os.utime(
        path,
        (
            old_time.timestamp(),
            old_time.timestamp(),
        ),
    )

    assert cache.cache_is_fresh(25544) is False


def test_cache_is_fresh_under_two_hours(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"
    path.touch()

    recent_time = datetime.now(UTC) - timedelta(hours=1, minutes=59)

    os.utime(
        path,
        (
            recent_time.timestamp(),
            recent_time.timestamp(),
        ),
    )

    assert cache.cache_is_fresh(25544) is True

def test_cache_is_fresh_str():
    with pytest.raises(TypeError):
        cache.cache_is_fresh("25544")


def test_cache_is_fresh_neg():
    with pytest.raises(ValueError):
        cache.cache_is_fresh(-25544)


def test_cache_is_fresh_short():
    with pytest.raises(ValueError):
        cache.cache_is_fresh(1234)


def test_cache_is_fresh_long():
    with pytest.raises(ValueError):
        cache.cache_is_fresh(1234567)

# save_omm
def test_save_omm_string_catalog():
    with pytest.raises(TypeError):
        cache.save_omm("25544", {})


def test_save_omm_negative_catalog():
    with pytest.raises(ValueError):
        cache.save_omm(-25544, {})


def test_save_omm_short_catalog():
    with pytest.raises(ValueError):
        cache.save_omm(1234, {})


def test_save_omm_long_catalog():
    with pytest.raises(ValueError):
        cache.save_omm(1234567, {})


def test_save_omm_invalid_data_type():
    with pytest.raises(TypeError):
        cache.save_omm(25544, "not a dictionary")


def test_save_omm_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    data = {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }

    cache.save_omm(25544, data)

    path = tmp_path / "25544.json"

    assert path.is_file()


def test_save_omm_writes_correct_data(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    data = {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }

    cache.save_omm(25544, data)

    path = tmp_path / "25544.json"

    with open(path, "r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == data

# load_omm
def test_load_omm_string_catalog():
    with pytest.raises(TypeError):
        cache.load_omm("25544", {})


def test_load_omm_negative_catalog():
    with pytest.raises(ValueError):
        cache.load_omm(-25544, {})


def test_load_omm_short_catalog():
    with pytest.raises(ValueError):
        cache.load_omm(1234, {})


def test_load_omm_long_catalog():
    with pytest.raises(ValueError):
        cache.load_omm(1234567, {})


def test_load_omm_invalid_data_type():
    with pytest.raises(TypeError):
        cache.load_omm(25544, "not a dictionary")


def test_load_omm_existing_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    cached_data = {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }

    path = tmp_path / "25544.json"

    with open(path, "w", encoding="utf-8") as file:
        json.dump(cached_data, file)

    result = cache.load_omm(25544, {})

    assert result == cached_data


def test_load_omm_no_cache_returns_data(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    data = {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }

    result = cache.load_omm(25544, data)

    assert result == data


def test_load_omm_no_cache_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    data = {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }

    cache.load_omm(25544, data)

    path = tmp_path / "25544.json"

    assert path.is_file()


def test_load_omm_no_cache_saves_correct_data(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    data = {
        "OBJECT_NAME": "ISS (ZARYA)",
        "NORAD_CAT_ID": 25544,
    }

    cache.load_omm(25544, data)

    path = tmp_path / "25544.json"

    with open(path, "r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == data

# clear_omm_specific
def test_clear_omm_specific_string_catalog():
    with pytest.raises(TypeError):
        cache.clear_omm_specific("25544")


def test_clear_omm_specific_negative_catalog():
    with pytest.raises(ValueError):
        cache.clear_omm_specific(-25544)


def test_clear_omm_specific_short_catalog():
    with pytest.raises(ValueError):
        cache.clear_omm_specific(1234)


def test_clear_omm_specific_long_catalog():
    with pytest.raises(ValueError):
        cache.clear_omm_specific(1234567)


def test_clear_omm_specific_removes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"
    path.touch()

    assert path.is_file()

    cache.clear_omm_specific(25544)

    assert not path.exists()


def test_clear_omm_specific_only_removes_requested_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    first_path = tmp_path / "25544.json"
    second_path = tmp_path / "123456.json"

    first_path.touch()
    second_path.touch()

    cache.clear_omm_specific(25544)

    assert not first_path.exists()
    assert second_path.is_file()


def test_clear_omm_specific_nonexistent_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"

    cache.clear_omm_specific(25544)

    assert not path.exists()

# clear_omm_all
def test_clear_omm_all_removes_all_json_files(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    first_path = tmp_path / "25544.json"
    second_path = tmp_path / "123456.json"

    first_path.touch()
    second_path.touch()

    cache.clear_omm_all()

    assert not first_path.exists()
    assert not second_path.exists()


def test_clear_omm_all_empty_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    cache.clear_omm_all()

    assert list(tmp_path.glob("*.json")) == []


def test_clear_omm_all_does_not_remove_other_files(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    json_path = tmp_path / "25544.json"
    other_path = tmp_path / "important.txt"

    json_path.touch()
    other_path.touch()

    cache.clear_omm_all()

    assert not json_path.exists()
    assert other_path.exists()

# print_cache
def test_print_cache_one_file(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"
    path.write_text('{"OBJECT_NAME": "ISS (ZARYA)"}', encoding="utf-8")

    cache.print_cache()

    captured = capsys.readouterr()

    assert "CATNR 25544 Cache" in captured.out
    assert "OBJECT_NAME" in captured.out
    assert "ISS (ZARYA)" in captured.out


def test_print_cache_multiple_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    first_path = tmp_path / "25544.json"
    second_path = tmp_path / "123456.json"

    first_path.write_text('{"OBJECT_NAME": "ISS (ZARYA)"}', encoding="utf-8")
    second_path.write_text('{"OBJECT_NAME": "TEST SATELLITE"}', encoding="utf-8")

    cache.print_cache()

    captured = capsys.readouterr()

    assert "CATNR 25544 Cache" in captured.out
    assert "CATNR 123456 Cache" in captured.out
    assert "OBJECT_NAME" in captured.out
    assert "ISS (ZARYA)" in captured.out
    assert "TEST SATELLITE" in captured.out


def test_print_cache_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    cache.print_cache()

    captured = capsys.readouterr()

    assert "Cache is empty." in captured.out


def test_print_cache_ignores_non_json_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "important.txt"
    path.write_text("DO NOT PRINT THIS", encoding="utf-8")

    cache.print_cache()

    captured = capsys.readouterr()

    assert "DO NOT PRINT THIS" not in captured.out
    assert "Cache is empty." in captured.out

# print_cache_specific
def test_print_cache_specific_string_catalog():
    with pytest.raises(TypeError):
        cache.print_cache_specific("25544")


def test_print_cache_specific_negative_catalog():
    with pytest.raises(ValueError):
        cache.print_cache_specific(-25544)


def test_print_cache_specific_short_catalog():
    with pytest.raises(ValueError):
        cache.print_cache_specific(1234)


def test_print_cache_specific_long_catalog():
    with pytest.raises(ValueError):
        cache.print_cache_specific(1234567)


def test_print_cache_specific_existing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"
    path.write_text(
        '{"OBJECT_NAME": "ISS (ZARYA)"}',
        encoding="utf-8",
    )

    cache.print_cache_specific(25544)

    captured = capsys.readouterr()

    assert "CATNR 25544 Cache" in captured.out
    assert "OBJECT_NAME" in captured.out
    assert "ISS (ZARYA)" in captured.out


def test_print_cache_specific_success_message(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    path = tmp_path / "25544.json"
    path.write_text(
        '{"OBJECT_NAME": "ISS (ZARYA)"}',
        encoding="utf-8",
    )

    cache.print_cache_specific(25544)

    captured = capsys.readouterr()

    assert "Retrieved cache data for CATNR 25544." in captured.out


def test_print_cache_specific_missing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    cache.print_cache_specific(25544)

    captured = capsys.readouterr()

    assert "CATNR not in cache." in captured.out


def test_print_cache_specific_only_prints_requested(
    tmp_path,
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)

    first_path = tmp_path / "25544.json"
    second_path = tmp_path / "123456.json"

    first_path.write_text(
        '{"OBJECT_NAME": "ISS (ZARYA)"}',
        encoding="utf-8",
    )

    second_path.write_text(
        '{"OBJECT_NAME": "OTHER SATELLITE"}',
        encoding="utf-8",
    )

    cache.print_cache_specific(25544)

    captured = capsys.readouterr()

    assert "CATNR 25544 Cache" in captured.out
    assert "OBJECT_NAME" in captured.out
    assert "ISS (ZARYA)" in captured.out
    assert "OTHER SATELLITE" not in captured.out
    assert "CATNR 123456 Cache" not in captured.out