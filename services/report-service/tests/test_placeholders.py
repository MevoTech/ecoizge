"""Yer tutuculu üretim ve kip denetimi testleri (R-GEN-03, R-GEN-04, R-VER-03, ADR-004)."""

import pytest

from report_service.generation.placeholders import Record, check_free_text, render, validate_draft
from report_service.verify.tense import check_sentence

RECORDS = [
    Record("toplam_emisyon", 2024, 43650, "tCO2e", "gerceklesmis", "olcum_gerceklesmis/2024"),
    Record(
        "toplam_emisyon",
        2028,
        39870,
        "tCO2e",
        "tahmin",
        "emisyon-api/senaryo",
        model_id="xgb-v3.2",
        senaryo_id="S-03",
        guven_araligi=(37900, 41800),
    ),
]

GOOD = (
    "Şirketin 2024 yılı toplam emisyonu {{KPI:toplam_emisyon:2024:gerceklesmis}} olarak "
    "gerçekleşmiştir [1]. S-03 senaryosunda 2028 yılı emisyonunun "
    "{{KPI:toplam_emisyon:2028:tahmin}} olması öngörülmektedir [2]."
)


def test_r_gen_03_render_fills_values_deterministically():
    res = render(GOOD, RECORDS)
    assert res.ok, res.errors
    assert "43.650 tCO2e" in res.text
    assert "39.870 tCO2e (tahmin)" in res.text
    assert "{{" not in res.text
    assert [c["veri_turu"] for c in res.claims] == ["gerceklesmis", "tahmin"]
    assert res.claims[1]["model_id"] == "xgb-v3.2"


def test_r_gen_03_free_text_number_rejected():
    bad = GOOD.replace("{{KPI:toplam_emisyon:2024:gerceklesmis}}", "43.650 tCO2e")
    errs = check_free_text(bad)
    assert errs and "serbest metinde sayı" in errs[0]
    assert not render(bad, RECORDS).ok


@pytest.mark.parametrize(
    "text",
    [
        "Kapsam 1 ve Kapsam 2 emisyonları TSRS 2 ve GRI 305 kapsamında raporlanır [1].",
        "ISO 14001 sertifikası madde 29(a) gereği açıklanır [3].",
        "2026 yılı hedefi belirlenmiştir [1, 2].",
    ],
)
def test_r_gen_03_identifiers_years_citations_are_not_values(text):
    assert check_free_text(text) == []


def test_r_gen_04_missing_record_is_error_not_invented():
    draft = "2025 emisyonu {{KPI:toplam_emisyon:2025:gerceklesmis}} olarak gerçekleşmiştir [1]."
    errs = validate_draft(draft, RECORDS)
    assert any("kaynak kaydı yok" in e for e in errs)


def test_r_ver_03_type_mismatch_rejected():
    draft = "2028 emisyonu {{KPI:toplam_emisyon:2028:gerceklesmis}} olarak gerçekleşmiştir [1]."
    errs = validate_draft(draft, RECORDS)
    assert any("tür uyuşmazlığı" in e for e in errs)


def test_r_ver_03_forecast_in_past_tense_rejected():
    draft = "2028 emisyonu {{KPI:toplam_emisyon:2028:tahmin}} olarak gerçekleşmiştir [2]."
    errs = validate_draft(draft, RECORDS)
    assert any("kip hatası" in e for e in errs)


def test_r_ver_03_forecast_without_future_marker_rejected():
    draft = "2028 emisyonu {{KPI:toplam_emisyon:2028:tahmin}} düzeyindedir [2]."
    assert any("öngörü kipi" in e for e in validate_draft(draft, RECORDS))


@pytest.mark.parametrize(
    "sentence,kind,ok",
    [
        ("Emisyonun düşmesi öngörülmektedir.", "tahmin", True),
        ("Emisyon 2028'de azalacaktır.", "tahmin", True),
        ("Emisyon azalmıştır.", "tahmin", False),
        ("Emisyon ölçülmüştür.", "gerceklesmis", True),
        ("Emisyonun düşmesi beklenmektedir.", "gerceklesmis", False),
    ],
)
def test_r_ver_03_tense_rules(sentence, kind, ok):
    assert (check_sentence(sentence, kind) is None) is ok


def test_unknown_kind_raises():
    with pytest.raises(ValueError):
        check_sentence("x", "senaryo")
