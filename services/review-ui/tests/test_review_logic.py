"""Onay arayüzü mantık ve arayüz testleri (R-HIL-01)."""

import csv
import json
import shutil
from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from review_ui.logic import LABEL_HEADER, Paths, decide, pending

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "services/review-ui/app.py"


def _row(i: int, **kw) -> dict:
    return (
        dict.fromkeys(LABEL_HEADER, "")
        | {
            "etiket_id": f"e{i}",
            "tur": "paragraf",
            "rapor_id": "karel-2025",
            "paragraf_id": f"p{i}",
            "sayfa": "12",
            "metin": "Sürdürülebilirlik Komitesi üç ayda bir bilgilendirilir.",
            "madde_id": "TSRS2-YON-06a-iii",
            "karsilama": "2",
            "guven": "0.9",
            "gerekce": "Yöntem ve sıklık var (§4).",
            "etiketleyen": "claude",
            "kaynak": "model_onerisi",
            "tarih": "2026-10-22",
        }
        | kw
    )


@pytest.fixture
def data(tmp_path) -> Paths:
    p = Paths(tmp_path / "data")
    p.proposals.mkdir(parents=True)
    p.catalog_dir.mkdir(parents=True)
    shutil.copy(ROOT / "data/catalog/catalog_v0.csv", p.catalog_dir)
    with (p.proposals / "pilot-karel.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LABEL_HEADER)
        w.writeheader()
        w.writerows([_row(1), _row(2), _row(3)])
    return p


def _reviewed(p: Paths) -> list[dict]:
    with (p.reviewed / "pilot-karel.csv").open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_r_hil_01_approve_correct_reject(data):
    prop = data.proposals / "pilot-karel.csv"
    rows = pending(data, prop)
    d = date(2026, 10, 23)
    decide(data, prop, rows[0], "onayla", "Mehmet Güneş", today=d)
    decide(data, prop, rows[1], "duzelt", "Mehmet Güneş", "1", "Sıklık belirsiz", today=d)
    decide(data, prop, rows[2], "reddet", "Mehmet Güneş", gerekce="Yanlış madde", today=d)

    out = {r["etiket_id"]: r for r in _reviewed(data)}
    assert set(out) == {"e1", "e2"}  # reddedilen onaylı dosyaya girmez
    assert out["e1"]["kaynak"] == "insan_onayli" and out["e1"]["etiketleyen"] == "Mehmet Güneş"
    assert out["e2"]["kaynak"] == "insan" and out["e2"]["karsilama"] == "1"
    log = [json.loads(x) for x in data.log.read_text(encoding="utf-8").splitlines()]
    assert [x["karar"] for x in log] == ["onayla", "duzelt", "reddet"]
    assert pending(data, prop) == []


def test_r_hil_01_reviewed_output_passes_validator(data):
    from validate_data import validate_file

    prop = data.proposals / "pilot-karel.csv"
    for r in pending(data, prop):
        decide(data, prop, r, "onayla", "Mehmet Güneş")
    assert validate_file(data.reviewed / "pilot-karel.csv") == []


@pytest.mark.parametrize(
    "decision,kw,needle",
    [
        ("onayla", {"reviewer": " "}, "inceleyen"),
        ("duzelt", {"new_karsilama": None, "gerekce": "x"}, "yeni karşılama"),
        ("reddet", {"gerekce": ""}, "gerekçe"),
        ("sil", {}, "geçersiz"),
    ],
)
def test_r_hil_01_invalid_decisions(data, decision, kw, needle):
    prop = data.proposals / "pilot-karel.csv"
    row = pending(data, prop)[0]
    reviewer = kw.pop("reviewer", "Mehmet")
    with pytest.raises(ValueError, match=needle):
        decide(data, prop, row, decision, reviewer, **kw)


def test_r_hil_01_app_renders_and_approves(data, monkeypatch):
    monkeypatch.setenv("ECOIZGE_DATA_DIR", str(data.data))
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value.startswith("EcoIzge")
    at.text_input(key="reviewer").input("Mehmet Güneş").run()
    at.button(key="approve").click().run()
    assert not at.exception
    assert [r["etiket_id"] for r in _reviewed(data)] == ["e1"]
    assert len(pending(data, data.proposals / "pilot-karel.csv")) == 2
