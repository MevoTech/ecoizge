"""Ekran testlerinin ortak fikstürü: geçici veri, rapor ve deney dizinleri."""

import json
import shutil

import pytest
from yardimci import KATALOG, _birim


@pytest.fixture
def veri(tmp_path, monkeypatch):
    """Geçici veri, rapor ve deney dizinleri; ekranlar bunları ortam değişkenlerinden okur."""
    data = tmp_path / "data"
    (data / "catalog").mkdir(parents=True)
    shutil.copy(KATALOG, data / "catalog")
    pilot = data / "labels" / "pilot"
    (pilot / "birimler").mkdir(parents=True)
    birimler = [_birim(i, sayfa=s) for s in (1, 2, 3) for i in range(1, 3)]
    (pilot / "birimler" / "sirket-ornek-2025.jsonl").write_text(
        "\n".join(json.dumps(b, ensure_ascii=False) for b in birimler), encoding="utf-8"
    )
    (pilot / "orneklem.jsonl").write_text(
        "\n".join(json.dumps(b, ensure_ascii=False) for b in birimler[:3]), encoding="utf-8"
    )
    # öneri dosyası körleme denetimi için: kör ekran bunu ASLA göstermemeli
    (data / "labels" / "proposals").mkdir(parents=True)
    (data / "labels" / "proposals" / "pilot.csv").write_text("GIZLI_MODEL_ONERISI", encoding="utf-8")
    raporlar = tmp_path / "raporlar" / "sirket"
    raporlar.mkdir(parents=True)
    import fitz

    doc = fitz.open()
    for s in range(3):
        doc.new_page().insert_text((72, 72), f"Sayfa {s + 1}")
    doc.save(raporlar / "ecoizge__sirket-ornek-2025.pdf")
    monkeypatch.setenv("ECOIZGE_DATA_DIR", str(data))
    monkeypatch.setenv("ECOIZGE_RAPOR_DIR", str(tmp_path / "raporlar"))
    monkeypatch.setenv("ECOIZGE_REPORTS_DIR", str(tmp_path / "deney"))
    return tmp_path
