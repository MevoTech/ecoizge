#!/usr/bin/env python3
"""Yapısal tablo çıkarımı: hücre ızgarası, başlıklar, sayfalar arası birleştirme ve olgular (R-TAB-01…03, ADR-014).

`pipelines/extract.py` tabloyu tek bir metin birimi olarak verir ("a | b" satırları); bu modül aynı tabloyu
**ızgara** olarak verir: her hücrenin satır/sütun konumu, kapsamı (birleşik hücre), başlık rolü, sayfası ve
koordinatı. Ardından her sayısal veri hücresinden bir **olgu** üretir: değer, birim, satır yolu, sütun yolu,
dönem ve kaynak koordinatı. Taslaktaki sayılar (ADR-004) bu olgulardan doldurulur ve doğrulanır.

Motorlar (kayıt biçimi motordan bağımsızdır; `tools/tablo_kurallari.py`):
- `pymupdf`: çizgili tablolar, `page.find_tables()`; hücre metni hücre alanından okunur (Türkçe binlik
  ayracı korunur, pdf-extract Tuzaklar).
- `pymupdf-bosluk`: `find_tables`'ın bulamadığı kenarlıksız tablolar için **sezgisel** yöntem (Klimasan 2025
  s. 37). Yalnızca "Tablo N" başlığının altındaki bölgede çalışır: başlık satırı bandının yatay kesimleri sütunları, dikey boşluklar satırları verir
  (izdüşüm profili / X-Y kesimi). Uyarı `kenarliksiz_sezgisel` ile işaretlenir.
- `docling`: TableFormer modeli (isteğe bağlı bağımlılık; `docling_tablosu` uyarlayıcısı).

Başlık rolleri motor vermediyse sezgiyle belirlenir (`basliklari_belirle`). Sayılar yalnızca
`report_service.verify.numbers` ile ayrıştırılır.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from pathlib import Path

_KOK = Path(__file__).resolve().parent.parent
for _yol in (_KOK / "tools", _KOK / "services" / "report-service", _KOK / "pipelines"):
    if str(_yol) not in sys.path:
        sys.path.insert(0, str(_yol))

from extract import BAND, join_lines  # noqa: E402
from tablo_kurallari import OLGU_SURUMU, TABLO_SURUMU, YIL, izgara  # noqa: E402

from report_service.generation.placeholders import IDENTIFIER  # noqa: E402
from report_service.verify.numbers import birim_bul, birimler_bul, extract_numbers, hucre_degeri  # noqa: E402

BASLIK_RE = re.compile(r"^\s*(Tablo|Table)\s*\d+", re.IGNORECASE)
ICINDEKILER_RE = re.compile(r"[İi]çindekiler|İÇİNDEKİLER|contents|sayfa", re.IGNORECASE)
TARIH_RE = re.compile(r"(?<!\d)\d{1,2}[./]\d{1,2}[./]((?:19|20)\d{2})(?!\d)")
DIPNOT_RE = re.compile(r"^\s*(\*+|[¹²³⁴⁵⁶⁷⁸⁹]|\(\d{1,2}\)|\d{1,2}\)|Not\s*:|Kaynak\s*:|Açıklama\s*:)")
BASLIK_ARALIGI = 30.0  # tablo başlığı tablonun en çok bu kadar üstünde (pt)
DIPNOT_ARALIGI = 25.0
KUMELEME_TOL = 2.0  # hücre kenarlarının aynı ızgara çizgisi sayılma toleransı (pt)
BIRLESTIRME_ALT = 0.70  # önceki sayfadaki tablo sayfanın bu oranından aşağıda bitmeli
BIRLESTIRME_UST = 0.35  # sonraki sayfadaki tablo bu orandan yukarıda başlamalı
SUTUN_TOL = 15.0  # birleştirmede sütun sol kenarlarının farkı (pt)


# ---------- kayıt ----------


def bos_hucre(r: int, c: int, sayfa: int, bbox: list[float] | None = None) -> dict:
    return {
        "satir": r, "sutun": c, "satir_kapsam": 1, "sutun_kapsam": 1, "metin": "",
        "sutun_basligi": False, "satir_basligi": False, "bolum_satiri": False, "sayfa": sayfa, "bbox": bbox,
    }  # fmt: skip


def tablo_kaydi(
    rapor_id: str,
    sayfa: int,
    sira: int,
    hucreler: list[dict],
    satir_sayisi: int,
    sutun_sayisi: int,
    motor: str,
    bbox: list[float],
    *,
    baslik: str = "",
    dipnotlar: list[str] | None = None,
    uyarilar: list[str] | None = None,
) -> dict:
    birim = birim_bul(baslik) if baslik else None
    return {
        "tablo_id": f"{rapor_id}-t{sayfa:03d}-{sira:02d}",
        "rapor_id": rapor_id,
        "sayfalar": [sayfa],
        "parcalar": [{"sayfa": sayfa, "bbox": [round(v, 2) for v in bbox]}],
        "baslik": baslik,
        "dipnotlar": dipnotlar or [],
        "birim": {"taban": birim[0], "carpan": birim[1], "kaynak": "tablo_basligi"} if birim else None,
        "satir_sayisi": satir_sayisi,
        "sutun_sayisi": sutun_sayisi,
        "hucreler": sorted(hucreler, key=lambda h: (h["satir"], h["sutun"])),
        "motor": motor,
        "paragraf_id": None,
        "uyarilar": uyarilar or [],
        "sema_surumu": TABLO_SURUMU,
    }


def _bosluklari_doldur(hucreler: list[dict], n: int, m: int, sayfa: int) -> list[dict]:
    dolu = {
        (r, c)
        for h in hucreler
        for r in range(h["satir"], h["satir"] + h["satir_kapsam"])
        for c in range(h["sutun"], h["sutun"] + h["sutun_kapsam"])
    }
    return hucreler + [bos_hucre(r, c, sayfa) for r in range(n) for c in range(m) if (r, c) not in dolu]


# ---------- başlık rolleri ----------


def _tam_izgara(t: dict) -> list[list[int]]:
    """Izgara; kaplanmayan konum varsa ValueError (sessizce son hücreyi okumamak için, inceleme bulgu 4)."""
    g = izgara(t)
    if any(-1 in row for row in g):
        raise ValueError(f"{t['tablo_id']}: ızgarada kaplanmayan konum var")
    return g


def _sayisal(metin: str) -> bool:
    """Veri hücresi gibi sayısal mı (yıl ve eksik değer işaretleri başlıkta da görülür, sayılmaz)."""
    h = hucre_degeri(metin)
    return h is not None and not h.eksik and not h.yil


def basliklari_belirle(t: dict) -> dict:
    """Motor başlık rolü vermediyse sezgiyle belirler; verdiyse dokunmaz. Tabloyu yerinde değiştirir.

    - Sütun başlığı: baştaki, hiç sayısal veri hücresi olmayan satırlar (en çok 3). Tabloda hiç sayısal
      hücre yoksa yalnızca ilk satır.
    - Satır başlığı: ilk sayısal sütunun solunda kalan ve gövdede hiç sayısal olmayan sütunlar.
    - Bölüm satırı: gövdede tek dolu hücresi olan, o hücre satır başlığı sütununda olan ve birim anmayan satır.
      (Değerleri boş bir veri satırı da bu tanıma uyabilir; biçim bilgisi olmadan ayırt edilemez, KL-13.)
    """
    g = _tam_izgara(t)
    n, m = t["satir_sayisi"], t["sutun_sayisi"]
    hc = t["hucreler"]
    satir_sayisal = [any(_sayisal(hc[i]["metin"]) for i in set(row)) for row in g]
    if not any(h["sutun_basligi"] for h in hc):
        k = 0
        while k < min(3, n - 1) and not satir_sayisal[k]:
            k += 1
        if not any(satir_sayisal):
            k = 1 if n > 1 else 0
        for i in {g[r][c] for r in range(k) for c in range(m)}:
            hc[i]["sutun_basligi"] = True
    govde = [r for r in range(n) if not all(hc[i]["sutun_basligi"] for i in g[r])]
    if not any(h["satir_basligi"] or h["bolum_satiri"] for h in hc):
        sayisal_sutun = [c for c in range(m) if any(_sayisal(hc[g[r][c]]["metin"]) for r in govde)]
        if sayisal_sutun:
            baslik_sutunlari = range(min(sayisal_sutun))
            for r in govde:
                dolu = [i for i in dict.fromkeys(g[r]) if hc[i]["metin"].strip()]
                for c in baslik_sutunlari:
                    i = g[r][c]
                    if hc[i]["metin"].strip() and not hc[i]["sutun_basligi"]:
                        hc[i]["satir_basligi"] = True
                        if len(dolu) == 1 and not birimler_bul(hc[i]["metin"]):
                            # birimli tek dolu hücre ("Su (m³)") değeri boş bir veri satırıdır, bölüm değil
                            hc[i]["bolum_satiri"] = True
    return t


# ---------- olgular ----------


def denetle(t: dict, sayfa_sayisi: int) -> dict:
    """Çıkarım hatası belirtilerini `uyarilar`a yazar (yerinde). Gerçek raporlarda görülen iki durum:

    - `baslikta_sayisal_veri`: bir sütun başlığı hücresinde yıl olmayan sayı var; başlık satırı veri satırını
      yutmuş olabilir (Klimasan 2025 s. 51). Bu hücreden birim alınmaz (`_birim`).
    - `icindekiler_olasi`: sayısal hücrelerin hepsi tek sütunda, tam sayı, 1…sayfa sayısı aralığında ve
      artan; başlıkta yıl ya da birim yok; "Tablo N" başlığı yok; sütun başlığı yok ya da "İçindekiler". İçindekiler sayfa numaraları olgu değildir (`olgular` atlar).
    """
    hc = t["hucreler"]
    uyari = list(t["uyarilar"])
    if any(h["sutun_basligi"] and not _guvenilir_baslik(h["metin"]) for h in hc):
        uyari.append("baslikta_sayisal_veri")
    g = izgara(t)
    sayisal = [
        (c, hucre_degeri(hc[i]["metin"]))
        for r, row in enumerate(g)
        for c, i in enumerate(row)
        if not hc[i]["sutun_basligi"]
        and (r, c) == (hc[i]["satir"], hc[i]["sutun"])
        and _sayisal(hc[i]["metin"])
    ]
    basliklar = " ".join(h["metin"] for h in hc if h["sutun_basligi"])
    degerler = [hd.deger for _, hd in sayisal]
    if (
        len(sayisal) >= 3
        and len({c for c, _ in sayisal}) == 1
        and all(
            hd.birim is None and float(hd.deger).is_integer() and 1 <= hd.deger <= sayfa_sayisi
            for _, hd in sayisal
        )
        and sum(a <= b for a, b in zip(degerler, degerler[1:], strict=False)) >= 0.8 * (len(degerler) - 1)
        and not YIL.search(basliklar)
        and not birimler_bul(basliklar)
        and not BASLIK_RE.match(t["baslik"])  # "Tablo N" başlıklı tablo içindekiler değildir
        and (not basliklar.strip() or ICINDEKILER_RE.search(basliklar))  # sütun adı varsa veri tablosudur
    ):
        uyari.append("icindekiler_olasi")
    t["uyarilar"] = list(dict.fromkeys(uyari))
    return t


def olgular(t: dict) -> list[dict]:
    """Her sayısal veri hücresi için bir olgu: değer + birim + satır/sütun yolu + dönem + kaynak.

    İçindekiler olası tablolar (`denetle`) olgu üretmez.
    """
    if "icindekiler_olasi" in t["uyarilar"]:
        return []
    g = _tam_izgara(t)
    hc = t["hucreler"]
    out: list[dict] = []
    bolum = ""
    gorulen: set[int] = set()
    for r, row in enumerate(g):
        bolumler = [hc[i]["metin"] for i in dict.fromkeys(row) if hc[i]["bolum_satiri"]]
        if bolumler:
            bolum = bolumler[0]
            continue
        for c, i in enumerate(row):
            h = hc[i]
            if i in gorulen or h["sutun_basligi"] or h["satir_basligi"]:
                continue
            gorulen.add(i)
            hd = hucre_degeri(h["metin"])
            if hd is None:
                continue
            sutun_yolu = _tekil(
                hc[g[rr][c]]["metin"] for rr in range(len(g)) if hc[g[rr][c]]["sutun_basligi"]
            )
            sol = [hc[j] for j in dict.fromkeys(row[:c])]
            basliklar = [x["metin"] for x in sol if x["satir_basligi"]]
            if not basliklar:  # motor ve sezgi satır başlığı vermediyse soldaki sayısal olmayan hücreler
                basliklar = [
                    x["metin"] for x in sol if x["metin"].strip() and hucre_degeri(x["metin"]) is None
                ]
            satir_yolu = _tekil(([bolum] if bolum else []) + basliklar)
            if hd.yil:  # yıl bir nicelik değildir; başlıktaki birimi almaz
                birim, carpan, kaynak = None, 1.0, None
            else:
                # bölüm adı birim kaynağı değildir (inceleme bulgu 3); yalnız bu satırın başlıkları
                birim, carpan, kaynak = _birim(hd.birim, sutun_yolu, _tekil(basliklar), t["birim"])
            out.append(
                {
                    "olgu_id": f"{t['tablo_id']}-r{r:02d}c{c:02d}",
                    "rapor_id": t["rapor_id"],
                    "tablo_id": t["tablo_id"],
                    "satir": r,
                    "sutun": c,
                    "sayfa": h["sayfa"],
                    "bbox": h["bbox"],
                    "deger": None if hd.eksik else hd.deger * carpan,
                    "birim": birim,
                    "carpan": carpan,
                    "birim_kaynagi": kaynak,
                    "ham": h["metin"],
                    "eksik": hd.eksik,
                    "dipnot": list(hd.dipnot),
                    "yil": hd.yil,
                    "satir_yolu": satir_yolu,
                    "sutun_yolu": sutun_yolu,
                    "donem": _donem(sutun_yolu) or _donem(satir_yolu),
                    "sema_surumu": OLGU_SURUMU,
                }
            )
    return out


def _tekil(metinler: Iterable[str]) -> list[str]:
    out: list[str] = []
    for m in metinler:
        m = " ".join(m.split())
        if m and (not out or out[-1] != m):
            out.append(m)
    return out


def _donem(yol: list[str]) -> str | None:
    """En derin yol öğesindeki tek yıl. Bir öğede birden çok farklı yıl varsa dönem belirsizdir (None)."""
    for parca in reversed(yol):
        yillar = set(YIL.findall(parca))
        if len(yillar) > 1:
            return None
        if yillar:
            return yillar.pop()
    return None


def _guvenilir_baslik(parca: str) -> bool:
    """Başlık öğesinde veri sayısı yok mu? Yıl, tarih ("31.12.2024") ve kimlik sayıları ("Kapsam 1",
    "Kategori 7", "TSRS 2") veri sayılmaz (inceleme bulgu 2)."""
    temiz = TARIH_RE.sub(lambda m: m.group(1), IDENTIFIER.sub(" ", parca))
    return not any(not q.is_year for q in extract_numbers(temiz))


def _birim(hucre_birimi, sutun_yolu, satir_yolu, tablo_birimi) -> tuple[str | None, float, str | None]:
    """Öncelik: hücre > sütun başlığı (en derin) > satır başlığı > tablo başlığı.

    Birden çok farklı birim anan ya da veri sayısı içeren (güvenilmez) bir başlık öğesine gelinince birim
    belirsizdir ve aranmaz: daha sığ kaynağa (ör. tablo başlığı) düşmek yanlış birim verir (bulgu 2).
    """
    if hucre_birimi:
        return hucre_birimi, 1.0, "hucre"
    for kaynak, yol in (("sutun_basligi", sutun_yolu), ("satir_basligi", satir_yolu)):
        for parca in reversed(yol):
            bulunan = set(birimler_bul(parca))
            if not _guvenilir_baslik(parca) or len(bulunan) > 1:
                return None, 1.0, None
            if bulunan:
                b = bulunan.pop()
                return b[0], b[1], kaynak
    if tablo_birimi:
        return tablo_birimi["taban"], tablo_birimi["carpan"], "tablo_basligi"
    return None, 1.0, None


def olgu_metni(o: dict, t: dict) -> str:
    """Retrieval ve taslak bağlamı için olgunun doğrusal metni (sayı, kaynaktaki yazımıyla)."""
    parcalar = [t["baslik"], *o["satir_yolu"], " / ".join(o["sutun_yolu"])]
    return " · ".join(p for p in parcalar if p) + f": {o['ham']}"


# ---------- PyMuPDF: çizgili tablolar ----------


def _kumele(degerler: Iterable[float], tol: float = KUMELEME_TOL) -> list[float]:
    """Yakın kenarları tek ızgara çizgisinde toplar; uzaklık grubun ilk değerine göre (zincirlenmez)."""
    gruplar: list[list[float]] = []
    for v in sorted(degerler):
        if gruplar and v - gruplar[-1][0] <= tol:
            gruplar[-1].append(v)
        else:
            gruplar.append([v])
    return [sum(g) / len(g) for g in gruplar]


def _en_yakin(cizgiler: list[float], v: float) -> int:
    return min(range(len(cizgiler)), key=lambda i: abs(cizgiler[i] - v))


def _hucre_metni(page, bbox) -> str:
    import pymupdf

    return re.sub(r"\s+", " ", page.get_text("text", clip=pymupdf.Rect(bbox))).strip()


def _cizgi_izgarasi(page, table, sayfa: int) -> tuple[list[dict], int, int, int]:
    """Hücre dikdörtgenlerinden ızgara: kenarlar kümelenir, her hücre kapladığı aralığa yerleşir."""
    kutular = list(dict.fromkeys(tuple(c) for c in table.cells if c))
    xs = _kumele([k[0] for k in kutular] + [k[2] for k in kutular])
    ys = _kumele([k[1] for k in kutular] + [k[3] for k in kutular])
    n, m = len(ys) - 1, len(xs) - 1
    dolu: set[tuple[int, int]] = set()
    hucreler = []
    atilan = 0
    for k in sorted(kutular, key=lambda k: (k[1], k[0])):
        r0, r1 = _en_yakin(ys, k[1]), _en_yakin(ys, k[3])
        c0, c1 = _en_yakin(xs, k[0]), _en_yakin(xs, k[2])
        konumlar = {(r, c) for r in range(r0, r1) for c in range(c0, c1)}
        if not konumlar or konumlar & dolu:
            atilan += 1  # çok ince ya da çakışan hücre: uyarı `cizgi_hucre_atildi`
            continue
        dolu |= konumlar
        h = bos_hucre(r0, c0, sayfa, [round(v, 2) for v in k])
        h.update(satir_kapsam=r1 - r0, sutun_kapsam=c1 - c0, metin=_hucre_metni(page, k))
        hucreler.append(h)
    for r in range(n):
        for c in range(m):
            if (r, c) not in dolu:
                hucreler.append(bos_hucre(r, c, sayfa, [xs[c], ys[r], xs[c + 1], ys[r + 1]]))
    return hucreler, n, m, atilan


def _bloklar(page) -> list[dict]:
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        satirlar = [
            {"bbox": ln["bbox"], "metin": "".join(s["text"] for s in ln["spans"]).strip(),
             "boyut": max((s["size"] for s in ln["spans"]), default=0.0)}
            for ln in b["lines"]
        ]  # fmt: skip
        satirlar = [s for s in satirlar if s["metin"]]
        if satirlar:
            out.append(
                {"bbox": b["bbox"], "metin": join_lines([s["metin"] for s in satirlar]), "satirlar": satirlar}
            )
    return out


def _icinde(bbox, alan, pay: float = 1.0) -> bool:
    cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    return alan[0] - pay <= cx <= alan[2] + pay and alan[1] - pay <= cy <= alan[3] + pay


def _baslik_ve_dipnot(bloklar, alan) -> tuple[str, list[str], set[int]]:
    ust = [
        (i, b)
        for i, b in enumerate(bloklar)
        if b["bbox"][3] <= alan[1] + 1
        and alan[1] - b["bbox"][3] < BASLIK_ARALIGI
        and 3 <= len(b["metin"]) < 120
        and re.search(r"[^\W\d_]", b["metin"])  # yalnız rakam (sayfa numarası) başlık değildir
    ]
    kullanilan: set[int] = set()
    baslik = ""
    if ust:
        i, b = max(ust, key=lambda x: (bool(BASLIK_RE.match(x[1]["metin"])), x[1]["bbox"][3]))
        baslik, _ = b["metin"], kullanilan.add(i)
    dipnotlar = []
    for i, b in sorted(enumerate(bloklar), key=lambda x: x[1]["bbox"][1]):
        if (
            b["bbox"][1] >= alan[3] - 1
            and b["bbox"][1] - alan[3] < DIPNOT_ARALIGI
            and DIPNOT_RE.match(b["metin"])
        ):
            dipnotlar.append(b["metin"])
            kullanilan.add(i)
    return baslik, dipnotlar, kullanilan


# ---------- PyMuPDF: kenarlıksız tablolar (sezgisel) ----------


def _bant(satirlar: list[dict], bas: int, tol: float) -> int:
    """`bas` satırından başlayan bandın bittiği indeks: dikey olarak çakışan (tol içinde) satırlar zinciri."""
    y1 = satirlar[bas]["bbox"][3]
    j = bas + 1
    while j < len(satirlar) and satirlar[j]["bbox"][1] <= y1 + tol:
        y1 = max(y1, satirlar[j]["bbox"][3])
        j += 1
    return j


def _kesimler(satirlar: list[dict]) -> list[list[float]]:
    """Satırların yatay izdüşümündeki dolu aralıklar (soldan sağa)."""
    out: list[list[float]] = []
    for s in sorted(satirlar, key=lambda s: s["bbox"][0]):
        if out and s["bbox"][0] <= out[-1][1] + 3:
            out[-1][1] = max(out[-1][1], s["bbox"][2])
        else:
            out.append([s["bbox"][0], s["bbox"][2]])
    return out


def _kenarliksiz(bloklar: list[dict], baslik_blok: dict, alt_sinir: float, sayfa: int):
    satirlar = sorted(
        (s for b in bloklar for s in b["satirlar"] if s["bbox"][1] >= baslik_blok["bbox"][3] - 1 and s["bbox"][3] <= alt_sinir),
        key=lambda s: (s["bbox"][1], s["bbox"][0]),
    )  # fmt: skip
    if len(satirlar) < 4:
        return None
    yukseklik = sorted(s["bbox"][3] - s["bbox"][1] for s in satirlar)[len(satirlar) // 2]
    tol = 0.35 * yukseklik
    # Sütunlar: kabul edilen bütün bantların yatay izdüşümündeki dolu aralıklar (boşluk vadileri arası).
    # Yeni bant var olan iki sütunu birleştirirse (paragraf satırı, sütun aşan metin) tablo orada biter.
    # Sağa hizalı sayılar ve boş sol üst başlık hücresi böylece doğru sütuna düşer (inceleme bulgu 5).
    j = _bant(satirlar, 0, tol)
    bantlar = [satirlar[:j]]
    tum = list(satirlar[:j])
    kesim = _kesimler(tum)
    son_y = max(s["bbox"][3] for s in tum)
    while j < len(satirlar):
        k = _bant(satirlar, j, tol)
        bant = satirlar[j:k]
        if bant[0]["bbox"][1] - son_y > 2.5 * yukseklik:
            break
        if any(s["boyut"] > 1.15 * satirlar[0]["boyut"] + 0.5 for s in bant):
            break  # bölüm başlığı
        yeni = _kesimler(tum + bant)
        if any(sum(e[0] >= y[0] - 0.01 and e[1] <= y[1] + 0.01 for e in kesim) >= 2 for y in yeni):
            break
        bantlar.append(bant)
        tum += bant
        kesim = yeni
        son_y = max(s["bbox"][3] for s in bant)
        j = k

    def sutun(s) -> int | None:
        for c, (x0, x1) in enumerate(kesim):
            if s["bbox"][0] >= x0 - 0.5 and s["bbox"][2] <= x1 + 0.5:
                return c
        return None

    if len(kesim) < 2 or len(bantlar) < 2 or not any(len({sutun(s) for s in b}) >= 2 for b in bantlar[1:]):
        return None
    hucreler = []
    for r, bant in enumerate(bantlar):
        y0, y1 = min(s["bbox"][1] for s in bant), max(s["bbox"][3] for s in bant)
        for c in range(len(kesim)):
            icerik = sorted((s for s in bant if sutun(s) == c), key=lambda s: (s["bbox"][1], s["bbox"][0]))
            h = bos_hucre(r, c, sayfa)
            if icerik:
                bb = [min(s["bbox"][0] for s in icerik), min(s["bbox"][1] for s in icerik),
                      max(s["bbox"][2] for s in icerik), max(s["bbox"][3] for s in icerik)]  # fmt: skip
                h.update(metin=join_lines([s["metin"] for s in icerik]), bbox=[round(v, 2) for v in bb])
            else:
                h["bbox"] = [round(kesim[c][0], 2), round(y0, 2), round(kesim[c][1], 2), round(y1, 2)]
            hucreler.append(h)
    alan = [min(k[0] for k in kesim), bantlar[0][0]["bbox"][1], max(k[1] for k in kesim), son_y]
    return hucreler, len(bantlar), len(kesim), alan


# ---------- belge düzeyi ----------


MOTORLAR_VARSAYILAN = ("pymupdf", "pymupdf-bosluk")


def sayfa_tablolari(
    page, sayfa: int, rapor_id: str, motorlar: tuple[str, ...] = MOTORLAR_VARSAYILAN
) -> list[dict]:
    """Bir sayfanın tabloları: önce `find_tables`, sonra bulunamayan "Tablo N" başlıkları için sezgisel yöntem."""
    bloklar = _bloklar(page)
    yukseklik = page.rect.height
    adaylar: list[tuple[list[float], dict]] = []
    alanlar: list[list[float]] = []
    kullanilan: set[int] = set()
    for t in page.find_tables().tables if "pymupdf" in motorlar else []:
        hucreler, n, m, atilan = _cizgi_izgarasi(page, t, sayfa)
        if n < 1 or m < 1:
            continue
        alan = list(t.bbox)
        baslik, dipnot, kul = _baslik_ve_dipnot(bloklar, alan)
        kullanilan |= kul
        alanlar.append(alan)
        adaylar.append((alan, {"hucreler": hucreler, "n": n, "m": m, "motor": "pymupdf",
                               "baslik": baslik, "dipnot": dipnot,
                               "uyari": ["cizgi_hucre_atildi"] if atilan else []}))  # fmt: skip
    basliklar = [
        (i, b)
        for i, b in enumerate(bloklar)
        if "pymupdf-bosluk" in motorlar
        and BASLIK_RE.match(b["metin"])
        and i not in kullanilan
        and not any(_icinde(b["bbox"], a) for a in alanlar)
    ]
    for k, (_, b) in enumerate(basliklar):
        sonraki = [bb["bbox"][1] for _, bb in basliklar[k + 1 :]] + [
            a[1] for a in alanlar if a[1] > b["bbox"][3]
        ]
        alt = min([yukseklik * (1 - BAND), *sonraki])
        disarida = [x for x in bloklar if not any(_icinde(x["bbox"], a) for a in alanlar) and x is not b]
        sonuc = _kenarliksiz(disarida, b, alt, sayfa)
        if sonuc is None:
            continue
        hucreler, n, m, alan = sonuc
        _, dipnot, _ = _baslik_ve_dipnot(disarida, alan)
        adaylar.append((alan, {"hucreler": hucreler, "n": n, "m": m, "motor": "pymupdf-bosluk",
                               "baslik": b["metin"], "dipnot": dipnot, "uyari": ["kenarliksiz_sezgisel"]}))  # fmt: skip
    out = []
    for sira, (alan, a) in enumerate(sorted(adaylar, key=lambda x: (x[0][1], x[0][0])), start=1):
        t = tablo_kaydi(rapor_id, sayfa, sira, a["hucreler"], a["n"], a["m"], a["motor"], alan,
                        baslik=a["baslik"], dipnotlar=a["dipnot"], uyarilar=a["uyari"])  # fmt: skip
        out.append(basliklari_belirle(t))
    return out


def sayfalari_birlestir(tablolar: list[dict], sayfa_yukseklikleri: dict[int, float]) -> list[dict]:
    """Sayfa sonunda bölünen tabloyu sonraki sayfadaki devamıyla birleştirir (R-TAB-03, KL-02).

    Koşullar: devam, sonraki sayfanın ilk tablosu ve sayfanın üst kısmında; önceki parça sayfasının son
    tablosu ve alt kısmında; sütun sayıları ve (koordinat varsa) sütun sol kenarları aynı; devamın
    başlığı yok ya da aynı. Devamın ilk satırları önceki parçanın başlık satırlarının tekrarıysa atılır.
    """
    sirali = sorted(tablolar, key=lambda t: (t["sayfalar"][0], t["parcalar"][0]["bbox"][1]))
    out: list[dict] = []
    for t in sirali:
        onceki = out[-1] if out else None
        birlesik = (
            _ekle(onceki, t)
            if onceki is not None and _devam_mi(onceki, t, sirali, sayfa_yukseklikleri)
            else None
        )
        if birlesik is not None:
            out[-1] = birlesik
        else:
            out.append(t)
    return out


def _devam_mi(a: dict, b: dict, hepsi: list[dict], h: dict[int, float]) -> bool:
    pa, pb = a["sayfalar"][-1], b["sayfalar"][0]
    if pb != pa + 1 or a["sutun_sayisi"] != b["sutun_sayisi"]:
        return False
    if b["baslik"] and b["baslik"] != a["baslik"]:
        return False
    # a'nın son parçası pa sayfasındaki en alt tablo parçası, b'nin ilk parçası pb'deki en üst parça olmalı.
    # Parçalar üzerinden bakılır: birleştirme kopya ürettiği için nesne kimliği karşılaştırılamaz.
    alt_pa = max(p["bbox"][3] for t in hepsi for p in t["parcalar"] if p["sayfa"] == pa)
    ust_pb = min(p["bbox"][1] for t in hepsi for p in t["parcalar"] if p["sayfa"] == pb)
    if a["parcalar"][-1]["bbox"][3] < alt_pa - 0.5 or b["parcalar"][0]["bbox"][1] > ust_pb + 0.5:
        return False
    if a["parcalar"][-1]["bbox"][3] < BIRLESTIRME_ALT * h.get(pa, 842.0):
        return False
    if b["parcalar"][0]["bbox"][1] > BIRLESTIRME_UST * h.get(pb, 842.0):
        return False
    sol_a, sol_b = _sol_kenarlar(a, a["sayfalar"][-1]), _sol_kenarlar(b, pb)
    return not (sol_a and sol_b and max(abs(x - y) for x, y in zip(sol_a, sol_b, strict=True)) > SUTUN_TOL)


def _sol_kenarlar(t: dict, sayfa: int) -> list[float] | None:
    kenar: dict[int, float] = {}
    for h in t["hucreler"]:
        if h["sayfa"] == sayfa and h["bbox"] and h["sutun_kapsam"] == 1:
            kenar[h["sutun"]] = min(kenar.get(h["sutun"], h["bbox"][0]), h["bbox"][0])
    return [kenar[c] for c in range(t["sutun_sayisi"])] if len(kenar) == t["sutun_sayisi"] else None


def _satir_metinleri(t: dict, r: int) -> list[str]:
    g = izgara(t)
    return [" ".join(t["hucreler"][i]["metin"].split()) for i in g[r]]


def _ekle(a: dict, b: dict) -> dict | None:
    """`a`'ya devamı `b`'yi ekler (kopya döner). Tekrarlanan başlık satırları atılır; `b`'den gelen bütün
    hücreler gövdedir (devamın kendi başlık sezgisi geçersiz). Atılan başlık satırları ile gövde arasında
    kalan (sınırı aşan) birleşik hücre varsa birleştirme yapılmaz → None (inceleme bulgu 4)."""
    baslik_sayisi = 0
    while (
        baslik_sayisi < min(a["satir_sayisi"], b["satir_sayisi"] - 1)
        and _satir_metinleri(a, baslik_sayisi) == _satir_metinleri(b, baslik_sayisi)
        and all(a["hucreler"][i]["sutun_basligi"] for i in izgara(a)[baslik_sayisi])
    ):
        baslik_sayisi += 1
    if any(h["satir"] < baslik_sayisi < h["satir"] + h["satir_kapsam"] for h in b["hucreler"]):
        return None
    kaydir = a["satir_sayisi"] - baslik_sayisi
    yeni = a | {"hucreler": [dict(h) for h in a["hucreler"]]}
    for h in b["hucreler"]:
        if h["satir"] >= baslik_sayisi:
            yeni["hucreler"].append(h | {"satir": h["satir"] + kaydir, "sutun_basligi": False})
    yeni["satir_sayisi"] = a["satir_sayisi"] + b["satir_sayisi"] - baslik_sayisi
    yeni["sayfalar"] = sorted(set(a["sayfalar"]) | set(b["sayfalar"]))
    yeni["parcalar"] = a["parcalar"] + b["parcalar"]
    yeni["dipnotlar"] = a["dipnotlar"] + [d for d in b["dipnotlar"] if d not in a["dipnotlar"]]
    yeni["uyarilar"] = list(dict.fromkeys([*a["uyarilar"], *b["uyarilar"], "sayfalar_arasi_birlestirildi"]))
    yeni["hucreler"].sort(key=lambda h: (h["satir"], h["sutun"]))
    return yeni


def cikar(pdf_path: Path, rapor_id: str, motorlar: tuple[str, ...] = MOTORLAR_VARSAYILAN) -> list[dict]:
    """PyMuPDF motorlarıyla bütün belgenin tabloları (sayfalar arası birleştirilmiş)."""
    import pymupdf

    doc = pymupdf.open(pdf_path)
    tablolar: list[dict] = []
    yukseklik: dict[int, float] = {}
    for sayfa, page in enumerate(doc, start=1):
        yukseklik[sayfa] = page.rect.height
        tablolar += sayfa_tablolari(page, sayfa, rapor_id, motorlar)
    return [denetle(t, len(doc)) for t in sayfalari_birlestir(tablolar, yukseklik)]


# ---------- Docling uyarlayıcısı ----------


def docling_tablosu(
    veri: dict,
    rapor_id: str,
    *,
    sayfa: int,
    sira: int,
    bbox: list[float],
    baslik: str,
    sayfa_yuksekligi: float,
    dipnotlar: list[str] | None = None,
) -> dict | None:
    """docling-core `TableData.model_dump()` → tablo kaydı. Hücre kutusu alt-sol orijinliyse çevrilir."""
    n, m = veri["num_rows"], veri["num_cols"]
    if n < 1 or m < 1:
        return None  # Docling bazen 0×0 tablo veriyor (Derimod 2025 s. 27); kayıt açılmaz
    hucreler: list[dict] = []
    dolu: set[tuple[int, int]] = set()
    uyarilar: list[str] = []
    for c in veri["table_cells"]:
        r0, r1 = c["start_row_offset_idx"], c["end_row_offset_idx"]
        c0, c1 = c["start_col_offset_idx"], c["end_col_offset_idx"]
        konumlar = {(r, k) for r in range(r0, r1) for k in range(c0, c1)}
        if not konumlar or konumlar & dolu or r1 > n or c1 > m:
            uyarilar.append("docling_gecersiz_hucre_atildi")
            continue
        dolu |= konumlar
        h = bos_hucre(r0, c0, sayfa, _docling_kutu(c.get("bbox"), sayfa_yuksekligi))
        h.update(
            satir_kapsam=r1 - r0,
            sutun_kapsam=c1 - c0,
            metin=" ".join(str(c.get("text", "")).split()),
            sutun_basligi=bool(c.get("column_header")),
            satir_basligi=bool(c.get("row_header")),
            bolum_satiri=bool(c.get("row_section")),
        )
        hucreler.append(h)
    hucreler = _bosluklari_doldur(hucreler, n, m, sayfa)
    t = tablo_kaydi(rapor_id, sayfa, sira, hucreler, n, m, "docling", bbox, baslik=baslik,
                    dipnotlar=dipnotlar, uyarilar=sorted(set(uyarilar)))  # fmt: skip
    return basliklari_belirle(t)


def _docling_kutu(b: dict | None, yukseklik: float) -> list[float] | None:
    if not b:
        return None
    if str(b.get("coord_origin", "TOPLEFT")).upper().endswith("BOTTOMLEFT"):
        return [b["l"], yukseklik - b["t"], b["r"], yukseklik - b["b"]]
    return [b["l"], b["t"], b["r"], b["b"]]
