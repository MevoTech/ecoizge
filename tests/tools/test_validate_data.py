"""Katalog ve etiket doğrulayıcı testleri (R-KAT-01, R-ETK-01)."""

import csv
import shutil
from pathlib import Path

from validate_data import CATALOG_HEADER, LABEL_HEADER, validate_file

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/catalog/catalog_v0.csv"


def test_r_kat_01_current_catalog_is_valid():
    assert validate_file(CATALOG) == []


def test_r_kat_01_detects_duplicate_and_bad_enum(tmp_path):
    rows = list(csv.reader(CATALOG.open(encoding="utf-8")))
    rows.append(rows[1])  # yinelenen madde_id
    bad = list(rows[2])
    bad[0] = "X-1"
    bad[6] = "belki"  # zorunluluk
    bad[10] = "kaynak?"  # dogrulama
    rows.append(bad)
    p = tmp_path / "catalog_v9.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(rows)
    errs = validate_file(p)
    assert any("yinelenen madde_id" in e for e in errs)
    assert any("zorunluluk='belki'" in e for e in errs)
    assert any("dogrulama=" in e for e in errs)


def _label(**kw) -> dict:
    base = dict.fromkeys(LABEL_HEADER, "")
    base |= {
        "etiket_id": "e1",
        "tur": "paragraf",
        "paragraf_id": "p1",
        "madde_id": "TSRS2-YON-06a",
        "karsilama": "2",
        "guven": "0.8",
        "gerekce": "Organ adı açıkça verilmiş (§4).",
        "etiketleyen": "claude",
        "kaynak": "model_onerisi",
        "tarih": "2026-10-22",
    }
    return base | kw


def _write(path: Path, rows: list[dict]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LABEL_HEADER)
        w.writeheader()
        w.writerows(rows)
    return path


def test_r_etk_01_valid_label_rows(tmp_path):
    rows = [_label(), _label(etiket_id="e2", madde_id="NONE", karsilama="NONE")]
    rows.append(_label(etiket_id="e3", tur="rapor_duzeyi", paragraf_id="", karsilama="0", kaynak="insan"))
    assert validate_file(_write(tmp_path / "ok.csv", rows)) == []


def test_r_etk_01_label_errors_detected(tmp_path):
    rows = [
        _label(karsilama="3"),
        _label(etiket_id="e2", madde_id="YOK-1"),
        _label(etiket_id="e3", guven="", gerekce=""),
        _label(etiket_id="e4", madde_id="NONE", karsilama="1"),
        _label(etiket_id="e5", tur="rapor_duzeyi", paragraf_id="", karsilama="2"),
        _label(etiket_id="e5", tarih="22.10.2026"),
    ]
    errs = validate_file(_write(tmp_path / "bad.csv", rows))
    joined = "\n".join(errs)
    for needle in [
        "karsilama='3'",
        "katalogda yok",
        "guven zorunlu",
        "gerekce zorunlu",
        "madde_id=NONE ise",
        "rapor_duzeyi için karsilama='2'",
        "yinelenen etiket_id",
        "YYYY-AA-GG",
    ]:
        assert needle in joined, needle


def test_unknown_header(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("a,b\n1,2\n", encoding="utf-8")
    assert "tanınmayan başlık" in validate_file(p)[0]


def test_template_header_matches(tmp_path):
    shutil.copy(ROOT / "data/labels/etiket_sablonu.csv", tmp_path / "t.csv")
    assert validate_file(tmp_path / "t.csv") == []
    assert CATALOG_HEADER[0] == "madde_id"
