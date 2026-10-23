"""Katalog ve etiket doğrulayıcı testleri (R-KAT-01, R-ETK-01)."""

import csv
import json
import shutil
from pathlib import Path

from validate_data import CATALOG_HEADER, LABEL_HEADER, validate_file

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/catalog/catalog_v0.csv"


def test_r_kat_01_current_catalog_is_valid():
    assert validate_file(CATALOG) == []


def test_r_kat_01_detects_duplicate_and_bad_enum(tmp_path):
    rows = list(csv.reader(CATALOG.open(encoding="utf-8")))
    rows.append(rows[1])  # yinelenen madde_id
    bad = list(rows[2])
    bad[0] = "X-1"
    bad[6] = "belki"  # zorunluluk
    bad[10] = "kaynak?"  # dogrulama
    rows.append(bad)
    p = tmp_path / "catalog_v9.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(rows)
    errs = validate_file(p)
    assert any("yinelenen madde_id" in e for e in errs)
    assert any("zorunluluk='belki'" in e for e in errs)
    assert any("dogrulama=" in e for e in errs)


def _label(**kw) -> dict:
    base = dict.fromkeys(LABEL_HEADER, "")
    base |= {
        "etiket_id": "e1",
        "tur": "paragraf",
        "paragraf_id": "p1",
        "madde_id": "TSRS2-YON-06a",
        "karsilama": "2",
        "guven": "0.8",
        "gerekce": "Organ adı açıkça verilmiş (§4).",
        "etiketleyen": "claude",
        "kaynak": "model_onerisi",
        "tarih": "2026-10-22",
    }
    return base | kw


def _write(path: Path, rows: list[dict]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LABEL_HEADER)
        w.writeheader()
        w.writerows(rows)
    return path


def test_r_etk_01_valid_label_rows(tmp_path):
    rows = [_label(), _label(etiket_id="e2", madde_id="NONE", karsilama="NONE")]
    rows.append(_label(etiket_id="e3", tur="rapor_duzeyi", paragraf_id="", karsilama="0", kaynak="insan"))
    assert validate_file(_write(tmp_path / "ok.csv", rows)) == []


def test_r_etk_01_label_errors_detected(tmp_path):
    rows = [
        _label(karsilama="3"),
        _label(etiket_id="e2", madde_id="YOK-1"),
        _label(etiket_id="e3", guven="", gerekce=""),
        _label(etiket_id="e4", madde_id="NONE", karsilama="1"),
        _label(etiket_id="e5", tur="rapor_duzeyi", paragraf_id="", karsilama="2"),
        _label(etiket_id="e5", tarih="22.10.2026"),
    ]
    errs = validate_file(_write(tmp_path / "bad.csv", rows))
    joined = "\n".join(errs)
    for needle in [
        "karsilama='3'",
        "katalogda yok",
        "guven zorunlu",
        "gerekce zorunlu",
        "madde_id=NONE ise",
        "rapor_duzeyi için karsilama='2'",
        "yinelenen etiket_id",
        "YYYY-AA-GG",
    ]:
        assert needle in joined, needle


