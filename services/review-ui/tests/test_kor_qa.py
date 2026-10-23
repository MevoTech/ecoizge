"""Kör etiketleme ve çıkarım kontrolü testleri (S04, S05, R-ETK-01, R-PDF-02, R-HIL-01)."""

import csv
import importlib.util
import json
import shutil
from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from review_ui import kor, qa

ROOT = Path(__file__).resolve().parents[3]
UI = ROOT / "services/review-ui"
KATALOG = ROOT / "data/catalog/catalog_v0.csv"
IDS = {r["madde_id"] for r in csv.DictReader(KATALOG.open(encoding="utf-8"))}


def _birim(i: int, sayfa: int = 3, rapor: str = "sirket-ornek-2025") -> dict:
    return {
        "paragraf_id": f"{rapor}-p{sayfa:03d}-{i:02d}",
        "rapor_id": rapor,
        "sayfa": sayfa,
        "bolum_basligi": "Yönetişim",
        "tur": "paragraf",
        "metin": f"Sürdürülebilirlik Komitesi yılda iki kez Yönetim Kurulu'na sunum yapar. #{i} *kalın değil*",
        "kaynak": "metin",
    }


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


# ---------- kör etiketleme mantığı ----------
def test_ad_kimligi_turkce():
    assert kor.ad_kimligi("Mehmet Güneş") == "mehmet-gunes"
    assert kor.ad_kimligi("IŞIL İnce") == "isil-ince"
    with pytest.raises(ValueError):
        kor.KorYollar(Path("x")).cikti("  ")


def test_r_etk_01_kaydet_none_ve_coklu_madde_dogrulayicidan_gecer(tmp_path):
    from validate_data import validate_file

    cikti = tmp_path / "blind" / "mehmet-gunes" / "pilot_v0.csv"
    d = date(2026, 10, 23)
    kor.kaydet(cikti, _birim(1), {}, "Mehmet Güneş", IDS, bugun=d)
    kor.kaydet(
        cikti, _birim(2), {"TSRS2-YON-06a": "2", "TSRS2-YON-06a-iii": "1"}, "Mehmet Güneş", IDS, bugun=d
    )
    rows = list(csv.DictReader(cikti.open(encoding="utf-8")))
    assert [(r["madde_id"], r["karsilama"]) for r in rows] == [
        ("NONE", "NONE"),
        ("TSRS2-YON-06a", "2"),
        ("TSRS2-YON-06a-iii", "1"),
    ]
    assert (
        {r["kaynak"] for r in rows} == {"insan"} and rows[0]["sirket"] == "ornek" and rows[0]["yil"] == "2025"
    )
    assert validate_file(cikti) == []


def test_r_etk_01_ayni_paragrafi_yeniden_kaydetmek_degistirir(tmp_path):
    cikti = tmp_path / "c.csv"
    kor.kaydet(cikti, _birim(1), {"TSRS2-YON-06a": "2"}, "M", IDS)
    kor.kaydet(cikti, _birim(1), {}, "M", IDS)
    yapilan = kor.yapilanlar(cikti)
    assert [r["madde_id"] for r in yapilan[_birim(1)["paragraf_id"]]] == ["NONE"]


@pytest.mark.parametrize(
    "secimler,ad,gerekce,igne",
    [
        ({"TSRS2-YON-06a": "3"}, "M", "", "geçersiz"),
        ({"UYDURMA-01": "2"}, "M", "", "katalogda yok"),
        ({"TSRS2-YON-06a": "U"}, "M", "", "gerekçe zorunlu"),
        ({}, " ", "", "etiketleyen"),
    ],
)
def test_r_etk_01_hatali_kayitlar_reddedilir(tmp_path, secimler, ad, gerekce, igne):
    with pytest.raises(ValueError, match=igne):
        kor.kaydet(tmp_path / "c.csv", _birim(1), secimler, ad, IDS, gerekce)
    assert not (tmp_path / "c.csv").exists()


def test_sonraki_sira():
    orneklem = [_birim(i) for i in range(1, 4)]
    assert kor.sonraki_sira(orneklem, {}) == 0
    assert kor.sonraki_sira(orneklem, {orneklem[0]["paragraf_id"]: [], orneklem[2]["paragraf_id"]: []}) == 1
    assert kor.sonraki_sira(orneklem, {b["paragraf_id"]: [] for b in orneklem}) is None


# ---------- çıkarım kontrolü mantığı ----------
def test_r_pdf_02_sayfa_secimi_qa_report_ile_ayni():
    spec = importlib.util.spec_from_file_location(
        "qa_report", ROOT / ".claude/skills/pdf-extract/scripts/qa_report.py"
    )
    qa_report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qa_report)
    birimler = [_birim(1, sayfa=s) for s in range(1, 40)]
    assert (
        qa.kontrol_sayfalari(birimler, 5, 43) == qa_report.analyze(birimler, 5, 43)["elle_kontrol_sayfalari"]
    )


