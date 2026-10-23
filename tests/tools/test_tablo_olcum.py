"""Tablo ölçümü testleri (R-TAB-05): GriTS tanım özellikleri, tespit ve olgu P/R/F1, CLI run_id zorunluluğu."""

from __future__ import annotations

import json

import pytest
import tablo_olcum as to


def _tablo(satirlar, tid="t1", sayfa=1, bbox=(0, 0, 100, 100), kapsam=None):
    """kapsam: {(r, c): (satir_kapsam, sutun_kapsam)}; kaplanan konumlar satirlar'da None."""
    kapsam = kapsam or {}
    hucreler = []
    for r, satir in enumerate(satirlar):
        for c, m in enumerate(satir):
            if m is None:
                continue
            a, b = kapsam.get((r, c), (1, 1))
            hucreler.append({"satir": r, "sutun": c, "satir_kapsam": a, "sutun_kapsam": b, "metin": m,
                             "sutun_basligi": r == 0, "satir_basligi": False, "bolum_satiri": False,
                             "sayfa": sayfa, "bbox": None})  # fmt: skip
    return {"tablo_id": tid, "satir_sayisi": len(satirlar), "sutun_sayisi": len(satirlar[0]),
            "hucreler": hucreler, "parcalar": [{"sayfa": sayfa, "bbox": list(bbox)}]}  # fmt: skip


A = [["Kapsam", "2024", "2025"], ["Kapsam 1", "12.450", "13.100"], ["Kapsam 2", "31.200", "30.900"]]


def test_r_tab_05_grits_ozdes_tablo_bir():
    assert to.grits_con(_tablo(A), _tablo(A)) == pytest.approx(1.0)
    assert to.grits_top(_tablo(A), _tablo(A)) == pytest.approx(1.0)


def test_r_tab_05_grits_fazla_satir_formulu():
    """Tahminde fazladan boş satır: eşleşen 9 konum → F = 2·9 / (9 + 12)."""
    tahmin = _tablo([*A, ["", "", ""]])
    assert to.grits_con(_tablo(A), tahmin) == pytest.approx(18 / 21)
    assert to.grits_top(_tablo(A), tahmin) == pytest.approx(18 / 21)


def test_r_tab_05_grits_con_hucre_metni_farki():
    tahmin = _tablo(
        [["Kapsam", "2024", "2025"], ["Kapsam 1", "12 450", "13.100"], ["Kapsam 2", "31.200", "30.900"]]
    )
    beklenen = (8 + to.lcs_benzerligi("12.450", "12 450")) / 9
    assert to.grits_con(_tablo(A), tahmin) == pytest.approx(beklenen)
    assert to.grits_top(_tablo(A), tahmin) == pytest.approx(1.0)  # yapı aynı


def test_r_tab_05_grits_top_birlesik_baslik_yakalanir():
    """Gerçekte 'Emisyon' iki sütunu kaplar; tahmin onu iki ayrı hücre sanırsa Top < 1, Con = 1 değil."""
    gercek = _tablo([["Kapsam", "Emisyon", None], ["Kapsam 1", "12.450", "13.100"]], kapsam={(0, 1): (1, 2)})
    tahmin = _tablo([["Kapsam", "Emisyon", "Emisyon"], ["Kapsam 1", "12.450", "13.100"]])
    assert to.grits_top(gercek, tahmin) < 1.0
    assert to.grits_con(gercek, tahmin) == pytest.approx(1.0)  # konum başına metin aynı


def test_r_tab_05_grits_sutun_kaymasi_hizalanir():
    """Tahminde başa boş sütun eklenmiş: hizalama sütunu atlar, kaydırmaz."""
    tahmin = _tablo([["", *r] for r in A])
    assert to.grits_con(_tablo(A), tahmin) == pytest.approx(18 / 21)


def test_r_tab_05_tespit_iou_ile_eslesir():
    gercek = [_tablo(A, "g1", 1, (0, 0, 100, 100)), _tablo(A, "g2", 2, (0, 0, 100, 100))]
    tahmin = [
        _tablo(A, "t1", 1, (5, 5, 100, 100)),
        _tablo(A, "t2", 2, (300, 300, 400, 400)),
        _tablo(A, "t3", 3),
    ]
    s = to.olc(gercek, tahmin)
    assert (s["tespit"]["tp"], s["tespit"]["p"], s["tespit"]["r"]) == (1, pytest.approx(1 / 3), 0.5)
    assert s["grits_con_eslenen_ort"] == pytest.approx(1.0)
    assert s["grits_con_tum_gercek_ort"] == pytest.approx(0.5)


def test_r_tab_05_kutusuz_altin_tablo_icerikle_eslesir():
    """İnsan altın kümesinde kutu yok ([0, 0, 0, 0]): aynı sayfada en benzer içerikli tahminle eşlenir."""
    gercek = [_tablo(A, "g1", 4, (0, 0, 0, 0))]
    baska = _tablo([["Fırsat", "Açıklama"], ["Enerji", "Verimlilik yatırımı"]], "t1", 4, (0, 0, 50, 50))
    s = to.olc(gercek, [baska, _tablo(A, "t2", 4, (0, 300, 100, 400))])
    assert [x["tahmin"] for x in s["tablo_bazinda"]] == ["t2"]


def _olgu(deger, satir="Kapsam 1", donem="2024", birim="tCO2e", sayfa=1):
    return {"sayfa": sayfa, "deger": deger, "birim": birim, "donem": donem, "satir_yolu": [satir]}


def test_r_tab_05_olgu_prf_ve_yalniz_deger():
    gercek = [_olgu(12450), _olgu(13100, donem="2025"), _olgu(31200, "Kapsam 2")]
    tahmin = [_olgu(12450), _olgu(13100, donem="2024"), _olgu(99, "Kapsam 3")]
    s = to.olgu_prf(gercek, tahmin)
    assert (s["tp"], s["p"], s["r"]) == (1, pytest.approx(1 / 3), pytest.approx(1 / 3))
    assert s["yalniz_deger"]["tp"] == 2  # 13.100 değeri doğru, dönemi yanlış


def test_r_tab_05_olgu_satir_basligi_turkce_buyuk_kucuk_esit():
    assert to.olgu_prf([_olgu(1, "KAPSAM 1 (İSTANBUL)")], [_olgu(1, "Kapsam 1 (istanbul)")])["tp"] == 1


def test_r_tab_05_cli_run_id_zorunlu(tmp_path, capsys):
    yol = tmp_path / "t.jsonl"
    yol.write_text(json.dumps(_tablo(A), ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        to.main(["--gercek", str(yol), "--tahmin", str(yol)])
    out = tmp_path / "olcum.json"
    assert (
        to.main(["--gercek", str(yol), "--tahmin", str(yol), "--run-id", "deneme-1", "--out", str(out)]) == 0
    )
    sonuc = json.loads(out.read_text(encoding="utf-8"))
    assert sonuc["run_id"] == "deneme-1" and len(sonuc["sha256"]["gercek"]) == 64
    assert sonuc["tespit"]["f1"] == 1.0
