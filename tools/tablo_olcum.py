#!/usr/bin/env python3
"""Tablo çıkarımı ölçümü: tespit, yapı (GriTS) ve olgu düzeyi P/R/F1 (R-TAB-05, S28; ADR-014).

    python tools/tablo_olcum.py --gercek data/gold/tables/<rapor>.tables.jsonl --tahmin <out>/tables.jsonl \
        [--gercek-olgu <gold>.facts.jsonl --tahmin-olgu <out>/facts.jsonl] --run-id <id> [--out rapor.json]

Ölçütler:
1. **Tespit:** aynı sayfadaki tablolar IoU ≥ 0,5 ile (altın kümede kutu yoksa GriTS_Con ≥ 0,5 ile) açgözlü
   eşlenir → P, R, F1.
2. **GriTS** (Smock, Pesala, Abraham 2023, "GriTS: Grid table similarity metric for table structure
   recognition", ICDAR; arXiv:2203.12555): iki ızgaranın en benzer alt yapıları (2D-MSS) "factored" çok
   terimli sezgisel ile hizalanır; F = 2·Σbenzerlik / (|A| + |B|). İki çeşit:
   - `GriTS_Con`: konum başına hücre metni; benzerlik difflib eşleşen blok oranı (başvuru koduyla aynı);
   - `GriTS_Top`: konum başına göreli kapsam kutusu [θ−j, p−i, θ−j+β, p−i+α]; benzerlik IoU.
   Bu dosyadaki uygulama makaledeki tanımdan bağımsız yazıldı; Microsoft table-transformer
   `src/grits.py` (MIT) ile rastgele ızgaralarda karşılaştırıldı (PROGRESS §4, S28).
3. **Olgu:** eşlenen tablo çiftleri içinde (değer, birim, dönem, son satır başlığı) anahtarıyla çoklu küme
   eşleşmesi → P, R, F1; ayrıca yalnız değer. Taslaktaki
   sayıyı doğrulamak için gereken düzey budur (ADR-004): yapı doğru ama olgu yanlışsa doğrulama yanılır.

Ölçüm sonucu yalnızca bir `run_id` ile raporlanır (AGENTS §3). Yalnızca standart kütüphane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tablo_kurallari import izgara  # noqa: E402

IOU_ESIK = 0.5


# ---------- GriTS ----------


def _hizala_1d(a: list, b: list, odul) -> float:
    """İki dizinin en yüksek toplam ödüllü hizalaması (boşluk cezasız; LCS genellemesi)."""
    onceki = [0.0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        simdi = [0.0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            simdi[j] = max(onceki[j - 1] + odul(a[i - 1], b[j - 1]), onceki[j], simdi[j - 1])
        onceki = simdi
    return onceki[-1]


def _hizala_dis(n_a: int, n_b: int, satir_odulu) -> list[tuple[int, int]]:
    """Dış dizileri (satırları) hizalar; iç ödül, iki satırın 1B hizalama puanıdır. Eşlenen indeks çiftleri."""
    puan = [[0.0] * (n_b + 1) for _ in range(n_a + 1)]
    yon = [[0] * (n_b + 1) for _ in range(n_a + 1)]  # 0 çapraz, 1 yukarı, 2 sol
    for i in range(1, n_a + 1):
        yon[i][0] = 1
    for j in range(1, n_b + 1):
        yon[0][j] = 2
    for i in range(1, n_a + 1):
        for j in range(1, n_b + 1):
            capraz = puan[i - 1][j - 1] + satir_odulu(i - 1, j - 1)
            yukari, sol = puan[i - 1][j], puan[i][j - 1]
            en = max(capraz, yukari, sol)
            puan[i][j] = en
            yon[i][j] = 0 if capraz == en else (1 if yukari == en else 2)
    ciftler = []
    i, j = n_a, n_b
    while i > 0 or j > 0:
        if yon[i][j] == 0:
            i, j = i - 1, j - 1
            ciftler.append((i, j))
        elif yon[i][j] == 1:
            i -= 1
        else:
            j -= 1
    return ciftler[::-1]


def factored_2dmss(a: list[list], b: list[list], benzerlik) -> tuple[float, float, float]:
    """(F, P, R). `a` gerçek, `b` tahmin ızgarası; satırlar ve sütunlar ayrı ayrı hizalanır.

    Ödüller konum dörtlüsü yerine hücre değeri çiftine göre önbelleğe alınır: bellek O(farklı değer çifti),
    büyük tabloda boş hücreler tekrar ettiği için çok daha az (inceleme bulgu 9). Zaman O(n²m²) kalır.
    """
    if not a or not b or not a[0] or not b[0]:
        return 0.0, 0.0, 0.0
    na, ma, nb, mb = len(a), len(a[0]), len(b), len(b[0])

    def kalici(v):
        return tuple(v) if isinstance(v, list) else v

    A = [[kalici(v) for v in row] for row in a]
    B = [[kalici(v) for v in row] for row in b]
    od = lru_cache(maxsize=None)(benzerlik)
    satirlar = _hizala_dis(
        na, nb, lambda i, k: _hizala_1d(range(ma), range(mb), lambda j, m: od(A[i][j], B[k][m]))
    )
    sutunlar = _hizala_dis(
        ma, mb, lambda j, m: _hizala_1d(range(na), range(nb), lambda i, k: od(A[i][j], B[k][m]))
    )
    toplam = sum(od(A[i][j], B[k][m]) for i, k in satirlar for j, m in sutunlar)
    p, r = toplam / (nb * mb), toplam / (na * ma)
    return (2 * p * r / (p + r) if p + r else 0.0), p, r


def lcs_benzerligi(x: str, y: str) -> float:
    if not x and not y:
        return 1.0
    # Başvuru uygulamasıyla aynı: difflib eşleşen blokları (Ratcliff/Obershelp; tam LCS değil), autojunk açık
    lcs = sum(blok.size for blok in SequenceMatcher(None, x, y).get_matching_blocks())
    return 2 * lcs / (len(x) + len(y))


def iou(a, b) -> float:
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    kes = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    birlesim = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - kes
    return kes / birlesim if birlesim > 0 else 0.0


def _metin(s: str) -> str:
    return " ".join(s.split())


def metin_izgarasi(t: dict) -> list[list[str]]:
    return [[_metin(t["hucreler"][i]["metin"]) for i in row] for row in izgara(t)]


def kapsam_izgarasi(t: dict) -> list[list[list[int]]]:
    out = []
    for i, row in enumerate(izgara(t)):
        satir = []
        for j, k in enumerate(row):
            h = t["hucreler"][k]
            p, th, a, b = h["satir"], h["sutun"], h["satir_kapsam"], h["sutun_kapsam"]
            satir.append([th - j, p - i, th - j + b, p - i + a])
        out.append(satir)
    return out


def grits_con(gercek: dict, tahmin: dict) -> float:
    return factored_2dmss(metin_izgarasi(gercek), metin_izgarasi(tahmin), lcs_benzerligi)[0]


def grits_top(gercek: dict, tahmin: dict) -> float:
    return factored_2dmss(kapsam_izgarasi(gercek), kapsam_izgarasi(tahmin), iou)[0]


# ---------- tespit ----------


def _prf(tp: int, n_tahmin: int, n_gercek: int) -> dict:
    p = tp / n_tahmin if n_tahmin else 0.0
    r = tp / n_gercek if n_gercek else 0.0
    return {
        "p": p,
        "r": r,
        "f1": 2 * p * r / (p + r) if p + r else 0.0,
        "tp": tp,
        "tahmin": n_tahmin,
        "gercek": n_gercek,
    }


def _kutu_var(b) -> bool:
    return b[2] > b[0] and b[3] > b[1]


def eslestir(gercek: list[dict], tahmin: list[dict]) -> list[tuple[dict, dict]]:
    """Aynı (ilk) sayfadaki tablolar en yüksek benzerlikten başlayarak bire bir eşlenir; eşik 0,5.

    Benzerlik, iki tarafta da kutu varsa IoU; insan altın kümesinde kutu yoksa ([0, 0, 0, 0]) GriTS_Con.
    """
    adaylar = []
    for gi, g in enumerate(gercek):
        for ti, t in enumerate(tahmin):
            if g["parcalar"][0]["sayfa"] != t["parcalar"][0]["sayfa"]:
                continue
            bg, bt = g["parcalar"][0]["bbox"], t["parcalar"][0]["bbox"]
            adaylar.append((iou(bg, bt) if _kutu_var(bg) and _kutu_var(bt) else grits_con(g, t), gi, ti))
    kullanilan_g, kullanilan_t, out = set(), set(), []
    for deger, gi, ti in sorted(adaylar, reverse=True):
        if deger < IOU_ESIK or gi in kullanilan_g or ti in kullanilan_t:
            continue
        kullanilan_g.add(gi)
        kullanilan_t.add(ti)
        out.append((gercek[gi], tahmin[ti]))
    return out


# ---------- olgular ----------


def _norm(s: str) -> str:
    s = s.replace("I", "ı").replace("İ", "i").lower()
    return re.sub(r"[^\w%]+", " ", s).strip()


def olgu_anahtari(o: dict, tablo: str) -> tuple:
    """(eşlenmiş tablo, değer, birim, dönem, son satır başlığı). Hücre sayfası anahtara girmez: altın küme
    birleşik tabloyu tek sayfaya yazar (inceleme bulgu 10)."""
    deger = None if o["deger"] is None else float(f"{o['deger']:.9g}")
    son = _norm(o["satir_yolu"][-1]) if o["satir_yolu"] else ""
    return (tablo, deger, o["birim"], o["donem"], son)


def olgu_prf(gercek: list[dict], tahmin: list[dict], esleme: dict[str, str]) -> dict:
    """`esleme`: tahmin tablo_id → gerçek tablo_id (tespit eşlemesi). Eşlenmeyen tablonun olguları eşleşmez."""
    g = Counter(olgu_anahtari(o, o["tablo_id"]) for o in gercek)
    t = Counter(olgu_anahtari(o, esleme.get(o["tablo_id"], "tahmin:" + o["tablo_id"])) for o in tahmin)
    sonuc = _prf(sum((g & t).values()), sum(t.values()), sum(g.values()))
    deger_g = Counter(k[:2] for k in g.elements())
    deger_t = Counter(k[:2] for k in t.elements())
    sonuc["yalniz_deger"] = _prf(
        sum((deger_g & deger_t).values()), sum(deger_t.values()), sum(deger_g.values())
    )
    return sonuc


# ---------- rapor ----------


def olc(gercek: list[dict], tahmin: list[dict], gercek_olgu=None, tahmin_olgu=None) -> dict:
    ciftler = eslestir(gercek, tahmin)
    con = [grits_con(g, t) for g, t in ciftler]
    top = [grits_top(g, t) for g, t in ciftler]
    n = len(gercek)
    out = {
        "tespit": _prf(len(ciftler), len(tahmin), n),
        "grits_con_eslenen_ort": sum(con) / len(con) if con else None,
        "grits_top_eslenen_ort": sum(top) / len(top) if top else None,
        "grits_con_tum_gercek_ort": sum(con) / n if n else None,  # eşlenmeyen gerçek tablo 0 sayılır
        "grits_top_tum_gercek_ort": sum(top) / n if n else None,
        "tablo_bazinda": [
            {"gercek": g["tablo_id"], "tahmin": t["tablo_id"], "grits_con": c, "grits_top": p}
            for (g, t), c, p in zip(ciftler, con, top, strict=True)
        ],
    }
    if gercek_olgu is not None and tahmin_olgu is not None:
        out["olgu"] = olgu_prf(gercek_olgu, tahmin_olgu, {t["tablo_id"]: g["tablo_id"] for g, t in ciftler})
    return out


def _oku(yol: Path) -> list[dict]:
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def _ozet(yol: Path) -> str:
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Tablo çıkarımı ölçümü (tespit, GriTS, olgu)")
    ap.add_argument("--gercek", type=Path, required=True)
    ap.add_argument("--tahmin", type=Path, required=True)
    ap.add_argument("--gercek-olgu", type=Path)
    ap.add_argument("--tahmin-olgu", type=Path)
    ap.add_argument("--run-id", required=True, help="sonuç bir koşu kimliğine bağlanmadan raporlanmaz")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    if (a.gercek_olgu is None) != (a.tahmin_olgu is None):
        ap.error("--gercek-olgu ve --tahmin-olgu birlikte verilir")
    sonuc = olc(
        _oku(a.gercek),
        _oku(a.tahmin),
        _oku(a.gercek_olgu) if a.gercek_olgu else None,
        _oku(a.tahmin_olgu) if a.tahmin_olgu else None,
    )
    girdiler = {k: str(v) for k, v in vars(a).items() if isinstance(v, Path) and k != "out"}
    sonuc = {
        "run_id": a.run_id,
        "girdiler": girdiler,
        "sha256": {k: _ozet(Path(v)) for k, v in girdiler.items()},
    } | sonuc
    metin = json.dumps(sonuc, ensure_ascii=False, indent=1)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(metin + "\n", encoding="utf-8")
    print(metin)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