def test_unknown_header(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("a,b\n1,2\n", encoding="utf-8")
    assert "tanınmayan başlık" in validate_file(p)[0]


def test_template_header_matches(tmp_path):
    shutil.copy(ROOT / "data/labels/etiket_sablonu.csv", tmp_path / "t.csv")
    assert validate_file(tmp_path / "t.csv") == []
    assert CATALOG_HEADER[0] == "madde_id"


def test_r_pdf_01_kaynak_manifesti_dogrulanir(tmp_path):
    """Derlem manifesti (S03) validate_data üzerinden de denetlenir."""
    import rapor_derlemi as rd

    iyi = {a: "" for a in rd.ALANLAR}
    iyi.update(rapor_id="a", kategori="kidr", url="https://x/a.pdf", dosya_adi="a.pdf", durum="planlandi")
    kotu = dict(iyi, rapor_id="a", url="http://x")
    p = tmp_path / "KAYNAKLAR.csv"
    rd.yaz(p, [iyi])
    assert validate_file(p) == []
    rd.yaz(p, [iyi, kotu])
    errs = "\n".join(validate_file(p))
    assert "yinelenmiş" in errs and "https değil" in errs


def test_r_pdf_01_repo_manifesti_gecerli():
    from validate_data import ROOT, default_files

    m = ROOT / "data" / "raw" / "public" / "KAYNAKLAR.csv"
    assert m in default_files()
    assert validate_file(m) == []


# ---------- paragraf kayıtları (ADR-013, şema 0.1) ----------
def _paragraf_dosyalari(tmp_path, kayit_degisikligi=None, karsilama="2"):
    import json

    core = tmp_path / "pilot_v0.csv"
    satir = dict.fromkeys(LABEL_HEADER, "") | {
        "etiket_id": "p1:TSRS2-YON-06a", "tur": "paragraf", "rapor_id": "sirket-x-2025", "sirket": "x",
        "yil": "2025", "paragraf_id": "p1", "sayfa": "3", "metin": "Komite toplanır.",
        "madde_id": "TSRS2-YON-06a", "karsilama": karsilama, "etiketleyen": "M", "kaynak": "insan",
        "tarih": "2026-10-23",
    }  # fmt: skip
    with core.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LABEL_HEADER)
        w.writeheader()
        w.writerow(satir)
    sema = json.loads((ROOT / "data/labels/etiket_semasi.json").read_text(encoding="utf-8"))
    kayit = {
        "paragraf_id": "p1", "rapor_id": "sirket-x-2025", "beyan_turleri": ["yonetisim"],
        "kanit": {"TSRS2-YON-06a": [1]}, "kanit_metni": {"TSRS2-YON-06a": ["Komite toplanır."]},
        "belirsizlik": [], "emin": True, "sure_sn": 12, "cumle_sayisi": 1, "bolme_surumu": "2",
        "birim_turu": "paragraf", "etiketleyen": "M",
        "tarih": "2026-10-23", "sema_surumu": sema["sema_surumu"],
    }  # fmt: skip
    kayit |= kayit_degisikligi or {}
    yan = tmp_path / "pilot_v0.paragraf.jsonl"
    yan.write_text(json.dumps(kayit, ensure_ascii=False) + "\n", encoding="utf-8")
    return core, yan


def test_r_etk_01_paragraf_kaydi_gecerli(tmp_path):
    core, yan = _paragraf_dosyalari(tmp_path)
    assert validate_file(core) == [] and validate_file(yan) == []


def test_r_etk_01_paragraf_kaydi_hatalari(tmp_path):
    _, yan = _paragraf_dosyalari(tmp_path, {"beyan_turleri": ["uydurma"], "emin": False, "sema_surumu": "x"})
    errs = validate_file(yan)
    assert any("beyan türü" in e for e in errs)
    assert any("en az bir belirsizlik nedeni" in e for e in errs)
    assert any("şema sürümü" in e for e in errs)


def test_r_etk_01_paragraf_kaydi_kanit_metni_eslesir(tmp_path):
    _, yan = _paragraf_dosyalari(tmp_path, {"kanit_metni": {"TSRS2-YON-06a": ["Başka cümle."]}})
    assert any("eşleşmiyor" in e for e in validate_file(yan))
    _, yan = _paragraf_dosyalari(tmp_path, {"etiketleyen": "Z"})
    assert any("etiketleyen çekirdek CSV ile farklı" in e for e in validate_file(yan))
    _, yan = _paragraf_dosyalari(
        tmp_path, {"kanit": {}, "kanit_metni": {}, "belirsizlik": ["cikarim_hatasi"], "emin": False}
    )
    assert any("Çıkarım hatasında madde seçilmez" in e for e in validate_file(yan))


def test_r_etk_01_paragraf_kaydi_kanit_cekirdekle_tutarli(tmp_path):
    _, yan = _paragraf_dosyalari(tmp_path, {"kanit": {}})
    assert any("en az bir kanıt cümlesi" in e for e in validate_file(yan))
    _, yan = _paragraf_dosyalari(tmp_path, {"kanit": {"TSRS2-YON-06a": [3]}})
    assert any("1–1 arasında" in e for e in validate_file(yan))
    _, yan = _paragraf_dosyalari(tmp_path, karsilama="U")
    assert any("yalnızca 2 ya da 1 verilen maddeler" in e for e in validate_file(yan))


# ---------- yapısal tablo, olgu, şekil dosyaları (R-TAB-01…04, ADR-014) ----------


