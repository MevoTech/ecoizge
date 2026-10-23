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


# ---------- code-reviewer 2026-10-23 bulguları (önce kırmızı yazıldı) ----------
def _oneri_yaz(data: Path, birimler: list[dict], metin_on: str) -> Path:
    from review_ui.logic import LABEL_HEADER, write_rows

    satirlar = [
        dict.fromkeys(LABEL_HEADER, "")
        | {
            "etiket_id": f"{b['paragraf_id']}:TSRS2-YON-06a",
            "tur": "paragraf",
            "rapor_id": b["rapor_id"],
            "paragraf_id": b["paragraf_id"],
            "sayfa": str(b["sayfa"]),
            "metin": f"{metin_on} {b['paragraf_id']}",
            "madde_id": "TSRS2-YON-06a",
            "karsilama": "2",
            "guven": "0.9",
            "gerekce": "model gerekçesi",
            "etiketleyen": "annotation-assistant",
            "kaynak": "model",
        }
        for b in birimler
    ]
    hedef = data / "labels" / "proposals" / "pilot_v0.csv"
    write_rows(hedef, satirlar)
    return hedef


def test_r_etk_01_onay_ekrani_pilot_bitmeden_pilot_onerisini_gostermez(veri):
    """Bulgu 1 (kritik): menüden '3 · Etiket onayı'na geçince kör pilot bozuluyordu."""
    data = veri / "data"
    (data / "labels/proposals/pilot.csv").unlink()
    orneklem = kor.orneklem_oku(data / "labels/pilot/orneklem.jsonl")
    _oneri_yaz(data, orneklem, "PILOT_ONERI_METNI")
    cikti = kor.KorYollar(data).cikti("Mehmet Güneş")
    kor.kaydet(cikti, orneklem[0], {}, "Mehmet Güneş", IDS)  # 1/3: pilot sürüyor

    at = _sayfa("ekranlar/etiket_onayi.py").run()
    assert not at.exception
    gorunen = " ".join(str(e.value) for e in [*at.markdown, *at.caption, *at.text, *at.info])
    assert "PILOT_ONERI_METNI" not in gorunen
    assert "kör etiketleme bitene kadar" in gorunen

    for b in orneklem[1:]:
        kor.kaydet(cikti, b, {}, "Mehmet Güneş", IDS)  # 3/3: pilot bitti
    at = _sayfa("ekranlar/etiket_onayi.py").run()
    assert "PILOT_ONERI_METNI" in " ".join(str(m.value) for m in at.markdown)


def test_r_etk_01_pilot_kilidi_mantigi(veri):
    data = veri / "data"
    orneklem = kor.orneklem_oku(data / "labels/pilot/orneklem.jsonl")
    assert kor.pilot_kilitli(data)  # hiç kör etiket yok
    a = kor.KorYollar(data).cikti("A")
    for b in orneklem:
        kor.kaydet(a, b, {}, "A", IDS)
    assert not kor.pilot_kilitli(data)
    kor.kaydet(kor.KorYollar(data).cikti("B"), orneklem[0], {}, "B", IDS)  # ikinci etiketleyici başladı
    assert kor.pilot_kilitli(data)


