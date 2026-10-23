"""Etiket şeması 0.1 (ADR-013) ve analiz ekranı testleri (R-ETK-01, R-PDF-02, R-HIL-01).

Paragraf kaydı: beyan türü, madde başına kanıt cümlesi, belirsizlik nedeni, emin değilim, süre.
"""

import csv
import json
from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest
from yardimci import IDS, ROOT, UI, _birim, _oneri_yaz

from review_ui import analiz, kor, qa

SEMA = json.loads((ROOT / "data/labels/etiket_semasi.json").read_text(encoding="utf-8"))
D = date(2026, 10, 23)


def _sayfa(ad: str) -> AppTest:
    return AppTest.from_file(str(UI / ad), default_timeout=60)


def _analiz(ad: str) -> AppTest:
    """Analiz ekranı adı paylaşılan oturumdan almaz (Ö4); ad kutusuna yazılır."""
    at = _sayfa("ekranlar/analiz.py").run()
    return at.text_input(key="ad_analiz").input(ad).run()


# ---------- cümlelere bölme ----------
@pytest.mark.parametrize(
    "metin,beklenen",
    [
        (
            "Komite üç ayda bir toplanır. Yönetim Kurulu'na yılda iki kez sunum yapılır.",
            ["Komite üç ayda bir toplanır.", "Yönetim Kurulu'na yılda iki kez sunum yapılır."],
        ),
        (
            "Kapsam 1 emisyonu 12.450 tCO2e oldu. Hedef 2030.",
            ["Kapsam 1 emisyonu 12.450 tCO2e oldu.", "Hedef 2030."],
        ),
        (
            "Tablo 1. Sera gazı emisyonları ve 2. sırada su.",
            ["Tablo 1. Sera gazı emisyonları ve 2. sırada su."],
        ),
        (
            "Akbank T.A.Ş. ile Ak Yatırım A.Ş. birlikte raporlanır.",
            ["Akbank T.A.Ş. ile Ak Yatırım A.Ş. birlikte raporlanır."],
        ),
        ("Tek cümle", ["Tek cümle"]),
    ],
)
def test_cumlelere_bol_turkce(metin, beklenen):
    assert kor.cumlelere_bol(metin, "paragraf") == beklenen


def test_cumlelere_bol_tablo_satir_satir():
    assert kor.cumlelere_bol("Tablo 1\nKapsam | 2024\nKapsam 1 | 12.450", "tablo") == [
        "Tablo 1",
        "Kapsam | 2024",
        "Kapsam 1 | 12.450",
    ]


# ---------- paragraf kaydı ----------
def _kaydet(cikti, birim, secimler, gerekce="", ad="Mehmet Güneş", **kw):
    alanlar = {"beyan_turleri": ["yonetisim"], "kanit": {}, "belirsizlik": [], "emin": True, "sure_sn": 42}
    alanlar |= kw
    return kor.kaydet(cikti, birim, secimler, ad, IDS, gerekce, bugun=D, **alanlar)


def test_r_etk_01_paragraf_kaydi_yazilir_ve_dogrulanir(tmp_path):
    from validate_data import validate_file

    cikti = tmp_path / "blind" / "mehmet-gunes" / "pilot_v0.csv"
    b = _birim(1) | {"metin": "Komite üç ayda bir toplanır. Kurula yılda iki kez sunum yapar."}
    _kaydet(cikti, b, {"TSRS2-YON-06a": "2"}, kanit={"TSRS2-YON-06a": [1, 2]})
    _kaydet(cikti, _birim(2), {}, beyan_turleri=["genel"], emin=False, belirsizlik=["eksik_baglam"])
    kayit = kor.paragraf_kayitlari(cikti)
    assert kayit[b["paragraf_id"]]["kanit"] == {"TSRS2-YON-06a": [1, 2]}
    assert kayit[b["paragraf_id"]]["sema_surumu"] == SEMA["sema_surumu"]
    assert kayit[_birim(2)["paragraf_id"]]["emin"] is False
    yan = cikti.with_suffix(".paragraf.jsonl")
    assert validate_file(cikti) == [] and validate_file(yan) == []


