"""Şekil ve grafik çıkarımı testleri (R-TAB-04, ADR-014).

Sentetik vektör grafikler: gruplu dikey çubuk (lejantlı, eksen işaretli), yatay çubuk, görüntü (raster)
grafik ve süs öğeleri. Değerler grafikte yazılı etiketlerden okunur; çubuk boyundan değer TAHMİN EDİLMEZ.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pymupdf = pytest.importorskip("pymupdf")
import figures as fg  # noqa: E402
import tablo_kurallari as tk  # noqa: E402

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
GRI, KIRMIZI = (0.6, 0.6, 0.6), (0.85, 0.0, 0.0)


def _yaz(page, x, y, metin, boyut=8):
    page.insert_text((x, y), metin, fontsize=boyut, fontname="dj", fontfile=FONT)


def _dikey_gruplu(page, ox=60, taban=400):
    """Akbank 2025 Şekil 5 benzeri: 3 kategori × 2 seri (2024 gri, 2025 kırmızı), etiketler çubuk üstünde."""
    veriler = [("A (Çok Yüksek)", 1, 6), ("B1 (Yüksek)", 5, 4), ("C (Düşük)", 0, 11)]
    _yaz(page, ox - 25, taban - 2, "0")  # eksen işaretleri: değer değildir
    _yaz(page, ox - 25, taban - 100, "10")
    for k, (kat, a, b) in enumerate(veriler):
        x = ox + k * 120
        for j, (deger, renk) in enumerate(((a, GRI), (b, KIRMIZI))):
            y0 = taban - deger * 10
            if deger:
                page.draw_rect(pymupdf.Rect(x + j * 22, y0, x + j * 22 + 18, taban), color=None, fill=renk)
            _yaz(page, x + j * 22 + 5, y0 - 4, str(deger))
        _yaz(page, x, taban + 14, kat)
    for j, (ad, renk) in enumerate((("2024", GRI), ("2025", KIRMIZI))):
        page.draw_rect(
            pymupdf.Rect(ox + 100 + j * 60, taban + 30, ox + 106 + j * 60, taban + 36), color=None, fill=renk
        )
        _yaz(page, ox + 110 + j * 60, taban + 36, ad)
    _yaz(page, ox, taban + 60, "Şekil 5: Çevresel ve sosyal etki değerlendirmesi kapsamında proje sayısı", 9)


def _yatay(page, ox=120, ust=100):
    """Akbank 2025 Şekil 6 benzeri: kategori solda, değer çubuğun sağında."""
    veriler = [("Toplam", 27), ("Lojistik", 1), ("Enerji", 5), ("İmalat", 8)]
    for i, (kat, deger) in enumerate(veriler):
        y = ust + i * 24
        _yaz(page, ox - 70, y + 12, kat)
        page.draw_rect(pymupdf.Rect(ox, y, ox + deger * 10, y + 16), color=None, fill=KIRMIZI)
        _yaz(page, ox + deger * 10 + 6, y + 12, str(deger))
    _yaz(page, ox - 70, ust + 4 * 24 + 20, "Şekil 6: Sektör bazında değerlendirilen kredi sayısı", 9)


@pytest.fixture
def grafik_pdf(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    _yaz(page, 50, 60, "Bu bölümde proje sayıları 2024 ve 2025 yılları için sunulmaktadır.", 9)
    _dikey_gruplu(page)
    page2 = doc.new_page(width=595, height=842)
    _yatay(page2)
    page2.draw_rect(pymupdf.Rect(20, 20, 30, 30), color=None, fill=KIRMIZI)  # süs: küçük kare
    doc.save(tmp_path / "grafik.pdf")
    return tmp_path / "grafik.pdf"


@pytest.fixture
def raster_pdf(tmp_path: Path) -> Path:
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 200, 120), False)
    pix.clear_with(200)
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_image(pymupdf.Rect(0, 0, 595, 842), pixmap=pix)  # tam sayfa arka plan: şekil değil
    page.insert_image(pymupdf.Rect(100, 200, 400, 380), pixmap=pix)
    _yaz(page, 100, 395, "Grafik 2: Yıllara göre enerji yoğunluğu", 9)
    doc.save(tmp_path / "raster.pdf")
    return tmp_path / "raster.pdf"


def test_r_tab_04_dikey_gruplu_cubuk_etiket_kategori_seri(grafik_pdf):
    sekiller = [s for s in fg.cikar(grafik_pdf, "akbank-2025") if s["sayfa"] == 1]
    assert len(sekiller) == 1
    s = sekiller[0]
    assert tk.sekil_hatalari(s) == []
    assert (s["tur"], s["veri_durumu"]) == ("grafik", "vektor_etiket")
    assert s["baslik"].startswith("Şekil 5:")
    assert {(v["kategori"], v["seri"], v["deger"]) for v in s["veri"]} == {
        ("A (Çok Yüksek)", "2024", 1), ("A (Çok Yüksek)", "2025", 6),
        ("B1 (Yüksek)", "2024", 5), ("B1 (Yüksek)", "2025", 4),
        ("C (Düşük)", "2025", 11),
    }  # fmt: skip
    # çubuğu olmayan "0" etiketi uydurulmaz; eşleşmeyen sayılır. Eksen işaretleri (0, 10) değer değildir
    assert s["eslesmeyen_etiket"] == 1


def test_r_tab_04_yatay_cubuk(grafik_pdf):
    sekiller = [s for s in fg.cikar(grafik_pdf, "akbank-2025") if s["sayfa"] == 2]
    assert len(sekiller) == 1  # köşedeki küçük kare süs, şekil değil
    s = sekiller[0]
    assert tk.sekil_hatalari(s) == []
    assert [(v["kategori"], v["seri"], v["deger"]) for v in s["veri"]] == [
        ("Toplam", None, 27),
        ("Lojistik", None, 1),
        ("Enerji", None, 5),
        ("İmalat", None, 8),
    ]
    assert s["eslesmeyen_etiket"] == 0
    assert s["baslik"].startswith("Şekil 6:")


def test_r_tab_04_raster_grafikte_veri_uydurulmaz(raster_pdf):
    sekiller = fg.cikar(raster_pdf, "x-2025")
    assert len(sekiller) == 1  # tam sayfa arka plan atlandı
    s = sekiller[0]
    assert tk.sekil_hatalari(s) == []
    assert (s["tur"], s["veri_durumu"], s["veri"]) == ("grafik", "goruntu_veri_yok", [])
    assert "goruntu_veri_cikarilmadi" in s["uyarilar"]
    assert s["baslik"] == "Grafik 2: Yıllara göre enerji yoğunluğu"


def test_r_tab_04_tablo_alani_sekil_sayilmaz(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    for r in range(4):
        for c in range(3):
            page.draw_rect(
                pymupdf.Rect(50 + c * 100, 100 + r * 20, 150 + c * 100, 120 + r * 20),
                color=(0, 0, 0),
                fill=GRI if r == 0 else None,
            )
            _yaz(page, 55 + c * 100, 114 + r * 20, f"{r * 10 + c}")
    doc.save(tmp_path / "t.pdf")
    assert fg.cikar(tmp_path / "t.pdf", "x-2025", tablo_alanlari={1: [[50, 100, 350, 180]]}) == []


def test_r_tab_04_cubuk_eslestirme_saf_fonksiyon():
    """Geometri: etiket çubuğun hemen üstünde ve ortasında; kategori tabanın altında; seri lejanttan."""
    cubuklar = [{"bbox": [10, 50, 20, 100], "renk": KIRMIZI}, {"bbox": [40, 80, 50, 100], "renk": KIRMIZI}]
    metinler = [
        {"bbox": [12, 40, 18, 48], "metin": "5"},
        {"bbox": [42, 70, 48, 78], "metin": "2"},
        {"bbox": [5, 104, 25, 112], "metin": "Ocak"},
        {"bbox": [35, 104, 55, 112], "metin": "Şubat"},
        {"bbox": [70, 40, 90, 48], "metin": "12,5"},  # hiçbir çubuğa ait değil
    ]
    veri, eslesmeyen = fg.cubuk_verisi(cubuklar, metinler, lejant={})
    assert [(v["kategori"], v["deger"]) for v in veri] == [("Ocak", 5), ("Şubat", 2)]
    assert eslesmeyen == 1


def test_r_tab_04_tablo_baslik_dolgusu_grafik_sanilmaz(tmp_path):
    """Akbank 2025 s. 6: tablonun kırmızı dolgulu başlık hücreleri ('2024', '2025') çubuk sanılıyordu.
    Eşit boylu dolgular ve yıl etiketleri çubuk grafik verisi değildir."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    for i, yil in enumerate(["2023", "2024", "2025"]):
        page.draw_rect(pymupdf.Rect(200 + i * 80, 100, 270 + i * 80, 118), color=None, fill=KIRMIZI)
        _yaz(page, 220 + i * 80, 112, yil)
        _yaz(page, 220 + i * 80, 140, f"{(i + 1) * 1250}")
    doc.save(tmp_path / "t.pdf")
    assert [s for s in fg.cikar(tmp_path / "t.pdf", "x-2025") if s["veri_durumu"] == "vektor_etiket"] == []