def _yapi_tablosu():
    hucreler = [
        {"satir": r, "sutun": c, "satir_kapsam": 1, "sutun_kapsam": 1, "metin": m, "sutun_basligi": r == 0,
         "satir_basligi": c == 0 and r > 0, "bolum_satiri": False, "sayfa": 3, "bbox": [0, 0, 10, 10]}
        for r, satir in enumerate([["Kapsam", "2024 (tCO2e)"], ["Kapsam 1", "12.450"]])
        for c, m in enumerate(satir)
    ]  # fmt: skip
    return {
        "tablo_id": "karel-2025-t003-01", "rapor_id": "karel-2025", "sayfalar": [3],
        "parcalar": [{"sayfa": 3, "bbox": [0, 0, 100, 40]}], "baslik": "Tablo 1", "dipnotlar": [], "birim": None,
        "satir_sayisi": 2, "sutun_sayisi": 2, "hucreler": hucreler, "motor": "insan", "paragraf_id": None,
        "uyarilar": [], "sema_surumu": "tablo-0.1",
    }  # fmt: skip


def _yapi_olgusu(**degisen):
    o = {
        "olgu_id": "karel-2025-t003-01-r01c01", "rapor_id": "karel-2025", "tablo_id": "karel-2025-t003-01",
        "satir": 1, "sutun": 1, "sayfa": 3, "bbox": [0, 0, 10, 10], "deger": 12450.0, "birim": "tCO2e",
        "carpan": 1.0, "birim_kaynagi": "sutun_basligi", "ham": "12.450", "eksik": False, "dipnot": [],
        "yil": False, "satir_yolu": ["Kapsam 1"], "sutun_yolu": ["2024 (tCO2e)"], "donem": "2024",
        "sema_surumu": "olgu-0.1",
    }  # fmt: skip
    return o | degisen


def _yaz_jsonl(yol, kayitlar):
    yol.write_text("".join(json.dumps(k, ensure_ascii=False) + "\n" for k in kayitlar), encoding="utf-8")
    return yol


def test_r_tab_01_gecerli_tablo_ve_olgu_dosyasi(tmp_path):
    t = _yaz_jsonl(tmp_path / "karel-2025.tables.jsonl", [_yapi_tablosu()])
    o = _yaz_jsonl(tmp_path / "karel-2025.facts.jsonl", [_yapi_olgusu()])
    assert validate_file(t) == [] and validate_file(o) == []


def test_r_tab_01_izgara_bosluklu_tablo_reddedilir(tmp_path):
    bozuk = _yapi_tablosu()
    bozuk["hucreler"].pop()
    errs = validate_file(_yaz_jsonl(tmp_path / "x.tables.jsonl", [bozuk, _yapi_tablosu()]))
    assert any("kaplanmayan" in e for e in errs) and any("tekrarlanan" in e for e in errs)


def test_r_tab_02_olgu_kaynakla_tutarsiz_reddedilir(tmp_path):
    _yaz_jsonl(tmp_path / "x.tables.jsonl", [_yapi_tablosu()])
    errs = validate_file(_yaz_jsonl(tmp_path / "x.facts.jsonl", [_yapi_olgusu(deger=1245.0)]))
    assert any("değer" in e for e in errs)
    (tmp_path / "x.tables.jsonl").unlink()
    assert any("tablo dosyası yok" in e for e in validate_file(tmp_path / "x.facts.jsonl"))


def test_r_tab_04_sekil_dosyasi_veri_durumu_tutarli(tmp_path):
    s = {
        "sekil_id": "x-g001-01", "rapor_id": "x", "sayfa": 1, "bbox": [0, 0, 10, 10], "tur": "grafik",
        "baslik": "", "metin": "", "veri": [{"kategori": "A", "seri": None, "deger": 1.0, "ham": "1", "bbox": None}],
        "veri_durumu": "goruntu_veri_yok", "eslesmeyen_etiket": 0, "motor": "pymupdf", "sinif": None,
        "uyarilar": [], "sema_surumu": "sekil-0.1",
    }  # fmt: skip
    errs = validate_file(_yaz_jsonl(tmp_path / "x.figures.jsonl", [s]))
    assert any("vektor_etiket" in e for e in errs)


def test_r_tab_02_bulgu_olgu_deger_null_eksik_false_cokmez(tmp_path):
    _yaz_jsonl(tmp_path / "x.tables.jsonl", [_yapi_tablosu()])
    errs = validate_file(_yaz_jsonl(tmp_path / "x.facts.jsonl", [_yapi_olgusu(deger=None)]))
    assert any("değer" in e for e in errs)