@pytest.mark.parametrize(
    "secimler,kw,igne",
    [
        ({}, {"beyan_turleri": []}, "beyan türü seç"),
        ({}, {"beyan_turleri": ["uydurma"]}, "beyan türü"),
        ({"TSRS2-YON-06a": "2"}, {"kanit": {}}, "kanıt cümlesi"),
        ({"TSRS2-YON-06a": "1"}, {"kanit": {"TSRS2-YON-06a": [9]}}, "kanıt cümlesi"),
        ({}, {"emin": False, "belirsizlik": []}, "belirsizlik nedeni"),
        ({}, {"belirsizlik": ["uydurma"], "emin": False}, "belirsizlik nedeni"),
        (
            {"TSRS2-YON-06a": "2"},
            {"kanit": {"TSRS2-YON-06a": [1]}, "belirsizlik": ["cikarim_hatasi"], "emin": False},
            "Çıkarım hatasında",
        ),
        ({}, {"belirsizlik": ["eksik_baglam"]}, "Emin değilim"),  # Ö7
    ],
)
def test_r_etk_01_hatali_paragraf_kaydi_reddedilir(tmp_path, secimler, kw, igne):
    cikti = tmp_path / "c.csv"
    with pytest.raises(ValueError, match=igne):
        _kaydet(cikti, _birim(1), secimler, **kw)
    assert not cikti.exists() and not cikti.with_suffix(".paragraf.jsonl").exists()