def test_r_pdf_02_kaydet_ozet_ve_hatalar(tmp_path):
    cikti = tmp_path / "qa.csv"
    qa.kaydet(cikti, "r", 3, set(), "Mehmet")
    qa.kaydet(cikti, "r", 5, {"kirik_tablo", "turkce_harf_kaybi"}, "Mehmet", "tablo kaymış, ş yok")
    qa.kaydet(cikti, "r", 3, {"fazla_metin"}, "Mehmet", "sayfa no kalmış")  # aynı sayfa: değiştirir
    assert qa.ozet(cikti) == {
        "sayfa": 2,
        "hatasiz": 0,
        "turler": {"fazla_metin": 1, "kirik_tablo": 1, "turkce_harf_kaybi": 1},
    }
    with pytest.raises(ValueError, match="not zorunlu"):
        qa.kaydet(cikti, "r", 7, {"kirik_tablo"}, "Mehmet")
    with pytest.raises(ValueError, match="bilinmeyen"):
        qa.kaydet(cikti, "r", 7, {"uydurma"}, "Mehmet", "x")


def test_rapor_dizini_ortam_degiskeni_oncelikli(tmp_path, monkeypatch):
    monkeypatch.setenv("ECOIZGE_RAPOR_DIR", str(tmp_path))
    assert qa.rapor_dizini(Path("data")) == tmp_path
    (tmp_path / "kap").mkdir()
    (tmp_path / "kap" / "ecoizge__kap-x-2025.pdf").write_bytes(b"%PDF-")
    assert qa.pdf_yolu(tmp_path, "kap-x-2025") == tmp_path / "kap" / "ecoizge__kap-x-2025.pdf"
    assert qa.pdf_yolu(tmp_path, "yok") is None


# ---------- ekranlar (gerçekten çalıştırılır) ----------
def _sayfa(ad: str) -> AppTest:
    return AppTest.from_file(str(UI / ad), default_timeout=60)


def test_r_hil_01_ana_sayfa_hazirlik_denetimi(veri):
    at = _sayfa("ekranlar/baslangic.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception
    metin = " ".join(m.value for m in at.markdown)
    assert "Pilot örneklemi" in metin and "⚠️" not in metin  # her şey hazır


def test_r_etk_01_kor_ekran_etiketler_ve_oneriyi_gostermez(veri):
    at = _sayfa("ekranlar/kor_etiketleme.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception
    tum_metin = " ".join(str(e.value) for e in [*at.markdown, *at.caption, *at.text])
    assert "GIZLI_MODEL_ONERISI" not in tum_metin
    assert "\\*kalın değil\\*" in tum_metin  # rapor metni Markdown olarak yorumlanmaz

    pid = _birim(1, sayfa=1)["paragraf_id"]
    at.multiselect(key=f"secili-{pid}").set_value(["TSRS2-YON-06a"]).run()
    at.radio(key=f"seviye-{pid}-TSRS2-YON-06a").set_value("2").run()
    at.button(key=f"kaydet-{pid}").click().run()
    assert not at.exception

    cikti = veri / "data/labels/blind/mehmet-gunes/pilot_v0.csv"
    rows = list(csv.DictReader(cikti.open(encoding="utf-8")))
    assert [(r["paragraf_id"], r["madde_id"], r["karsilama"]) for r in rows] == [(pid, "TSRS2-YON-06a", "2")]
    assert any("1 / 3" in str(p.text) for p in at.sidebar.get("progress"))

    pid2 = _birim(2, sayfa=1)["paragraf_id"]  # sıradaki paragrafa kendiliğinden geçti
    at.button(key=f"kaydet-{pid2}").click().run()  # hiçbir madde seçmeden: NONE
    rows = list(csv.DictReader(cikti.open(encoding="utf-8")))
    assert rows[-1]["paragraf_id"] == pid2 and rows[-1]["madde_id"] == "NONE"


def test_r_etk_01_kor_ekran_ad_olmadan_baslamaz(veri):
    at = _sayfa("ekranlar/kor_etiketleme.py").run()
    assert not at.exception
    assert any("adını soyadını" in i.value for i in at.info)
    assert not (veri / "data/labels/blind").exists()


def test_r_pdf_02_cikarim_kontrol_ekrani(veri):
    at = _sayfa("ekranlar/cikarim_kontrolu.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception
    assert len(at.get("image")) == 1  # PDF sayfası görüntüye çevrildi
    sayfa = qa.kontrol_sayfalari([_birim(1, sayfa=s) for s in (1, 2, 3)])[0]
    anahtar = f"sirket-ornek-2025-{sayfa}"
    at.checkbox(key=f"h-kirik_tablo-{anahtar}").check().run()
    at.button(key=f"kaydet-{anahtar}").click().run()
    assert any("not zorunlu" in e.value for e in at.error)  # notsuz hata kaydedilmez
    at.text_input(key=f"not-{anahtar}").input("tablo kaymış").run()
    at.button(key=f"kaydet-{anahtar}").click().run()
    assert not at.exception
    assert qa.ozet(veri / "deney/extraction-qa-elle.csv")["turler"] == {"kirik_tablo": 1}


def test_r_hil_01_yonlendirici_turkce_menu(veri):
    at = _sayfa("app.py").run()
    assert not at.exception
    assert at.title[0].value == "EcoIzge · Çalışma ekranları"  # varsayılan ekran: Başlangıç
