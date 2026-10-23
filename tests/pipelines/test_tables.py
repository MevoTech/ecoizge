"""Yapısal tablo çıkarımı testleri (R-TAB-01, R-TAB-02, R-TAB-03; ADR-014).

Sentetik Türkçe PDF'ler: kenarlıklı ve birleşik başlıklı tablo, kenarlıksız (yalnızca hizalı) tablo,
iki sayfaya bölünen tablo. Beklenen ızgara, başlık ve olgular elle yazıldı (gerçek veri değil).
"""

from __future__ import annotations

from pathlib import Path

import pytest

pymupdf = pytest.importorskip("pymupdf")
import tables as tb  # noqa: E402
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


def _yaz(page, x, y, metin, boyut=9):
    page.insert_text((x, y), metin, fontsize=boyut, fontname="dj", fontfile=FONT)


def _kutu(page, x0, y0, x1, y1, metin=""):
    page.draw_rect(pymupdf.Rect(x0, y0, x1, y1), color=(0, 0, 0), width=0.7)
    if metin:
        _yaz(page, x0 + 3, y0 + 13, metin)


def _cizgili_tablo(page, y0=120):
    """İki düzey başlık: 'Kapsam' iki satır kaplar, 'Emisyon (tCO2e)' iki sütun kaplar."""
    _yaz(page, 50, y0 - 8, "Tablo 1. Sera gazı emisyonları", 10)
    x = [50, 170, 270, 370]
    h = 20
    _kutu(page, x[0], y0, x[1], y0 + 2 * h, "Kapsam")
    _kutu(page, x[1], y0, x[3], y0 + h, "Emisyon (tCO2e)")
    _kutu(page, x[1], y0 + h, x[2], y0 + 2 * h, "2024")
    _kutu(page, x[2], y0 + h, x[3], y0 + 2 * h, "2025")
    satirlar = [["Kapsam 1", "12.450", "13.100*"], ["Kapsam 2", "31.200", "-"]]
    for i, satir in enumerate(satirlar):
        yy = y0 + (2 + i) * h
        for j, metin in enumerate(satir):
            _kutu(page, x[j], yy, x[j + 1], yy + h, metin)
    _yaz(page, 50, y0 + 4 * h + 14, "* Bağımsız güvence kapsamında değildir.", 7)


