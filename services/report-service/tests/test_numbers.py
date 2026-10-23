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


# ---------- tablo hücresi ve başlık birimi (R-TAB-02, ADR-014) ----------

from report_service.verify.numbers import birim_bul, hucre_degeri  # noqa: E402


@pytest.mark.parametrize(
    "metin,deger,birim",
    [
        ("12.450", 12450, None),
        ("12.450,5 tCO2e", 12450.5, "tCO2e"),
        ("%12,5", 12.5, "%"),
        ("12,5%", 12.5, "%"),
        ("% 40", 40, "%"),
        ("-3,2", -3.2, None),
        ("−3,2", -3.2, None),  # U+2212 eksi işareti
        ("(1.234)", -1234, None),  # muhasebe gösterimi: ayraç = eksi
        ("+19.202.635", 19202635, None),  # Akbank 2025 s. 39, senaryo tablosu
        ("805.299 TL", 805299, "TL"),
        ("16.000 euro", 16000, "EUR"),
        ("2,26 milyon €", 2_260_000, "EUR"),
        ("1,5 milyar TL", 1_500_000_000, "TL"),
    ],
)
def test_r_tab_02_hucre_degeri_sayisal(metin, deger, birim):
    h = hucre_degeri(metin)
    assert h is not None and not h.eksik
    assert h.deger == pytest.approx(deger)
    assert h.birim == birim
    assert h.ham == metin


@pytest.mark.parametrize("metin", ["-", "–", "—", "n/a", "N/A", "Yok", "mevcut değil", "-*"])
def test_r_tab_02_hucre_degeri_eksik(metin):
    h = hucre_degeri(metin)
    assert h is not None and h.eksik and h.deger is None


@pytest.mark.parametrize(
    "metin,deger,dipnot",
    [
        ("12.450*", 12450, ("*",)),
        ("12.450 (1)", 12450, ("(1)",)),
        ("31.200¹", 31200, ("¹",)),
        ("%12,5**", 12.5, ("**",)),
    ],
)
def test_r_tab_02_hucre_degeri_dipnot(metin, deger, dipnot):
    h = hucre_degeri(metin)
    assert h is not None and h.deger == pytest.approx(deger)
    assert h.dipnot == dipnot


@pytest.mark.parametrize("metin", ["Kapsam 1", "Toplam", "", "Isı Geri Kazanımı", "12.450 ve 3.200", "S-03"])
def test_r_tab_02_hucre_degeri_metin_hucresi(metin):
    assert hucre_degeri(metin) is None


def test_r_tab_02_hucre_degeri_yil_ayri_isaretlenir():
    h = hucre_degeri("2024")
    assert h is not None and h.yil and h.deger == 2024


def test_r_ver_01_para_birimi_eslesir_birim_karismaz():
    tl = _one("yatırım 805.299 TL oldu")
    assert (tl.value, tl.unit) == (805299, "TL")
    assert match(tl, [_one("805.299 ton")]) is None


@pytest.mark.parametrize(
    "metin,birim,carpan",
    [
        ("Emisyon (tCO2e)", "tCO2e", 1.0),
        ("Kapsam 1 (ton CO₂e)", "tCO2e", 1.0),
        ("Enerji tüketimi (MWh)", "kWh", 1e3),
        ("Yatırım (Bin TL)", "TL", 1e3),
        ("Gelir (milyon TL)", "TL", 1e6),
        ("Pay (%)", "%", 1.0),
        ("Tablo 3: Su tüketimi (m³)", "m3", 1.0),
    ],
)
def test_r_tab_02_birim_bul(metin, birim, carpan):
    assert birim_bul(metin) == (birim, carpan)


@pytest.mark.parametrize("metin", ["Kapsam", "Fırsat Adı", "2024", "Tonaj artışı"])
def test_r_tab_02_birim_bul_yok(metin):
    assert birim_bul(metin) is None


@pytest.mark.parametrize(
    "metin", ["12.450 ton CO₂ olarak", "12.450 ton CO2 salım", "12.450 tCO₂ ve", "12.450 ktCO2 ile"]
)
def test_r_ver_01_co2_e_eksiz_birim_cokmez(metin):
    """Regresyon (2026-10-23, Klimasan 2025 tablosu): 'ton CO₂ ' birimi normalize_unit'te ValueError veriyordu."""
    q = _one(metin)
    assert q.unit == "tCO2e"
    assert q.raw.endswith(("CO₂", "CO2"))


@pytest.mark.parametrize("metin", ["Emisyonlar (ton CO 2 e)", "Emisyon (t CO 2 e)", "Kapsam 1 (ktCO 2 e)"])
def test_r_tab_02_alt_simge_ayri_yazilmis_co2e(metin):
    """Regresyon (2026-10-23, Klimasan 2025 s. 51, Docling metni): alt simge '2' ayrı yazılınca birim 'ton' sanılıyordu."""
    taban, _ = birim_bul(metin)
    assert taban == "tCO2e"


# ---------- code-reviewer bulguları (2026-10-23, S28 incelemesi) ----------


def test_r_tab_02_bulgu1_m3_ust_simgesi_dipnot_degil():
    h = hucre_degeri("1.200 m³")
    assert h is not None and (h.deger, h.birim, h.dipnot) == (1200, "m3", ())


def test_r_tab_02_bulgu1_sayidan_sonra_ust_simge_dipnottur():
    h = hucre_degeri("31.200¹")
    assert h is not None and h.dipnot == ("¹",)


def test_r_ver_01_bulgu7_yil_ve_para_birimi_adi_yil_kalir():
    """'2025 Avro Bölgesi' bir tutar değildir; serbest metin denetimi geçerli taslağı reddetmesin."""
    qs = extract_numbers("2025 Avro Bölgesi'nde büyüme yavaşladı.")
    assert len(qs) == 1 and qs[0].is_year and qs[0].unit is None


def test_r_ver_01_bulgu7_on_ekli_para_birimi():
    assert match(_one("TL 805.299 tutarında"), [_one("805.299 TL")]) is not None
    assert _one("€ 16.000 yatırım").unit == "EUR"


def test_r_ver_01_bulgu8_buyuk_harfli_olcek():
    assert hucre_degeri("1,5 MİLYAR TL").deger == pytest.approx(1.5e9)
    assert _one("2,5 MİLYON ton").value == pytest.approx(2.5e6)
