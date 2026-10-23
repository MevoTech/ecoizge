#!/usr/bin/env python3
"""Şekil ve grafik çıkarımı (R-TAB-04, ADR-014).

Bir sürdürülebilirlik raporundaki grafiğin verisi üç biçimde bulunabilir; bu modül yalnızca ilkini okur:

1. **Vektör grafik + yazılı veri etiketleri** (Akbank 2025 Şekil 5–6): çubuklar PDF çizimi, değerler metin.
   Değer, etiket metninden `report_service.verify.numbers.hucre_degeri` ile **kesin** okunur; çubuk geometrisi
   yalnızca etiketi çubuğa, çubuğu kategoriye (eksen yazısı) ve seriye (lejant rengi) bağlamak için kullanılır.
   Etiketi olmayan çubuğa değer **verilmez** (boydan ölçek tahmini yapılmaz).
2. Vektör grafik, etiketsiz (yalnızca eksen): değer ancak eksen ölçeğinden yaklaşık okunabilir → yapılmaz,
   `yalniz_etiket` ya da `veri_yok` olarak işaretlenir.
3. **Görüntü (raster) grafik:** metin katmanı yok; veri ancak görüntü modeliyle (ör. Docling
   `do_chart_extraction`, granite-vision) yaklaşık çıkarılabilir → `goruntu_veri_yok`, uyarı
   `goruntu_veri_cikarilmadi` (KL-14).

Çıktı şeması `tools/tablo_kurallari.py` (SEKIL_ALANLARI).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_KOK = Path(__file__).resolve().parent.parent
for _yol in (_KOK / "tools", _KOK / "services" / "report-service", _KOK / "pipelines"):
    if str(_yol) not in sys.path:
        sys.path.insert(0, str(_yol))

from extract import BAND  # noqa: E402
from tablo_kurallari import SEKIL_SURUMU  # noqa: E402

from report_service.verify.numbers import hucre_degeri  # noqa: E402

SEKIL_BASLIK_RE = re.compile(r"^\s*(Grafik|Şekil|Sekil|Figür|Figure|Chart)\s*\d+", re.IGNORECASE)
EN_KUCUK_ALAN = 0.02  # sayfa alanına oran: daha küçük görüntü süs/ikon sayılır
PANEL_ORANI = 0.10  # tek bir dolu çizim sayfanın bu oranından büyükse arka plan paneli sayılır
KUME_TOL = 30.0  # grafik çekirdeği çevresinde etiketlerin toplandığı pay (pt)
KATEGORI_PAYI = 200.0  # kategori yazılarının arandığı pay: dikeyde tabanın altı, yatayda çubukların solu
EN_BUYUK_ALAN = 0.85  # daha büyüğü arka plan
LEJANT_KENAR = 12.0  # lejant karesi en çok bu kadar (pt)
ETIKET_ARALIGI = 15.0  # etiket ile çubuk ucu arası en çok (pt)
BASLIK_ARALIGI = 80.0  # grafik ile başlığı arasında lejant da olabilir (Akbank 2025 Şekil 5)


def _renk(r) -> tuple[float, ...] | None:
    return tuple(round(v, 2) for v in r) if r else None


def _beyaz(r) -> bool:
    return r is not None and all(v >= 0.95 for v in r)


def _merkez(b) -> tuple[float, float]:
    return (b[0] + b[2]) / 2, (b[1] + b[3]) / 2


def _icinde(b, alan, pay: float = 1.0) -> bool:
    cx, cy = _merkez(b)
    return alan[0] - pay <= cx <= alan[2] + pay and alan[1] - pay <= cy <= alan[3] + pay


def _lejant_karesi(b) -> bool:
    w, h = b[2] - b[0], b[3] - b[1]
    return 0 < w <= LEJANT_KENAR and 0 < h <= LEJANT_KENAR and 0.6 <= w / h <= 1.6


def cubuk_verisi(
    cubuklar: list[dict], metinler: list[dict], lejant: dict[tuple, str]
) -> tuple[list[dict], int]:
    """Çubuk grafikte (etiket → çubuk → kategori, seri) eşlemesi. Saf fonksiyon (geometri girdisi).

    `cubuklar`: [{"bbox", "renk"}]; `metinler`: [{"bbox", "metin"}] (lejant yazıları hariç);
    `lejant`: renk → seri adı. Dönüş: (veri, eşleşmeyen sayısal etiket sayısı).
    Eksen işaretleri (dikeyde çubukların solunda, yatayda çubukların altında kalan sayılar) değer sayılmaz.
    """
    if not cubuklar:
        return [], 0
    dikey = sum(c["bbox"][3] - c["bbox"][1] >= c["bbox"][2] - c["bbox"][0] for c in cubuklar) * 2 >= len(
        cubuklar
    )
    if dikey:
        taban = max(c["bbox"][3] for c in cubuklar)
        sol = min(c["bbox"][0] for c in cubuklar)
        kategori_bolgesi = [m for m in metinler if m["bbox"][1] >= taban - 2]
        eksen = [m for m in metinler if m["bbox"][2] <= sol + 1 and m not in kategori_bolgesi]
    else:
        sol = min(c["bbox"][0] for c in cubuklar)
        taban = max(c["bbox"][3] for c in cubuklar)
        kategori_bolgesi = [m for m in metinler if m["bbox"][2] <= sol + 2]
        eksen = [m for m in metinler if m["bbox"][1] >= taban - 1 and m not in kategori_bolgesi]
    adaylar = [
        (m, hd)
        for m in metinler
        if m not in kategori_bolgesi and m not in eksen
        for hd in [hucre_degeri(m["metin"])]
        if hd is not None and not hd.eksik and not hd.yil  # yıl etiketi eksen/kategori yazısıdır, değer değil
    ]
    kullanilan: set[int] = set()
    veri: list[tuple[float, dict]] = []
    eslesmeyen = 0
    for m, hd in adaylar:
        mx, my = _merkez(m["bbox"])
        en_iyi, mesafe = None, float("inf")
        for i, c in enumerate(cubuklar):
            if i in kullanilan:
                continue
            b = c["bbox"]
            cx, cy = _merkez(b)
            if dikey:
                hizali = abs(mx - cx) <= max((b[2] - b[0]) / 2, 6)
                d = b[1] - m["bbox"][3]  # etiket çubuğun üstünde
                icinde = b[1] <= my <= b[3]
            else:
                hizali = abs(my - cy) <= max((b[3] - b[1]) / 2, 6)
                d = m["bbox"][0] - b[2]  # etiket çubuğun sağında
                icinde = b[0] <= mx <= b[2]
            if hizali and (icinde or -2 <= d <= ETIKET_ARALIGI):
                d = 0 if icinde else abs(d)
                if d < mesafe:
                    en_iyi, mesafe = i, d
        if en_iyi is None:
            eslesmeyen += 1
            continue
        kullanilan.add(en_iyi)
        c = cubuklar[en_iyi]
        veri.append(
            (
                _merkez(c["bbox"])[0] if dikey else _merkez(c["bbox"])[1],
                {
                    "kategori": _kategori(c["bbox"], kategori_bolgesi, dikey),
                    "seri": lejant.get(_renk(c["renk"])),
                    "deger": hd.deger,
                    "ham": m["metin"],
                    "bbox": [round(v, 2) for v in m["bbox"]],
                },
            )
        )
    return [v for _, v in sorted(veri, key=lambda x: x[0])], eslesmeyen


def _kategori(b, adaylar: list[dict], dikey: bool) -> str | None:
    cx, cy = _merkez(b)
    if dikey:
        uygun = [m for m in adaylar if m["bbox"][1] - b[3] <= 40]
        if not uygun:
            return None
        return min(uygun, key=lambda m: (abs(_merkez(m["bbox"])[0] - cx), m["bbox"][1]))["metin"]
    uygun = [m for m in adaylar if abs(_merkez(m["bbox"])[1] - cy) <= max(b[3] - b[1], 8)]
    return max(uygun, key=lambda m: m["bbox"][2])["metin"] if uygun else None


def _satirlar(page, alan=None) -> list[dict]:
    out = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            metin = " ".join("".join(s["text"] for s in ln["spans"]).split())
            if metin and (alan is None or _icinde(ln["bbox"], alan)):
                out.append({"bbox": list(ln["bbox"]), "metin": metin})
    return out


def _baslik(satirlar: list[dict], alan) -> str:
    adaylar = [
        s
        for s in satirlar
        if SEKIL_BASLIK_RE.match(s["metin"])
        and (0 <= s["bbox"][1] - alan[3] <= BASLIK_ARALIGI or 0 <= alan[1] - s["bbox"][3] <= BASLIK_ARALIGI)
        and s["bbox"][0] < alan[2] and s["bbox"][2] > alan[0]
    ]  # fmt: skip
    if not adaylar:
        return ""
    return min(adaylar, key=lambda s: min(abs(s["bbox"][1] - alan[3]), abs(alan[1] - s["bbox"][3])))["metin"]


def _kayit(rapor_id, sayfa, sira, bbox, tur, baslik, metin, veri, durum, eslesmeyen, motor, uyarilar) -> dict:
    return {
        "sekil_id": f"{rapor_id}-g{sayfa:03d}-{sira:02d}",
        "rapor_id": rapor_id,
        "sayfa": sayfa,
        "bbox": [round(v, 2) for v in bbox],
        "tur": tur,
        "baslik": baslik,
        "metin": metin,
        "veri": veri,
        "veri_durumu": durum,
        "eslesmeyen_etiket": eslesmeyen,
        "motor": motor,
        "sinif": None,
        "uyarilar": uyarilar,
        "sema_surumu": SEKIL_SURUMU,
    }


def cubuk_gruplari(dikdortgenler: list[dict]) -> list[tuple[list[dict], bool]]:
    """Ortak tabana göre çubuk grupları: dikey çubuklar aynı alt kenarı, yatay çubuklar aynı sol kenarı paylaşır.

    Her grup bir çubuk grafiğin çekirdeğidir. Aynı tabandaki iki ayrı grafik, çubuklar arası boşluk
    çubuk genişliğinin 6 katını (en az 100 pt) aşınca ayrılır. Bütün boyları eşit grup çubuk grafik sayılmaz
    (tablo başlık dolguları). Dönüş: [(çubuklar, dikey_mi)].
    """
    kalan = [d for d in dikdortgenler if not _lejant_karesi(d["bbox"])]
    out: list[tuple[list[dict], bool]] = []
    while True:
        adaylar: list[tuple[list[dict], bool]] = []
        for dikey in (True, False):
            anahtar: dict[int, list[dict]] = {}
            for d in kalan:
                k = d["bbox"][3] if dikey else d["bbox"][0]
                anahtar.setdefault(round(k / 1.5), []).append(d)
            adaylar += [(g, dikey) for g in anahtar.values() if len(g) >= 2]
        if not adaylar:
            return out
        grup, dikey = max(adaylar, key=lambda x: len(x[0]))
        kalan = [d for d in kalan if d not in grup]
        boylar = [(d["bbox"][3] - d["bbox"][1]) if dikey else (d["bbox"][2] - d["bbox"][0]) for d in grup]
        if max(boylar) - min(boylar) <= 1.0:
            continue  # bütün "çubuklar" eşit boyda: tablo başlığı dolgusu ya da süs (Akbank 2025 s. 6)
        eksen = 0 if dikey else 1
        grup = sorted(grup, key=lambda d: d["bbox"][eksen])
        kalinlik = sorted(d["bbox"][eksen + 2] - d["bbox"][eksen] for d in grup)[len(grup) // 2]
        parca = [grup[0]]
        for d in grup[1:]:
            if d["bbox"][eksen] - parca[-1]["bbox"][eksen + 2] > max(100.0, 6 * kalinlik):
                out.append((parca, dikey)) if len(parca) >= 2 else None
                parca = []
            parca.append(d)
        if len(parca) >= 2:
            out.append((parca, dikey))


def _birlesim(kutular) -> list[float]:
    return [
        min(k[0] for k in kutular),
        min(k[1] for k in kutular),
        max(k[2] for k in kutular),
        max(k[3] for k in kutular),
    ]


def sayfa_sekilleri(
    page, sayfa: int, rapor_id: str, tablo_alanlari: list[list[float]] | None = None
) -> list[dict]:
    """Bir sayfanın şekilleri: (1) ortak tabanlı çubuk grupları, (2) diğer çizim kümeleri, (3) görüntüler."""
    tablo_alanlari = tablo_alanlari or []
    alan_sayfa = page.rect.width * page.rect.height
    satirlar = _satirlar(page)

    def boy(b) -> float:
        return (b[2] - b[0]) * (b[3] - b[1]) / alan_sayfa

    def tabloda(b) -> bool:
        return any(_icinde(b, t, 2) for t in tablo_alanlari)

    cizimler: list[dict] = []
    for d in page.get_drawings():
        if d.get("fill") is None or d.get("rect") is None or _beyaz(d["fill"]):
            continue
        # Bir yol birden çok dikdörtgen içerebilir (üreticiler çubukları tek yolda toplar); her biri ayrı çubuk
        parcalar = [it[1] for it in d["items"] if it[0] == "re"] + [
            it[1].rect for it in d["items"] if it[0] == "qu"
        ]
        if len(parcalar) != len(d["items"]):
            parcalar = [d["rect"]]
        for r in parcalar:
            b = [r.x0, r.y0, r.x1, r.y1]
            if boy(b) < PANEL_ORANI and not tabloda(b) and r.width > 0 and r.height > 0:
                cizimler.append({"bbox": b, "renk": d["fill"], "cizim": d})
    out: list[dict] = []
    kullanilan: list[list[float]] = []

    # (1) çubuk grafikler
    for cubuklar, dikey in cubuk_gruplari(cizimler):
        cekirdek = _birlesim([c["bbox"] for c in cubuklar])
        # metin toplama alanı: her yanda KUME_TOL, kategori tarafında (dikeyde alt, yatayda sol) daha geniş
        genis = [cekirdek[0] - (KATEGORI_PAYI if not dikey else KUME_TOL), cekirdek[1] - KUME_TOL,
                 cekirdek[2] + KUME_TOL, cekirdek[3] + (KATEGORI_PAYI if dikey else KUME_TOL)]  # fmt: skip
        icerik = [s for s in satirlar if _icinde(s["bbox"], genis)]
        kareler = [c for c in cizimler if _lejant_karesi(c["bbox"]) and _icinde(c["bbox"], genis)]
        lejant, lejant_metni = _lejant(kareler, icerik)
        baslik = _baslik(satirlar, cekirdek)
        metinler = [s for s in icerik if s not in lejant_metni and s["metin"] != baslik]
        veri, eslesmeyen = cubuk_verisi(cubuklar, metinler, lejant)
        if len(veri) < 2:
            continue
        b = _birlesim([cekirdek, *(v["bbox"] for v in veri)])
        kullanilan.append(genis)
        uyarilar = ["eslesmeyen_etiket_var"] if eslesmeyen else []
        if len(veri) < len(cubuklar):
            uyarilar.append("etiketsiz_cubuk_var")
        out.append(_kayit(rapor_id, sayfa, 0, b, "grafik", baslik, " ".join(s["metin"] for s in icerik), veri,
                          "vektor_etiket", eslesmeyen, "pymupdf", uyarilar))  # fmt: skip

    # (2) diğer vektör çizim kümeleri (pasta, çizgi, akış şeması …): veri okunmaz, yalnızca etiketler sayılır
    kalan = [c for c in cizimler if not any(_icinde(c["bbox"], k) for k in kullanilan)]
    for r in (
        page.cluster_drawings(drawings=list({id(c["cizim"]): c["cizim"] for c in kalan}.values()))
        if kalan
        else []
    ):
        b = [r.x0, r.y0, r.x1, r.y1]
        if not EN_KUCUK_ALAN <= boy(b) <= EN_BUYUK_ALAN or tabloda(b):
            continue
        icerik = [s for s in satirlar if _icinde(s["bbox"], b)]
        baslik = _baslik(satirlar, b)
        sayisal = [s for s in icerik if (hd := hucre_degeri(s["metin"])) is not None and not hd.eksik]
        if len(sayisal) >= 3:
            durum, tur, uyari = "yalniz_etiket", "grafik", ["etiketsiz_veri_okunmadi"]
        elif baslik:
            durum, tur, uyari = "veri_yok", "sekil", []
        else:
            continue  # süs, çerçeve, simge
        kullanilan.append(b)
        out.append(_kayit(rapor_id, sayfa, 0, b, tur, baslik, " ".join(s["metin"] for s in icerik), [], durum, 0,
                          "pymupdf", uyari))  # fmt: skip

    # (3) görüntüler
    for im in page.get_image_info():
        b = list(im["bbox"])
        if (
            not EN_KUCUK_ALAN <= boy(b) <= EN_BUYUK_ALAN
            or tabloda(b)
            or any(_icinde(b, k) for k in kullanilan)
        ):
            continue
        baslik = _baslik(satirlar, b)
        if any(_icinde(s["bbox"], b) for s in satirlar):
            continue  # metin katmanı üstte: görüntü arka plan ya da süs
        tur = "grafik" if baslik else "sekil"
        out.append(_kayit(rapor_id, sayfa, 0, b, tur, baslik, "", [], "goruntu_veri_yok", 0, "pymupdf",
                          ["goruntu_veri_cikarilmadi"]))  # fmt: skip

    out.sort(key=lambda s: (s["bbox"][1], s["bbox"][0]))
    for i, s in enumerate(out, start=1):
        s["sekil_id"] = f"{rapor_id}-g{sayfa:03d}-{i:02d}"
    return out


def _lejant(kareler: list[dict], metinler: list[dict]) -> tuple[dict[tuple, str], list[dict]]:
    lejant: dict[tuple, str] = {}
    kullanilan: list[dict] = []
    for k in kareler:
        yan = [
            s for s in metinler
            if 0 <= s["bbox"][0] - k["bbox"][2] <= 10 and abs(_merkez(s["bbox"])[1] - _merkez(k["bbox"])[1]) <= 6
        ]  # fmt: skip
        if yan:
            s = min(yan, key=lambda s: s["bbox"][0])
            lejant[_renk(k["renk"])] = s["metin"]
            kullanilan.append(s)
    return lejant, kullanilan


def cikar(
    pdf_path: Path, rapor_id: str, tablo_alanlari: dict[int, list[list[float]]] | None = None
) -> list[dict]:
    """Belgedeki şekil ve grafikler. `tablo_alanlari`: sayfa → tablo bbox listesi (tablolar şekil sayılmaz)."""
    import pymupdf

    doc = pymupdf.open(pdf_path)
    out: list[dict] = []
    for sayfa, page in enumerate(doc, start=1):
        bant = page.rect.height * BAND
        sekiller = sayfa_sekilleri(page, sayfa, rapor_id, (tablo_alanlari or {}).get(sayfa))
        out += [s for s in sekiller if not (s["bbox"][3] < bant or s["bbox"][1] > page.rect.height - bant)]
    return out
