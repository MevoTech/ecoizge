"""Türkçe sayı ve birim normalleştirme testleri (R-VER-01, B9)."""

import pytest

from report_service.verify.numbers import (
    Quantity,
    extract_numbers,
    format_tr,
    match,
    parse_tr_number,
)


@pytest.mark.parametrize(
    "text,value",
    [
        ("12.450,5", 12450.5),
        ("12.450", 12450.0),
        ("1.234.567", 1234567.0),
        ("1,5", 1.5),
        ("12.5", 12.5),
        ("0,25", 0.25),
        ("42", 42.0),
    ],
)
def test_r_ver_01_parse_turkish_formats(text, value):
    assert parse_tr_number(text) == pytest.approx(value)


@pytest.mark.parametrize("text", ["1,2,3", "1,234.5", "abc", "1.23.4"])
def test_r_ver_01_parse_rejects_ambiguous(text):
    with pytest.raises(ValueError):
        parse_tr_number(text)


def _one(text: str) -> Quantity:
    qs = [q for q in extract_numbers(text) if not q.is_year]
    assert len(qs) == 1, qs
    return qs[0]


@pytest.mark.parametrize(
    "text,value,unit",
    [
        ("Kapsam 1 toplamı 12.450 tCO2e oldu", 12450, "tCO2e"),
        ("emisyon 12,4 ktCO2e", 12400, "tCO2e"),
        ("emisyon 1,1 MtCO2e", 1_100_000, "tCO2e"),
        ("tüketim 3,4 GWh", 3_400_000, "kWh"),
        ("tüketim 850 MWh", 850_000, "kWh"),
        ("su çekimi 1,2 milyon m³", 1_200_000, "m3"),
        ("yenilenebilir payı %12,5", 12.5, "%"),
        ("yenilenebilir payı yüzde 40", 40, "%"),
        ("atık 2,5 bin ton", 2500, "t"),
    ],
)
def test_r_ver_01_extract_value_and_base_unit(text, value, unit):
    q = _one(text.replace("Kapsam 1 ", ""))
    assert q.value == pytest.approx(value)
    assert q.unit == unit


def test_r_ver_01_year_is_not_a_value():
    qs = extract_numbers("2024 yılında 12.450 tCO2e")
    assert [q.is_year for q in qs] == [True, False]


def test_r_ver_01_digits_inside_identifiers_ignored():
    assert extract_numbers("CO2 ve S-03 senaryosu") == []


def test_r_ver_01_match_within_eps_same_unit():
    q = _one("12,45 ktCO2e")
    src = [Quantity(12450.0, "tCO2e", "12.450 tCO2e", 0, 0)]
    assert match(q, src, eps=0.005) is not None


def test_r_ver_01_match_rejects_unit_mismatch_and_large_error():
    src = [Quantity(12450.0, "tCO2e", "", 0, 0)]
    assert match(_one("12.450 MWh"), src) is None
    assert match(_one("13.000 tCO2e"), src) is None


def test_format_tr_roundtrip():
    assert format_tr(12450.5, 1) == "12.450,5"
    assert parse_tr_number(format_tr(1234567, 0)) == 1234567