def test_r_etk_01_paragraf_kaydi_yeniden_kaydedince_degisir(tmp_path):
    cikti = tmp_path / "c.csv"
    _kaydet(cikti, _birim(1), {}, beyan_turleri=["genel"])
    _kaydet(cikti, _birim(1), {}, beyan_turleri=["politika"])
    satirlar = cikti.with_suffix(".paragraf.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(satirlar) == 1 and json.loads(satirlar[0])["beyan_turleri"] == ["politika"]


def test_sema_dosyasi_kilavuzla_ayni():
    """Doğrulayıcının izin verdiği değerler kılavuzla aynıdır (.claude/rules/data.md)."""
    kilavuz = (ROOT / "docs/labeling/etiket_kilavuzu_v0.md").read_text(encoding="utf-8")
    for kod in [*SEMA["beyan_turleri"], *SEMA["belirsizlik_nedenleri"]]:
        assert f"`{kod}`" in kilavuz, kod
    assert SEMA["beyan_turleri"] == kor.BEYAN_TURLERI


# ---------- analiz mantığı ----------
def _ornek_veri(tmp_path) -> tuple[list[dict], Path]:
    orneklem = [_birim(i, sayfa=s) for s in (1, 2) for i in (1, 2)]
    cikti = tmp_path / "pilot_v0.csv"
    _kaydet(cikti, orneklem[0], {"TSRS2-YON-06a": "2"}, kanit={"TSRS2-YON-06a": [1]}, sure_sn=30)
    _kaydet(
        cikti,
        orneklem[1],
        {"TSRS2-YON-06a": "1", "TSRS2-YON-06a-iii": "1"},
        kanit={"TSRS2-YON-06a": [1], "TSRS2-YON-06a-iii": [1]},
        beyan_turleri=["yonetisim", "politika"],
        emin=False,
        belirsizlik=["kilavuz_belirsiz"],
        sure_sn=90,
    )
    _kaydet(cikti, orneklem[2], {}, beyan_turleri=["genel"], sure_sn=10)
    return orneklem, cikti


def test_analiz_kor_ozeti(tmp_path):
    orneklem, cikti = _ornek_veri(tmp_path)
    oz = analiz.kor_ozeti(orneklem, kor.yapilanlar(cikti), kor.paragraf_kayitlari(cikti))
    assert oz["etiketli"] == 3 and oz["orneklem"] == 4
    assert oz["duzey"] == {"2": 1, "1": 2, "NONE": 1}
    assert oz["beyan"] == {"yonetisim": 2, "politika": 1, "genel": 1}
    assert oz["emin_degil"] == 1 and oz["belirsizlik"] == {"kilavuz_belirsiz": 1}
    assert oz["sure_medyan_sn"] == 30 and oz["sure_toplam_sn"] == 130
    assert oz["madde"]["TSRS2-YON-06a"] == {"2": 1, "1": 1}
    rapor = {r["rapor_id"]: r for r in oz["rapor"]}
    assert rapor["sirket-ornek-2025"]["etiketli"] == 3 and rapor["sirket-ornek-2025"]["none"] == 1


def test_analiz_duz_tablo_indirme_icin(tmp_path):
    orneklem, cikti = _ornek_veri(tmp_path)
    tablo = analiz.paragraf_tablosu(orneklem, kor.yapilanlar(cikti), kor.paragraf_kayitlari(cikti))
    assert len(tablo) == 3
    ikinci = next(r for r in tablo if r["paragraf_id"] == orneklem[1]["paragraf_id"])
    assert ikinci["maddeler"] == "TSRS2-YON-06a:1; TSRS2-YON-06a-iii:1"
    assert ikinci["beyan_turleri"] == "yonetisim; politika" and ikinci["emin"] == "hayır"


def test_analiz_qa_ozeti_rapor_bazinda(tmp_path):
    c = tmp_path / "qa.csv"
    qa.kaydet(c, "r1", 1, set(), "M")
    qa.kaydet(c, "r1", 2, {"kirik_tablo"}, "M", "kaymış")
    qa.kaydet(c, "r2", 1, {"kirik_tablo", "eksik_metin"}, "M", "x")
    oz = analiz.qa_ozeti(qa.kayitlar(c), "M")
    assert oz["sayfa"] == 3 and oz["hatasiz"] == 1
    assert oz["turler"] == {"kirik_tablo": 2, "eksik_metin": 1}
    assert {r["rapor_id"]: r["hatasiz_oran"] for r in oz["rapor"]} == {"r1": 0.5, "r2": 0.0}


# ---------- ekranlar ----------
def test_r_etk_01_kor_ekran_yeni_alanlarla_kaydeder(veri):
    at = _sayfa("ekranlar/kor_etiketleme.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception
    pid = _birim(1, sayfa=1)["paragraf_id"]
    at.button(key=f"kaydet-{pid}").click().run()
    assert any("beyan türü" in e.value for e in at.error)  # beyan türü seçilmeden kaydedilmez

    at.multiselect(key=f"beyan-{pid}").set_value(["yonetisim"]).run()
    at.multiselect(key=f"secili-{pid}").set_value(["TSRS2-YON-06a"]).run()
    at.radio(key=f"seviye-{pid}-TSRS2-YON-06a").set_value("2").run()
    at.button(key=f"kaydet-{pid}").click().run()
    assert any("kanıt cümlesi" in e.value for e in at.error)

    at.multiselect(key=f"kanit-{pid}-TSRS2-YON-06a").set_value([1]).run()
    at.checkbox(key=f"emin-degil-{pid}").check().run()
    at.multiselect(key=f"neden-{pid}").set_value(["kilavuz_belirsiz"]).run()
    at.button(key=f"kaydet-{pid}").click().run()
    assert not at.exception and not at.error

    cikti = veri / "data/labels/blind/mehmet-gunes/pilot_v0.csv"
    kayit = kor.paragraf_kayitlari(cikti)[pid]
    assert kayit["beyan_turleri"] == ["yonetisim"] and kayit["kanit"] == {"TSRS2-YON-06a": [1]}
    assert kayit["emin"] is False and kayit["belirsizlik"] == ["kilavuz_belirsiz"]
    assert isinstance(kayit["sure_sn"], int) and kayit["sure_sn"] >= 0


def test_r_hil_01_analiz_ekrani(veri):
    data = veri / "data"
    cikti = kor.KorYollar(data).cikti("Mehmet Güneş")
    orneklem = kor.orneklem_oku(data / "labels/pilot/orneklem.jsonl")
    _kaydet(cikti, orneklem[0], {"TSRS2-YON-06a": "2"}, kanit={"TSRS2-YON-06a": [1]})
    qa.kaydet(
        veri / "deney/extraction-qa-elle.csv", "sirket-ornek-2025", 1, {"kirik_tablo"}, "Mehmet Güneş", "x"
    )

    at = _analiz("Mehmet Güneş")
    assert not at.exception
    metin = " ".join(str(m.value) for m in [*at.markdown, *at.info, *at.caption])
    assert "pilot bitince" in metin  # uyum bölümü kör pilot sürerken kapalı
    assert any(m.label == "Etiketlenen paragraf" and m.value == "1 / 3" for m in at.metric)
    assert any(m.label == "Kontrol edilen sayfa" and m.value == "1" for m in at.metric)


def test_r_etk_01_analiz_pilot_surerken_baskasinin_etiketini_gostermez(veri):
    """İkinci etiketleyici (D-06) analiz ekranında birinci etiketleyicinin kararlarını görmemeli."""
    data = veri / "data"
    orneklem = kor.orneklem_oku(data / "labels/pilot/orneklem.jsonl")
    _kaydet(kor.KorYollar(data).cikti("Mehmet Güneş"), orneklem[0], {"TSRS2-YON-06a": "2"},
            kanit={"TSRS2-YON-06a": [1]})  # fmt: skip
    at = _analiz("Zemzem Boyluğ")
    assert not at.exception
    assert any(m.label == "Etiketlenen paragraf" and m.value == "0 / 3" for m in at.metric)


def test_r_etk_01_analiz_pilot_bitince_kappa(veri):
    data = veri / "data"
    (data / "labels/proposals/pilot.csv").unlink()
    orneklem = kor.orneklem_oku(data / "labels/pilot/orneklem.jsonl")
    cikti = kor.KorYollar(data).cikti("Mehmet Güneş")
    for b in orneklem:
        _kaydet(cikti, b, {"TSRS2-YON-06a": "2"}, kanit={"TSRS2-YON-06a": [1]})
    _oneri_yaz(data, orneklem, "MODEL")  # model de hepsine YON-06a:2 dedi
    at = _analiz("Mehmet Güneş")
    assert not at.exception
    assert any(m.label.startswith("κ") and m.value == "1,000" for m in at.metric)
    assert kor.korleme_acildi(data)  # κ gösterilince kör etiketler donar (K1)


def test_yonlendirici_analiz_sayfasi_var():
    app = (UI / "app.py").read_text(encoding="utf-8")
    assert '"4 · Analiz"' in app


def test_dosya_csv_basligi_degismedi():
    """Çekirdek etiket dosyası kappa ve doğrulayıcıyla uyumlu kalır (yeni alanlar ayrı dosyada)."""
    from review_ui.logic import LABEL_HEADER

    with (ROOT / "data/labels/etiket_sablonu.csv").open(encoding="utf-8") as fh:
        assert next(csv.reader(fh)) == LABEL_HEADER


# ---------- code-reviewer 2026-10-23 (şema 0.1) bulguları; önce kırmızı yazıldı ----------
def test_k1_korleme_acilinca_kor_etiket_degistirilemez(veri):
    data = veri / "data"
    orneklem = kor.orneklem_oku(data / "labels/pilot/orneklem.jsonl")
    cikti = kor.KorYollar(data).cikti("Mehmet Güneş")
    _kaydet(cikti, orneklem[0], {}, beyan_turleri=["genel"])
    kor.korlemeyi_ac(data, "test")
    kilit = json.loads((cikti.parent / "pilot_v0.kilit.json").read_text(encoding="utf-8"))
    assert kilit["neden"] == "test" and len(kilit["csv_sha256"]) == 64
    with pytest.raises(ValueError, match="Körleme açıldı"):
        _kaydet(cikti, orneklem[0], {}, beyan_turleri=["politika"])
    kor.korlemeyi_ac(data, "ikinci kez")  # ilk kayıt korunur
    assert json.loads((cikti.parent / "pilot_v0.kilit.json").read_text(encoding="utf-8"))["neden"] == "test"


def test_k1_onay_ekrani_pilot_onerisini_gosterince_korlemeyi_acar(veri):
    data = veri / "data"
    (data / "labels/proposals/pilot.csv").unlink()
    orneklem = kor.orneklem_oku(data / "labels/pilot/orneklem.jsonl")
    cikti = kor.KorYollar(data).cikti("Mehmet Güneş")
    for b in orneklem:
        _kaydet(cikti, b, {}, beyan_turleri=["genel"])
    _oneri_yaz(data, orneklem, "MODEL")
    assert not kor.korleme_acildi(data)
    _sayfa("ekranlar/etiket_onayi.py").run()
    assert kor.korleme_acildi(data)
    at = _sayfa("ekranlar/kor_etiketleme.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception and not at.button  # donmuş: kayıt düğmesi yok
    assert any("Körleme açıldı" in i.value for i in at.info)


def test_o1_ikinci_dosya_yazilamazsa_ilki_geri_alinir(tmp_path, monkeypatch):
    monkeypatch.setattr(kor.ortak, "_BEKLEME", 0)
    cikti = tmp_path / "pilot_v0.csv"
    _kaydet(cikti, _birim(1), {"TSRS2-YON-06a": "2"}, kanit={"TSRS2-YON-06a": [1]})
    once_csv = cikti.read_bytes()
    once_yan = kor.paragraf_yolu(cikti).read_bytes()
    gercek = Path.replace

    def secici(self, hedef):
        if str(hedef).endswith(".paragraf.jsonl"):
            raise PermissionError(32, "kilitli")
        return gercek(self, hedef)

    monkeypatch.setattr(Path, "replace", secici)
    with pytest.raises(ValueError, match="başka bir programda açık"):
        _kaydet(cikti, _birim(1), {}, beyan_turleri=["genel"])
    assert cikti.read_bytes() == once_csv and kor.paragraf_yolu(cikti).read_bytes() == once_yan
    assert not list(tmp_path.rglob("*.tmp"))


def test_o1_o8_dogrulayici_kayitsiz_paragraf_ve_tur_hatasi(tmp_path):
    from validate_data import validate_file

    cikti = tmp_path / "pilot_v0.csv"
    _kaydet(cikti, _birim(1), {}, beyan_turleri=["genel"])
    kor.kaydet(cikti, _birim(2), {}, "Mehmet Güneş", IDS)  # şema 0 yolu: yan kayıt yok
    yan = kor.paragraf_yolu(cikti)
    assert any("paragraf kaydı yok" in e for e in validate_file(yan))
    satir = json.loads(yan.read_text(encoding="utf-8").splitlines()[0]) | {"kanit": [1]}
    yan.write_text(json.dumps(satir) + "\n", encoding="utf-8")
    assert any("sözlüğü olmalı" in e for e in validate_file(yan))  # çökmez
    yalniz = tmp_path / "yalniz" / "pilot_v0.paragraf.jsonl"
    yalniz.parent.mkdir()
    yalniz.write_text(yan.read_text(encoding="utf-8"), encoding="utf-8")
    assert any("çekirdek CSV yok" in e for e in validate_file(yalniz))


def test_o3_analiz_dosyasi_olmayan_ad_ve_olculemeyen_kappa(veri):
    data = veri / "data"
    (data / "labels/proposals/pilot.csv").unlink()
    orneklem = kor.orneklem_oku(data / "labels/pilot/orneklem.jsonl")
    cikti = kor.KorYollar(data).cikti("Mehmet Güneş")
    for b in orneklem:
        _kaydet(cikti, b, {}, beyan_turleri=["genel"])  # insan da model de hepsine NONE: κ ölçülemez
    model = _oneri_yaz(data, orneklem, "MODEL")
    model.write_text(
        model.read_text(encoding="utf-8")
        .replace(":TSRS2-YON-06a,", ":NONE,")
        .replace(",TSRS2-YON-06a,2,", ",NONE,NONE,"),
        encoding="utf-8",
    )
    at = _analiz("M. Güneş")  # dosyası yok
    assert not at.exception
    at = _analiz("Mehmet Güneş")
    assert not at.exception
    assert any("ölçülecek" in i.value for i in at.info)


def test_o4_analiz_adi_oturumdan_almaz(veri):
    at = _sayfa("ekranlar/analiz.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception and not at.metric
    assert at.text_input(key="ad_analiz").value == ""


def test_o5_kanit_metinden_yeniden_eslenir():
    cumleler = ["A cümlesi.", "B cümlesi.", "C cümlesi."]
    kayit = {"kanit": {"M": [3]}, "kanit_metni": {"M": ["B cümlesi."]}, "bolme_surumu": "eski"}
    assert kor.kanit_varsayilan(kayit, "M", cumleler) == [2]  # numara değil metin esas
    assert kor.kanit_varsayilan({"kanit": {"M": [9]}, "kanit_metni": {"M": ["yok"]}}, "M", cumleler) == []
    assert kor.kanit_varsayilan({}, "M", cumleler) == []


def test_o5_kayitta_bolme_surumu(tmp_path):
    cikti = tmp_path / "c.csv"
    _kaydet(cikti, _birim(1), {}, beyan_turleri=["genel"])
    assert kor.paragraf_kayitlari(cikti)[_birim(1)["paragraf_id"]]["bolme_surumu"] == kor.BOLME_SURUMU


def test_o6_aktif_sure_ve_duzeltme():
    durum: dict = {}
    kor.sure_guncelle(durum, "A", 0.0)
    kor.sure_guncelle(durum, "B", 10.0)  # A'da 10 sn
    kor.sure_guncelle(durum, "A", 15.0)  # B'de 5 sn
    assert kor.sure_al(durum, "A", 18.0) == 13
    assert kor.sure_al(durum, "B", 18.0) == 5


def test_o6_duzeltme_suresi_eklenir_ve_kesintili_ayrilir(tmp_path):
    orneklem = [_birim(i) for i in (1, 2, 3)]
    cikti = tmp_path / "c.csv"
    _kaydet(cikti, orneklem[0], {}, beyan_turleri=["genel"], sure_sn=120)
    _kaydet(cikti, orneklem[0], {}, beyan_turleri=["politika"], sure_sn=8)
    assert kor.paragraf_kayitlari(cikti)[orneklem[0]["paragraf_id"]]["sure_sn"] == 128
    _kaydet(cikti, orneklem[1], {}, beyan_turleri=["genel"], sure_sn=4000)  # öğle arası
    oz = analiz.kor_ozeti(orneklem, kor.yapilanlar(cikti), kor.paragraf_kayitlari(cikti))
    assert oz["sure_toplam_sn"] == 128 and oz["sure_medyan_sn"] == 128 and oz["sure_kesintili"] == 1


@pytest.mark.parametrize(
    "metin,beklenen",
    [
        ("Emisyon azaldı. %12 düşüş sağlandı.", ["Emisyon azaldı.", "%12 düşüş sağlandı."]),
        # sayıdan sonraki nokta bölmez ("11. Kalkınma"); "s. 40." de birleşik kalır, yanlış bölünmez
        ("Ayrıntılar için bkz. s. 40. Komite toplandı.", ["Ayrıntılar için bkz. s. 40. Komite toplandı."]),
        ("Hedef yılı 2030. Bunun için plan var.", ["Hedef yılı 2030.", "Bunun için plan var."]),
        ("“Azaldı.” Komite toplandı.", ["“Azaldı.”", "Komite toplandı."]),
        ("11. Kalkınma Planı ile uyumludur.", ["11. Kalkınma Planı ile uyumludur."]),
        ("Doç. Dr. Ayşe Yılmaz katıldı.", ["Doç. Dr. Ayşe Yılmaz katıldı."]),
    ],
)
def test_k1_bolme_ek_durumlar(metin, beklenen):
    assert kor.cumlelere_bol(metin, "paragraf") == beklenen


def test_k2_k3_k4_k5_k6_k7_bicim_ve_kucukler(tmp_path):
    assert analiz.yuzde(1, 3) == "%33,3" and analiz.yuzde(1, 8) == "%12,5" and analiz.yuzde(0, 0) == "—"
    assert analiz.csv_baytlari([{"a": "1", "b": "x"}]).decode("utf-8-sig").splitlines()[0] == "a;b"
    assert analiz.etiket_adi({"genel": "Genel bilgi: açıklama"}, "eski_kod") == "eski_kod"
    c = tmp_path / "qa.csv"
    qa.kaydet(c, "r1", 1, set(), "Mehmet Güneş")
    assert analiz.qa_ozeti(qa.kayitlar(c), "mehmet güneş")["sayfa"] == 1
    orneklem = [_birim(1, rapor="sirket-a-2025"), _birim(2, rapor="sirket-b-2025")]
    cikti = tmp_path / "pilot_v0.csv"
    _kaydet(cikti, orneklem[0], {}, beyan_turleri=[], belirsizlik=["cikarim_hatasi"], emin=False)  # K-7
    oz = analiz.kor_ozeti(orneklem, kor.yapilanlar(cikti), kor.paragraf_kayitlari(cikti))
    rapor = {r["rapor_id"]: r for r in oz["rapor"]}
    assert rapor["sirket-b-2025"]["etiketli"] == 0 and rapor["sirket-b-2025"]["none"] == 0
    assert oz["cikarim_hatasi"] == 1 and oz["duzey"].get("NONE", 0) == 0
