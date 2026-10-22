"""Ortak sözleşme testleri (R-API-01, R-INT-01, R-VER-03)."""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "shared/contracts/forecast_record.schema.json").read_text())
EXAMPLE = json.loads((ROOT / "shared/contracts/examples/forecast_record.example.json").read_text())
V = Draft202012Validator(SCHEMA)


def test_schema_is_valid_draft_2020_12():
    Draft202012Validator.check_schema(SCHEMA)


def test_r_api_01_s19_example_with_schema_version_passes():
    assert list(V.iter_errors(EXAMPLE)) == []


def test_r_api_01_schema_version_required():
    rec = copy.deepcopy(EXAMPLE)
    del rec["schema_version"]
    assert not V.is_valid(rec)


@pytest.mark.parametrize("field", ["model_id", "senaryo_id", "guven_araligi"])
def test_r_ver_03_forecast_requires_provenance(field):
    rec = copy.deepcopy(EXAMPLE)
    del rec[field]
    assert not V.is_valid(rec)


def test_r_ver_03_realized_record_needs_no_model():
    rec = {
        "schema_version": "1.0",
        "kpi": "toplam_emisyon",
        "birim": "tCO2e",
        "yil": 2024,
        "deger": 43650,
        "veri_turu": "gerceklesmis",
        "kaynak": "olcum_gerceklesmis/2024",
    }
    assert V.is_valid(rec)


def test_r_ver_03_unknown_data_type_rejected():
    rec = copy.deepcopy(EXAMPLE)
    rec["veri_turu"] = "senaryo"
    assert not V.is_valid(rec)