def test_r_etk_01_filtre_degisince_kaydedilmemis_secim_korunur(veri):
    """Bulgu 2: arama kutusu seçilmiş ama kaydedilmemiş maddeyi listeden düşürüyordu."""
    at = _sayfa("ekranlar/kor_etiketleme.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    pid = _birim(1, sayfa=1)["paragraf_id"]
    at.multiselect(key=f"secili-{pid}").set_value(["TSRS2-YON-06a"]).run()
    at.radio(key=f"seviye-{pid}-TSRS2-YON-06a").set_value("2").run()
    at.text_input(key="ara").input("emisyon").run()
    assert "TSRS2-YON-06a" in at.multiselect(key=f"secili-{pid}").value
    at.button(key=f"kaydet-{pid}").click().run()
    rows = kor.yapilanlar(veri / "data/labels/blind/mehmet-gunes/pilot_v0.csv")[pid]
    assert [r["madde_id"] for r in rows] == ["TSRS2-YON-06a"]


def test_madde_aramasi_turkce_buyuk_harf():
    """Bulgu 3: 'iklim' araması 'İklim…' başlığını bulmuyordu (str.lower)."""
    from review_ui.logic import Paths, catalog_lookup

    katalog = catalog_lookup(Paths(ROOT / "data"))
    bulunan = kor.madde_filtrele(katalog, "Tümü", "Tümü", "iklimle ilgili risk")
    assert "TSRS2-YON-06a" in bulunan
    assert kor.madde_filtrele(katalog, "Tümü", "Tümü", "İKLİMLE İLGİLİ RİSK") == bulunan


def test_r_etk_01_ilerleme_sahipsiz_satiri_saymaz(tmp_path):
    """Bulgu 4: örneklem değişince eski satırlar ilerlemeyi 1'in üstüne çıkarıyordu."""
    orneklem = [_birim(i) for i in range(1, 3)]
    yapilan = {orneklem[0]["paragraf_id"]: [{}], "eski-paragraf": [{}]}
    assert kor.ilerleme(orneklem, yapilan) == (1, 2, ["eski-paragraf"])


def test_r_etk_01_orneklem_degisirse_ekran_durur(veri):
    data = veri / "data"
    at = _sayfa("ekranlar/kor_etiketleme.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    pid = _birim(1, sayfa=1)["paragraf_id"]
    at.button(key=f"kaydet-{pid}").click().run()
    assert (data / "labels/blind/mehmet-gunes/pilot_v0.orneklem.sha256").exists()

    yol = data / "labels/pilot/orneklem.jsonl"
    yol.write_text(yol.read_text(encoding="utf-8") + "\n" + json.dumps(_birim(9)), encoding="utf-8")
    at = _sayfa("ekranlar/kor_etiketleme.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception
    assert any("örneklem değişmiş" in e.value for e in at.error)
    assert not at.button  # kayıt yapılamaz


def test_kayit_dosya_kilitliyse_anlasilir_hata_verir(tmp_path, monkeypatch):
    """Bulgu 5: Excel dosyayı açık tutunca Windows'ta PermissionError yığını görünüyordu."""
    monkeypatch.setattr(kor.ortak, "_BEKLEME", 0)

    def kilitli(self, hedef):
        raise PermissionError(32, "The process cannot access the file")

    monkeypatch.setattr(Path, "replace", kilitli)
    cikti = tmp_path / "blind" / "pilot_v0.csv"
    with pytest.raises(ValueError, match="başka bir programda açık"):
        kor.kaydet(cikti, _birim(1), {}, "M", IDS)
    with pytest.raises(ValueError, match="başka bir programda açık"):
        qa.kaydet(tmp_path / "qa.csv", "r", 1, set(), "M")
    assert not list(tmp_path.rglob("*.tmp"))


def test_bom_ile_kaydedilmis_csv_okunur(tmp_path):
    from review_ui.logic import read_rows

    p = tmp_path / "x.csv"
    p.write_bytes("﻿etiket_id,paragraf_id\nx,p\n".encode())
    assert read_rows(p) == [{"etiket_id": "x", "paragraf_id": "p"}]


def test_r_pdf_02_birimsiz_sayfa_da_orneklemeye_girer():
    """Bulgu 6: OCR gereken ya da metni kaçan sayfalar (birimsiz) hiç seçilmiyordu."""
    spec = importlib.util.spec_from_file_location(
        "qa_report", ROOT / ".claude/skills/pdf-extract/scripts/qa_report.py"
    )
    qa_report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qa_report)
    birimler = [_birim(1, sayfa=s) for s in (1, 2)]
    secilen = qa.kontrol_sayfalari(birimler, 5, 43, sayfa_sayisi=40)
    assert secilen == qa_report.analyze(birimler, 5, 43, page_count=40)["elle_kontrol_sayfalari"]
    assert set(secilen) - {1, 2}


def test_r_pdf_02_sayfa_sayisi_manifestten(tmp_path):
    m = tmp_path / "KAYNAKLAR.csv"
    m.write_text("rapor_id,sayfa\nsirket-a-2025,61\nsirket-b-2025,\n", encoding="utf-8")
    assert qa.sayfa_sayisi("sirket-a-2025", m, None, []) == 61
    assert qa.sayfa_sayisi("sirket-b-2025", m, None, [_birim(1, sayfa=7)]) == 7


def test_r_pdf_02_birimsiz_sayfa_ekranda_gosterilir(veri):
    data = veri / "data"
    (data / "raw/public").mkdir(parents=True)
    (data / "raw/public/KAYNAKLAR.csv").write_text("rapor_id,sayfa\nsirket-ornek-2025,3\n", encoding="utf-8")
    yol = data / "labels/pilot/birimler/sirket-ornek-2025.jsonl"
    yol.write_text(json.dumps(_birim(1, sayfa=1), ensure_ascii=False), encoding="utf-8")
    at = _sayfa("ekranlar/cikarim_kontrolu.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception
    sayfalar = qa.kontrol_sayfalari([_birim(1, sayfa=1)], sayfa_sayisi=3)
    assert sayfalar == [1, 2, 3]
    at.sidebar.radio(key="qa_sayfa").set_value(1).run()  # s.2: birimi yok
    assert any("çıkarılan birim yok" in w.value for w in at.warning)


def test_r_pdf_02_ilerleme_yalnizca_secili_sayfalari_sayar(veri):
    cikti = veri / "deney/extraction-qa-elle.csv"
    qa.kaydet(cikti, "sirket-eski-2024", 9, set(), "Mehmet")  # artık örneklemde olmayan rapor
    at = _sayfa("ekranlar/cikarim_kontrolu.py")
    at.session_state["_ad"] = "Mehmet Güneş"
    at.run()
    assert not at.exception
    assert any("0 / 3" in str(p.text) for p in at.sidebar.get("progress"))


def test_r_pdf_02_iki_kisinin_kontrolu_birbirini_silmez(tmp_path):
    cikti = tmp_path / "qa.csv"
    qa.kaydet(cikti, "r", 3, set(), "Mehmet")
    qa.kaydet(cikti, "r", 3, {"kirik_tablo"}, "Zemzem", "kaymış")
    assert {r["kontrol_eden"] for r in qa.kayitlar(cikti)} == {"Mehmet", "Zemzem"}


def test_r_etk_01_seviye_secilmeden_kaydedilmez(tmp_path):
    """Bulgu 9: radyo '1' seçili açılıyordu; dokunmadan kaydeden kişi farkında olmadan 1 veriyordu."""
    with pytest.raises(ValueError, match="karşılama düzeyini seç"):
        kor.kaydet(tmp_path / "c.csv", _birim(1), {"TSRS2-YON-06a": None}, "M", IDS)


def test_kor_ekran_ascii_karsiligi_olmayan_ad_cokmez(veri):
    at = _sayfa("ekranlar/kor_etiketleme.py")
    at.session_state["_ad"] = "..."
    at.run()
    assert not at.exception
    assert any("harf" in e.value for e in at.error)


def test_label_propose_skill_ayni_orneklem_yolunu_kullanir():
    """Bulgu 7 / C-02: skill ile kör ekran farklı örneklem dosyalarını kullanıyordu."""
    skill = (ROOT / ".claude/skills/label-propose/SKILL.md").read_text(encoding="utf-8")
    yol = kor.KorYollar(Path("data")).orneklem.as_posix()
    assert yol in skill
    assert "pilot-orneklem.jsonl" not in skill