@pytest.fixture
def cizgili_pdf(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    _cizgili_tablo(doc.new_page(width=595, height=842))
    doc.save(tmp_path / "cizgili.pdf")
    return tmp_path / "cizgili.pdf"


@pytest.fixture
def kenarliksiz_pdf(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    _yaz(page, 50, 80, "Su yönetimi", 16)
    _yaz(page, 50, 120, "Tablo 2: Tesis bazında su çekimi (m³)", 10)
    satirlar = [["Tesis", "2024", "2025"], ["Manisa", "12.450", "11.900"], ["Gebze", "8.300", "8.120"]]
    for i, satir in enumerate(satirlar):
        for j, metin in enumerate(satir):
            _yaz(page, [50, 200, 300][j], 150 + i * 18, metin)
    _yaz(page, 50, 260, "Su çekimi bir önceki yıla göre azalmıştır ve hedeflerle uyumludur.", 9)
    doc.save(tmp_path / "kenarliksiz.pdf")
    return tmp_path / "kenarliksiz.pdf"


@pytest.fixture
def bolunen_pdf(tmp_path: Path) -> Path:
    """Tablo 1. sayfanın altından başlar, 2. sayfada başlık satırı tekrar edilerek sürer."""
    doc = pymupdf.open()
    x = [50, 200, 330]
    for sayfa, (ust, satirlar) in enumerate(
        [(700, [["Gösterge", "Değer (MWh)"], ["Elektrik", "1.200"], ["Doğal gaz", "3.400"]]),
         (60, [["Gösterge", "Değer (MWh)"], ["Buhar", "450"], ["Toplam", "5.050"]])]
    ):  # fmt: skip
        page = doc.new_page(width=595, height=842)
        if sayfa == 0:
            _yaz(page, 50, ust - 8, "Tablo 3. Enerji tüketimi", 10)
        for i, satir in enumerate(satirlar):
            for j, metin in enumerate(satir):
                _kutu(page, x[j], ust + i * 20, x[j + 1], ust + (i + 1) * 20, metin)
    doc.save(tmp_path / "bolunen.pdf")
    return tmp_path / "bolunen.pdf"


def _metin_izgarasi(t: dict) -> list[list[str]]:
    g = tk.izgara(t)
    return [[t["hucreler"][i]["metin"] for i in row] for row in g]


# ---------- R-TAB-01: hücre ızgarası ----------


def test_r_tab_01_cizgili_tablo_izgara_kapsam_ve_baslik(cizgili_pdf):
    tablolar = tb.cikar(cizgili_pdf, "karel-2025")
    assert len(tablolar) == 1
    t = tablolar[0]
    assert tk.tablo_hatalari(t) == []
    assert t["tablo_id"] == "karel-2025-t001-01"
    assert t["motor"] == "pymupdf"
    assert (t["satir_sayisi"], t["sutun_sayisi"]) == (4, 3)
    assert t["baslik"] == "Tablo 1. Sera gazı emisyonları"
    assert _metin_izgarasi(t) == [
        ["Kapsam", "Emisyon (tCO2e)", "Emisyon (tCO2e)"],
        ["Kapsam", "2024", "2025"],
        ["Kapsam 1", "12.450", "13.100*"],
        ["Kapsam 2", "31.200", "-"],
    ]
    kapsam = next(h for h in t["hucreler"] if h["metin"] == "Kapsam")
    emisyon = next(h for h in t["hucreler"] if h["metin"] == "Emisyon (tCO2e)")
    assert (kapsam["satir_kapsam"], kapsam["sutun_kapsam"]) == (2, 1)
    assert (emisyon["satir_kapsam"], emisyon["sutun_kapsam"]) == (1, 2)
    assert {h["metin"] for h in t["hucreler"] if h["sutun_basligi"]} == {
        "Kapsam",
        "Emisyon (tCO2e)",
        "2024",
        "2025",
    }
    assert {h["metin"] for h in t["hucreler"] if h["satir_basligi"]} == {"Kapsam 1", "Kapsam 2"}
    assert t["dipnotlar"] == ["* Bağımsız güvence kapsamında değildir."]


def test_r_tab_01_turkce_binlik_ayraci_hucrede_korunur(cizgili_pdf):
    t = tb.cikar(cizgili_pdf, "karel-2025")[0]
    assert "12.450" in {h["metin"] for h in t["hucreler"]}


@pytest.mark.parametrize("motorlar", [("pymupdf-bosluk",), tb.MOTORLAR_VARSAYILAN])
def test_r_tab_01_hizali_kenarliksiz_tablo_bulunur(kenarliksiz_pdf, motorlar):
    """Düzenli hizalı kenarlıksız tabloyu find_tables de buluyor (2026-10-23 denemesi); sezgisel yöntem de."""
    tablolar = tb.cikar(kenarliksiz_pdf, "karel-2025", motorlar)
    assert len(tablolar) == 1
    t = tablolar[0]
    assert tk.tablo_hatalari(t) == []
    assert t["baslik"] == "Tablo 2: Tesis bazında su çekimi (m³)"
    assert _metin_izgarasi(t) == [
        ["Tesis", "2024", "2025"],
        ["Manisa", "12.450", "11.900"],
        ["Gebze", "8.300", "8.120"],
    ]
    # tablonun altındaki paragraf tabloya karışmaz
    assert all("azalmıştır" not in h["metin"] for h in t["hucreler"])


@pytest.fixture
def blok_sutunlu_pdf(tmp_path: Path) -> Path:
    """Klimasan 2025 s. 37 benzeri: kenarlıksız, her sütunda dikey ortalanmış çok satırlı metin bloğu."""
    doc = pymupdf.open()
    page = doc.new_page(width=842, height=595)
    _yaz(page, 40, 70, "Tablo 4: İklimle ilgili fırsatlar", 10)
    for x, m in zip(
        [40, 180, 330, 480], ["Fırsat Adı", "Fırsat Tanımı", "Ölçüm Metrikleri", "Finansal Etki"], strict=True
    ):
        _yaz(page, x, 100, m)
    sutunlar = {
        40: ["Enerji verimliliği"],
        180: ["Üretim tesislerinde", "enerji yoğun proseslerde", "verimlilik artışı"],
        330: ["Geri dönüş süresi,", "birim ürün başına enerji", "yoğunluğu ve yıllık", "tasarruf miktarı"],
        480: ["Yatırım tutarı", "805.299 TL"],
    }
    for x, satirlar in sutunlar.items():
        ust = 150 - len(satirlar) * 6  # dikey ortalama
        for i, m in enumerate(satirlar):
            _yaz(page, x, ust + i * 12, m)
    _yaz(
        page,
        40,
        260,
        "Bu fırsatlar, şirketin geçiş planında yer alan yatırımlarla birlikte izlenmektedir ve raporlanır.",
    )
    doc.save(tmp_path / "blok.pdf")
    return tmp_path / "blok.pdf"


@pytest.mark.parametrize("motorlar", [("pymupdf-bosluk",), tb.MOTORLAR_VARSAYILAN])
def test_r_tab_01_blok_sutunlu_kenarliksiz_tablo(blok_sutunlu_pdf, motorlar):
    """Sezgisel yöntem tek başına da, find_tables ile birlikte de aynı ızgarayı verir."""
    tablolar = tb.cikar(blok_sutunlu_pdf, "karel-2025", motorlar)
    assert len(tablolar) == 1
    t = tablolar[0]
    assert tk.tablo_hatalari(t) == []
    if motorlar == ("pymupdf-bosluk",):
        assert t["motor"] == "pymupdf-bosluk" and "kenarliksiz_sezgisel" in t["uyarilar"]
    assert t["baslik"] == "Tablo 4: İklimle ilgili fırsatlar"
    assert _metin_izgarasi(t) == [
        ["Fırsat Adı", "Fırsat Tanımı", "Ölçüm Metrikleri", "Finansal Etki"],
        [
            "Enerji verimliliği",
            "Üretim tesislerinde enerji yoğun proseslerde verimlilik artışı",
            "Geri dönüş süresi, birim ürün başına enerji yoğunluğu ve yıllık tasarruf miktarı",
            "Yatırım tutarı 805.299 TL",
        ],
    ]
    assert all("izlenmektedir" not in h["metin"] for h in t["hucreler"])


def test_r_tab_01_basliksiz_metin_tablo_sanilmaz(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    for i in range(6):
        _yaz(
            page,
            50,
            100 + i * 14,
            f"Şirketimiz {2020 + i} yılında iklim stratejisini güncellemiştir ve izlemiştir.",
        )
    doc.save(tmp_path / "duz.pdf")
    assert tb.cikar(tmp_path / "duz.pdf", "karel-2025") == []
    assert tb.cikar(tmp_path / "duz.pdf", "karel-2025", ("pymupdf-bosluk",)) == []


# ---------- R-TAB-03: sayfalar arası birleştirme (KL-02) ----------


def test_r_tab_03_bolunen_tablo_birlesir_tekrar_baslik_atilir(bolunen_pdf):
    tablolar = tb.cikar(bolunen_pdf, "karel-2025")
    assert len(tablolar) == 1
    t = tablolar[0]
    assert tk.tablo_hatalari(t) == []
    assert t["sayfalar"] == [1, 2]
    assert [p["sayfa"] for p in t["parcalar"]] == [1, 2]
    assert "sayfalar_arasi_birlestirildi" in t["uyarilar"]
    assert _metin_izgarasi(t) == [
        ["Gösterge", "Değer (MWh)"],
        ["Elektrik", "1.200"],
        ["Doğal gaz", "3.400"],
        ["Buhar", "450"],
        ["Toplam", "5.050"],
    ]
    assert [h["sayfa"] for h in t["hucreler"] if h["metin"] in ("Buhar", "Elektrik")] == [1, 2]


def test_r_tab_03_farkli_sutun_sayisi_birlesmez():
    a = _elle_tablo(1, [["A", "B"], ["x", "1"]], alt=800)
    b = _elle_tablo(2, [["A", "B", "C"], ["y", "2", "3"]], ust=50)
    assert len(tb.sayfalari_birlestir([a, b], {1: 842.0, 2: 842.0})) == 2


def test_r_tab_03_baslikli_yeni_tablo_birlesmez():
    a = _elle_tablo(1, [["A", "B"], ["x", "1"]], alt=800)
    b = _elle_tablo(2, [["A", "B"], ["y", "2"]], ust=50, baslik="Tablo 9. Başka tablo")
    assert len(tb.sayfalari_birlestir([a, b], {1: 842.0, 2: 842.0})) == 2


def _elle_tablo(sayfa, satirlar, *, ust=100.0, alt=None, baslik=""):
    n = len(satirlar)
    if alt is not None:  # tablonun alt kenarı verildiyse üst kenar ondan hesaplanır
        ust = alt - 20 * n
    hucreler = [
        {
            "satir": r,
            "sutun": c,
            "satir_kapsam": 1,
            "sutun_kapsam": 1,
            "metin": m,
            "sutun_basligi": r == 0,
            "satir_basligi": False,
            "bolum_satiri": False,
            "sayfa": sayfa,
            "bbox": [50.0 + 100 * c, ust + 20 * r, 150.0 + 100 * c, ust + 20 * (r + 1)],
        }  # fmt: skip
        for r, satir in enumerate(satirlar)
        for c, m in enumerate(satir)
    ]
    return tb.tablo_kaydi(
        "karel-2025", sayfa, 1, hucreler, n, len(satirlar[0]), "pymupdf",
        [50.0, ust, 50.0 + 100 * len(satirlar[0]), ust + 20 * n], baslik=baslik,
    )  # fmt: skip


# ---------- R-TAB-02: olgular (değer + satır/sütun yolu + birim + dönem) ----------


def test_r_tab_02_olgular_cok_duzeyli_baslik_birim_donem(cizgili_pdf):
    t = tb.cikar(cizgili_pdf, "karel-2025")[0]
    olgular = tb.olgular(t)
    assert all(tk.olgu_hatalari(o, {t["tablo_id"]: t}) == [] for o in olgular)
    ozet = {(tuple(o["satir_yolu"]), o["donem"]): o for o in olgular}
    k1 = ozet[(("Kapsam 1",), "2024")]
    assert (k1["deger"], k1["birim"], k1["birim_kaynagi"]) == (12450, "tCO2e", "sutun_basligi")
    assert k1["sutun_yolu"] == ["Emisyon (tCO2e)", "2024"]
    k1b = ozet[(("Kapsam 1",), "2025")]
    assert (k1b["deger"], k1b["dipnot"]) == (13100, ["*"])
    k2b = ozet[(("Kapsam 2",), "2025")]
    assert k2b["eksik"] and k2b["deger"] is None
    assert len(olgular) == 4  # başlıktaki 2024 / 2025 olgu değildir


def test_r_tab_02_birim_tablo_basligindan_ve_carpan():
    t = _elle_tablo(
        1, [["Kalem", "2025"], ["Yatırım", "1.250"], ["Pay", "%12,5"]], baslik="Tablo 4. Yatırımlar (Bin TL)"
    )
    ozet = {o["satir_yolu"][0]: o for o in tb.olgular(t)}
    assert (ozet["Yatırım"]["deger"], ozet["Yatırım"]["birim"], ozet["Yatırım"]["carpan"]) == (
        1_250_000,
        "TL",
        1000.0,
    )
    assert ozet["Yatırım"]["birim_kaynagi"] == "tablo_basligi"
    # hücredeki birim başlıktakinden önce gelir
    assert (ozet["Pay"]["deger"], ozet["Pay"]["birim"], ozet["Pay"]["carpan"]) == (12.5, "%", 1.0)


def test_r_tab_02_bolum_satiri_satir_yoluna_girer():
    t = _elle_tablo(
        1,
        [["Gösterge", "2025"], ["Kapsam 1", ""], ["Doğal gaz", "120"], ["Kapsam 2", ""], ["Elektrik", "340"]],
    )
    tb.basliklari_belirle(t)
    ozet = {o["satir_yolu"][-1]: o for o in tb.olgular(t)}
    assert ozet["Doğal gaz"]["satir_yolu"] == ["Kapsam 1", "Doğal gaz"]
    assert ozet["Elektrik"]["satir_yolu"] == ["Kapsam 2", "Elektrik"]


def test_r_tab_02_olgu_metni_rag_icin_dogrusal():
    t = _elle_tablo(1, [["Kapsam", "2024 (tCO2e)"], ["Kapsam 1", "12.450"]], baslik="Tablo 1. Emisyonlar")
    o = tb.olgular(t)[0]
    assert tb.olgu_metni(o, t) == "Tablo 1. Emisyonlar · Kapsam 1 · 2024 (tCO2e): 12.450"


# ---------- docling uyarlayıcısı (motor bağımsız şema) ----------


def test_r_tab_01_docling_verisi_ayni_semaya_donusur():
    veri = {
        "num_rows": 2,
        "num_cols": 2,
        "table_cells": [
            {"start_row_offset_idx": 0, "end_row_offset_idx": 1, "start_col_offset_idx": 0, "end_col_offset_idx": 2,
             "row_span": 1, "col_span": 2, "text": "Emisyon (tCO2e)", "column_header": True, "row_header": False,
             "row_section": False, "bbox": {"l": 50, "t": 742, "r": 250, "b": 722, "coord_origin": "BOTTOMLEFT"}},
            {"start_row_offset_idx": 1, "end_row_offset_idx": 2, "start_col_offset_idx": 0, "end_col_offset_idx": 1,
             "row_span": 1, "col_span": 1, "text": "Kapsam 1", "column_header": False, "row_header": True,
             "row_section": False, "bbox": None},
            {"start_row_offset_idx": 1, "end_row_offset_idx": 2, "start_col_offset_idx": 1, "end_col_offset_idx": 2,
             "row_span": 1, "col_span": 1, "text": "12.450", "column_header": False, "row_header": False,
             "row_section": False, "bbox": {"l": 150, "t": 120, "r": 250, "b": 140, "coord_origin": "TOPLEFT"}},
        ],
    }  # fmt: skip
    t = tb.docling_tablosu(
        veri, "karel-2025", sayfa=3, sira=1, bbox=[50, 100, 250, 140], baslik="Tablo 1", sayfa_yuksekligi=842
    )
    assert tk.tablo_hatalari(t) == []
    assert t["motor"] == "docling"
    emisyon = t["hucreler"][0]
    assert emisyon["sutun_kapsam"] == 2 and emisyon["sutun_basligi"]
    assert emisyon["bbox"] == [50, 100, 250, 120]  # alt-sol orijinden üst-sola çevrildi
    o = tb.olgular(t)[0]
    assert (o["deger"], o["birim"], o["satir_yolu"], o["sutun_yolu"]) == (
        12450,
        "tCO2e",
        ["Kapsam 1"],
        ["Emisyon (tCO2e)"],
    )


def test_r_tab_01_docling_bos_konumlar_bos_hucreyle_doldurulur():
    veri = {"num_rows": 1, "num_cols": 2, "table_cells": [
        {"start_row_offset_idx": 0, "end_row_offset_idx": 1, "start_col_offset_idx": 0, "end_col_offset_idx": 1,
         "row_span": 1, "col_span": 1, "text": "A", "column_header": False, "row_header": False, "row_section": False, "bbox": None}]}  # fmt: skip
    t = tb.docling_tablosu(
        veri, "karel-2025", sayfa=1, sira=1, bbox=[0, 0, 10, 10], baslik="", sayfa_yuksekligi=842
    )
    assert tk.tablo_hatalari(t) == []
    assert _metin_izgarasi(t) == [["A", ""]]


# ---------- şema değişmezleri ----------


def test_r_tab_01_izgara_cakisma_ve_bosluk_yakalanir():
    t = _elle_tablo(1, [["A", "B"], ["x", "1"]])
    t["hucreler"][0]["sutun_kapsam"] = 2  # B ile çakışır
    assert any("iki hücrede" in h for h in tk.tablo_hatalari(t))
    t = _elle_tablo(1, [["A", "B"], ["x", "1"]])
    t["hucreler"].pop()
    assert any("kaplanmayan" in h for h in tk.tablo_hatalari(t))


def test_r_tab_02_olgu_kaynakla_tutarsizsa_yakalanir():
    t = _elle_tablo(1, [["Kalem", "2025"], ["Yatırım", "1.250"]])
    o = tb.olgular(t)[0]
    assert tk.olgu_hatalari(o, {t["tablo_id"]: t}) == []
    assert any("değer" in h for h in tk.olgu_hatalari(o | {"deger": 1250.5}, {t["tablo_id"]: t}))
    assert any("ham" in h for h in tk.olgu_hatalari(o | {"ham": "1.205"}, {t["tablo_id"]: t}))


# ---------- gerçek raporlarda bulunan hatalar (2026-10-23, regresyon) ----------


def test_r_tab_02_yil_hucresine_birim_verilmez():
    """QUA Granite 2025 s. 42: 'Hedef Yılı' sütunundaki 2035, satırdaki tCO2e birimini almıştı."""
    t = _elle_tablo(1, [["Hedef", "Hedef Yılı"], ["Kapsam 1 emisyon yoğunluğu (tCO2e)", "2035"]])
    o = tb.olgular(t)[0]
    assert (o["deger"], o["birim"], o["yil"], o["birim_kaynagi"]) == (2035, None, True, None)


def test_r_tab_02_birden_cok_yil_iceren_baslikta_donem_belirsiz():
    """Klimasan 2025 s. 51: iki satırlık başlık tek hücreye birleşti; dönem ilk yıl (2024) sanılıyordu."""
    t = _elle_tablo(1, [["Kategori 2024 Gerçekleşen 2025 Gerçekleşen", "x"], ["Kapsam 2", "368,61"]])
    t["hucreler"] = [h for h in t["hucreler"] if h["metin"] != "x"]
    t["hucreler"][0]["sutun_kapsam"] = 2
    assert tk.tablo_hatalari(t) == []
    o = tb.olgular(t)[0]
    assert o["sutun_yolu"] == ["Kategori 2024 Gerçekleşen 2025 Gerçekleşen"]
    assert o["donem"] is None


def test_r_tab_02_birden_cok_birim_iceren_baslikta_birim_belirsiz():
    t = _elle_tablo(1, [["Gösterge", "Enerji (MWh) ve emisyon (tCO2e)"], ["Tesis A", "1.200"]])
    assert tb.olgular(t)[0]["birim"] is None


def test_r_tab_01_baslikta_veri_varsa_uyari():
    """Klimasan 2025 s. 51: başlık hücresi ilk veri satırını da yuttu ('Kapsam 1 1.514,11 1.075,62')."""
    t = _elle_tablo(
        1, [["Emisyon Kategorisi 2024 Kapsam 1 1.514,11 1.075,62", "Açıklama"], ["Kapsam 2", "368,61"]]
    )
    tb.denetle(t, sayfa_sayisi=60)
    assert "baslikta_sayisal_veri" in t["uyarilar"]


def test_r_tab_01_icindekiler_tablosu_olgu_uretmez():
    """Derimod, QUA Granite, Akbank s. 2–3: içindekiler tablosundaki sayfa numaraları olgu sanılıyordu."""
    t = _elle_tablo(
        1, [["Yönetişim", "12"], ["Strateji", "21"], ["Risk Yönetimi", "32"], ["Metrikler", "41"]]
    )
    for h in t["hucreler"]:
        h["sutun_basligi"] = False
    tb.denetle(t, sayfa_sayisi=60)
    assert "icindekiler_olasi" in t["uyarilar"]
    assert tb.olgular(t) == []


def test_r_tab_01_icindekiler_olmayan_sayisal_tablo_isaretlenmez():
    t = _elle_tablo(1, [["Kalem", "2025"], ["Elektrik", "1.200"], ["Doğal gaz", "3.400"], ["Buhar", "450"]])
    tb.denetle(t, sayfa_sayisi=60)
    assert "icindekiler_olasi" not in t["uyarilar"]


def test_r_tab_01_yalniz_rakam_blok_tablo_basligi_sayilmaz(tmp_path):
    """Klimasan 2025 s. 51: tablonun üstündeki sayfa numarası ('2') başlık sanılmıştı."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    _yaz(page, 300, 100, "2", 9)
    for r, satir in enumerate([["Kalem", "2025"], ["Elektrik", "1.200"]]):
        for c, m in enumerate(satir):
            _kutu(page, 50 + c * 120, 110 + r * 20, 170 + c * 120, 130 + r * 20, m)
    doc.save(tmp_path / "b.pdf")
    assert tb.cikar(tmp_path / "b.pdf", "x-2025")[0]["baslik"] == ""
