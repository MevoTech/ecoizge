"""structure.py uçtan uca: tablo + olgu + şekil dosyaları, paragraf bağı, Docling resim sınıfları (R-TAB-01…04)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pymupdf = pytest.importorskip("pymupdf")
import extract  # noqa: E402
import structure as st  # noqa: E402
import tablo_kurallari as tk  # noqa: E402
from test_figures import _yatay  # noqa: E402
from test_tables import _cizgili_tablo  # noqa: E402


@pytest.fixture
def rapor(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    _cizgili_tablo(doc.new_page(width=595, height=842))
    _yatay(doc.new_page(width=595, height=842))
    doc.save(tmp_path / "rapor.pdf")
    return tmp_path / "rapor.pdf"


def test_r_tab_01_cli_uc_dosya_ve_paragraf_bagi(rapor, tmp_path, capsys):
    birimler = extract.extract(rapor, "karel-2025").units
    par = tmp_path / "paragraphs.jsonl"
    par.write_text("".join(json.dumps(u, ensure_ascii=False) + "\n" for u in birimler), encoding="utf-8")
    out = tmp_path / "cikti"
    assert (
        st.main([str(rapor), "--rapor-id", "karel-2025", "--out-dir", str(out), "--paragraflar", str(par)])
        == 0
    )
    assert "1 tablo" in capsys.readouterr().out
    tablolar = [json.loads(s) for s in (out / "tables.jsonl").read_text(encoding="utf-8").splitlines()]
    olgular = [json.loads(s) for s in (out / "facts.jsonl").read_text(encoding="utf-8").splitlines()]
    sekiller = [json.loads(s) for s in (out / "figures.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [tk.tablo_hatalari(t) for t in tablolar] == [[]]
    by_id = {t["tablo_id"]: t for t in tablolar}
    assert all(tk.olgu_hatalari(o, by_id) == [] for o in olgular) and len(olgular) == 4
    assert [tk.sekil_hatalari(s) for s in sekiller] == [[]]
    tablo_birimi = next(u for u in birimler if u["tur"] == "tablo")
    assert tablolar[0]["paragraf_id"] == tablo_birimi["paragraf_id"]
    # tablo alanı şekil sayılmaz; grafik 2. sayfada
    assert [s["sayfa"] for s in sekiller] == [2]


def test_r_tab_04_docling_resim_sinifi_eklenir_ve_grafik_resmi_kayit_olur():
    sekiller = [
        st.fg._kayit(
            "x-2025", 2, 1, [100, 100, 300, 250], "grafik", "", "", [], "yalniz_etiket", 0, "pymupdf", []
        )
    ]
    resimler = [
        {"sayfa": 2, "bbox": [105, 102, 298, 248], "baslik": "", "sinif": {"ad": "pie_chart", "guven": 0.97}},
        {
            "sayfa": 3,
            "bbox": [50, 50, 300, 300],
            "baslik": "Grafik 4",
            "sinif": {"ad": "bar_chart", "guven": 0.9},
        },
        {"sayfa": 3, "bbox": [400, 50, 450, 90], "baslik": "", "sinif": {"ad": "logo", "guven": 1.0}},
    ]
    out = st.resimleri_ekle(sekiller, resimler, "x-2025")
    assert [(s["sayfa"], s["sinif"]["ad"], s["veri_durumu"]) for s in out] == [
        (2, "pie_chart", "yalniz_etiket"),
        (3, "bar_chart", "goruntu_veri_yok"),
    ]
    assert all(tk.sekil_hatalari(s) == [] for s in out)
    assert out[1]["sekil_id"] == "x-2025-g003-01"


def test_r_tab_01_bilinmeyen_motor_reddedilir(rapor):
    with pytest.raises(ValueError):
        st.calistir(rapor, "karel-2025", motor="azure")


def test_r_tab_01_paragraf_bagi_bire_bir():
    t1 = {
        "sayfalar": [3],
        "baslik": "",
        "paragraf_id": None,
        "hucreler": [{"metin": "Kalem"}, {"metin": "2025"}],
    }
    t2 = {
        "sayfalar": [3],
        "baslik": "",
        "paragraf_id": None,
        "hucreler": [{"metin": "Kalem"}, {"metin": "2025"}],
    }
    birimler = [
        {"paragraf_id": "p1", "tur": "tablo", "sayfa": 3, "metin": "Kalem | 2025\nA | 1"},
        {"paragraf_id": "p2", "tur": "tablo", "sayfa": 3, "metin": "Kalem | 2025\nB | 2"},
    ]
    st.paragraflara_bagla([t1, t2], birimler)
    assert (t1["paragraf_id"], t2["paragraf_id"]) == ("p1", "p2")
