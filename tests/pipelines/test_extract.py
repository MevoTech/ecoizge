"""PDF çıkarım testleri (R-PDF-01). Sentetik, Türkçe karakterli bir PDF üretilip çıkarılır.

PyMuPDF requirements-train.txt'tedir; kurulu değilse (CI) testler atlanır ve bu PROGRESS'te yazılıdır.
"""

from pathlib import Path

import pytest

pymupdf = pytest.importorskip("pymupdf")
from extract import extract, join_lines  # noqa: E402

FONT = next(
    (
        p
        for p in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        if Path(p).exists()
    ),
    None,
)


def _make_pdf(path: Path) -> Path:
    doc = pymupdf.open()
    for pno in (1, 2):
        page = doc.new_page(width=595, height=842)

        def put(y, text, size=10, page=page):
            page.insert_text((50, y), text, fontsize=size, fontname="dj", fontfile=FONT)

        put(30, "Karel Sürdürülebilirlik Raporu 2025", 8)  # üst bilgi (her sayfada)
        put(825, f"Sayfa {pno}", 8)  # alt bilgi
        if pno == 1:
            put(120, "Yönetişim", 18)
            put(160, "Sürdürülebilirlik Komitesi iklim konularında yönetimden üç ayda bir")
            put(173, "yazılı rapor alır ve yılda iki kez kurula sunum yapar.")
            put(210, "Şirketimiz iklimle ilgili riskleri sürdürüle-")
            put(223, "bilirlik stratejisinin merkezine almıştır.")
        else:
            put(120, "Metrikler", 18)
            put(160, "Tablo 1. Sera gazı emisyonları")
            x0, y0, w, h = 50, 175, 240, 22
            rows = [["Kapsam", "2024 (tCO2e)"], ["Kapsam 1", "12.450"], ["Kapsam 2", "31.200"]]
            for r, row in enumerate(rows):
                for c, cell in enumerate(row):
                    rect = pymupdf.Rect(x0 + c * w, y0 + r * h, x0 + (c + 1) * w, y0 + (r + 1) * h)
                    page.draw_rect(rect, color=(0, 0, 0), width=0.8)
                    page.insert_text(
                        (rect.x0 + 4, rect.y0 + 15), cell, fontsize=10, fontname="dj", fontfile=FONT
                    )
            put(300, "Kapsam 3 emisyonları geçiş hükmü kapsamında bu dönemde açıklanmamıştır.")
    doc.save(path)
    return path


@pytest.fixture
def units(tmp_path):
    if FONT is None:
        pytest.skip("Türkçe glifli yazı tipi yok")
    return extract(_make_pdf(tmp_path / "r.pdf"), "test-2025")


def test_join_lines_hyphenation():
    assert join_lines(["sürdürüle-", "bilirlik raporu"]) == "sürdürülebilirlik raporu"
    assert join_lines(["Kapsam 1-", "Kapsam 2"]) == "Kapsam 1- Kapsam 2"  # büyük harfle devam: birleştirme


def test_r_pdf_01_headers_footers_removed(units):
    texts = [u["metin"] for u in units.units]
    assert not any("Karel Sürdürülebilirlik Raporu" in t for t in texts)
    assert not any(t.startswith("Sayfa") for t in texts)
    assert units.atilan_ust_alt >= 4


def test_r_pdf_01_heading_context_and_turkish_text(units):
    p1 = [u for u in units.units if u["sayfa"] == 1]
    assert p1 and all(u["bolum_basligi"] == "Yönetişim" for u in p1)
    joined = " ".join(u["metin"] for u in p1)
    assert "üç ayda bir yazılı rapor alır" in joined
    assert "sürdürülebilirlik stratejisinin" in joined  # tireleme birleşti


def test_r_pdf_01_table_with_caption_is_one_unit(units):
    tables = [u for u in units.units if u["tur"] == "tablo"]
    assert len(tables) == 1
    t = tables[0]
    assert t["metin"].startswith("Tablo 1. Sera gazı emisyonları")
    assert "Kapsam 1 | 12.450" in t["metin"]
    assert t["bolum_basligi"] == "Metrikler"
    cells_as_paragraphs = [u for u in units.units if u["tur"] == "paragraf" and "12.450" in u["metin"]]
    assert cells_as_paragraphs == []


def test_r_pdf_01_ids_pages_and_order(units):
    ids = [u["paragraf_id"] for u in units.units]
    assert len(ids) == len(set(ids))
    p2 = [u for u in units.units if u["sayfa"] == 2]
    assert [u["tur"] for u in p2] == ["tablo", "paragraf"]
    assert all(u["kaynak"] == "metin" for u in units.units)


def test_page_without_text_layer_flagged(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page()
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 40, 40), 0)
    pix.clear_with(200)
    page.insert_image(pymupdf.Rect(50, 50, 300, 300), pixmap=pix)
    doc.save(tmp_path / "scan.pdf")
    res = extract(tmp_path / "scan.pdf", "tarama")
    assert res.ocr_gerekli == [1] and res.units == []
