"""Yapısal tablo, olgu ve şekil kayıtlarının şeması ve değişmezleri; TEK uygulama (R-TAB-01…04, ADR-014).

Çıkarıcı (`pipelines/tables.py`, `pipelines/figures.py`), doğrulayıcı (`tools/validate_data.py`) ve ölçüm
(`tools/tablo_olcum.py`) bu modülü kullanır; kurallar iki yerde ayrışmaz. Yalnızca standart kütüphane
(sayı denetimi `report_service.verify.numbers` ile yapılır, çağrıldığında yüklenir).

Tablo, hücre ızgarasıdır. Hücre alanları docling-core `TableCell` ile aynı anlamdadır
(start_row_offset_idx → satir, row_span → satir_kapsam, column_header → sutun_basligi …); bu sayede
motor değişse de kayıt biçimi değişmez.

Değişmez (ızgara bütünlüğü): her (satır, sütun) konumu tam olarak bir hücre tarafından kaplanır.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLO_SURUMU = "tablo-0.1"
OLGU_SURUMU = "olgu-0.1"
SEKIL_SURUMU = "sekil-0.1"
MOTORLAR = {"pymupdf", "pymupdf-bosluk", "docling", "insan"}
SEKIL_TURLERI = {"grafik", "sekil"}
VERI_DURUMLARI = {"vektor_etiket", "yalniz_etiket", "goruntu_veri_yok", "veri_yok"}

TABLO_ALANLARI = {
    "tablo_id", "rapor_id", "sayfalar", "parcalar", "baslik", "dipnotlar", "birim", "satir_sayisi",
    "sutun_sayisi", "hucreler", "motor", "paragraf_id", "uyarilar", "sema_surumu",
}  # fmt: skip
HUCRE_ALANLARI = {
    "satir", "sutun", "satir_kapsam", "sutun_kapsam", "metin", "sutun_basligi", "satir_basligi",
    "bolum_satiri", "sayfa", "bbox",
}  # fmt: skip
OLGU_ALANLARI = {
    "olgu_id", "rapor_id", "tablo_id", "satir", "sutun", "sayfa", "bbox", "deger", "birim", "carpan",
    "birim_kaynagi", "ham", "eksik", "dipnot", "yil", "satir_yolu", "sutun_yolu", "donem", "sema_surumu",
}  # fmt: skip
SEKIL_ALANLARI = {
    "sekil_id", "rapor_id", "sayfa", "bbox", "tur", "baslik", "metin", "veri", "veri_durumu",
    "eslesmeyen_etiket", "motor", "sinif", "uyarilar", "sema_surumu",
}  # fmt: skip
YIL = re.compile(r"(?<!\d)(19\d{2}|20\d{2}|2100)(?!\d)")


def _bbox_hatasi(b: object) -> str | None:
    if b is None:
        return None
    if not isinstance(b, list) or len(b) != 4 or not all(isinstance(v, (int, float)) for v in b):
        return "bbox [x0, y0, x1, y1] sayı listesi olmalı"
    if b[0] > b[2] or b[1] > b[3]:
        return "bbox x0 ≤ x1 ve y0 ≤ y1 olmalı"
    return None


def izgara(tablo: dict) -> list[list[int]]:
    """(satır, sütun) → hücre indeksi; kaplanmayan konum -1. Izgara geçersizse ValueError."""
    n, m = tablo["satir_sayisi"], tablo["sutun_sayisi"]
    g = [[-1] * m for _ in range(n)]
    for i, h in enumerate(tablo["hucreler"]):
        for r in range(h["satir"], h["satir"] + h["satir_kapsam"]):
            for c in range(h["sutun"], h["sutun"] + h["sutun_kapsam"]):
                if not (0 <= r < n and 0 <= c < m):
                    raise ValueError(f"hücre {i} ({h['satir']},{h['sutun']}) tablo dışına taşıyor")
                if g[r][c] != -1:
                    raise ValueError(f"({r},{c}) konumu iki hücrede: {g[r][c]} ve {i}")
                g[r][c] = i
    return g


def tablo_hatalari(t: object) -> list[str]:
    """Tablo kaydının şema ve ızgara hataları (Türkçe mesaj listesi; boşsa geçerli)."""
    if not isinstance(t, dict):
        return ["kayıt sözlük olmalı"]
    eksik = TABLO_ALANLARI - t.keys()
    fazla = t.keys() - TABLO_ALANLARI
    if eksik or fazla:
        return [f"alanlar: eksik {sorted(eksik)}, fazla {sorted(fazla)}"]
    h: list[str] = []
    if t["sema_surumu"] != TABLO_SURUMU:
        h.append(f"sema_surumu {TABLO_SURUMU} olmalı")
    if t["motor"] not in MOTORLAR:
        h.append(f"bilinmeyen motor: {t['motor']!r}")
    if (
        not isinstance(t["sayfalar"], list)
        or not t["sayfalar"]
        or t["sayfalar"] != sorted(set(t["sayfalar"]))
    ):
        h.append("sayfalar artan, tekrarsız ve boş olmayan liste olmalı")
    sayfalar = set(t["sayfalar"]) if isinstance(t["sayfalar"], list) else set()
    for p in t["parcalar"] if isinstance(t["parcalar"], list) else [None]:
        if not isinstance(p, dict) or p.get("sayfa") not in sayfalar or _bbox_hatasi(p.get("bbox")):
            h.append("parcalar: her parça {sayfa ∈ sayfalar, bbox} olmalı")
            break
    if not all(
        isinstance(t[k], int) and not isinstance(t[k], bool) and t[k] >= 1
        for k in ("satir_sayisi", "sutun_sayisi")
    ):
        return [*h, "satir_sayisi ve sutun_sayisi ≥ 1 tam sayı olmalı"]
    if t["birim"] is not None and (
        not isinstance(t["birim"], dict) or set(t["birim"]) != {"taban", "carpan", "kaynak"}
    ):
        h.append("birim null ya da {taban, carpan, kaynak} olmalı")
    for i, c in enumerate(t["hucreler"] if isinstance(t["hucreler"], list) else []):
        if not isinstance(c, dict) or set(c) != HUCRE_ALANLARI:
            h.append(f"hücre {i}: alanlar {sorted(HUCRE_ALANLARI)} olmalı")
            continue
        sayilar = ("satir", "sutun", "satir_kapsam", "sutun_kapsam")
        if not all(isinstance(c[k], int) and not isinstance(c[k], bool) for k in sayilar):
            h.append(f"hücre {i}: konum ve kapsam tam sayı olmalı")
        elif c["satir"] < 0 or c["sutun"] < 0 or c["satir_kapsam"] < 1 or c["sutun_kapsam"] < 1:
            h.append(f"hücre {i}: konum ≥ 0, kapsam ≥ 1 olmalı")
        if not all(isinstance(c[k], bool) for k in ("sutun_basligi", "satir_basligi", "bolum_satiri")):
            h.append(f"hücre {i}: başlık işaretleri true/false olmalı")
        if not isinstance(c["metin"], str):
            h.append(f"hücre {i}: metin dize olmalı")
        if c["sayfa"] not in sayfalar:
            h.append(f"hücre {i}: sayfa {c['sayfa']} tablonun sayfalarında yok")
        if (e := _bbox_hatasi(c["bbox"])) is not None:
            h.append(f"hücre {i}: {e}")
    if h or not isinstance(t["hucreler"], list):
        return h or ["hucreler liste olmalı"]
    try:
        g = izgara(t)
    except ValueError as e:
        return [f"ızgara: {e}"]
    bos = [(r, c) for r, row in enumerate(g) for c, v in enumerate(row) if v == -1]
    if bos:
        h.append(f"ızgara: kaplanmayan konumlar {bos[:5]}{' …' if len(bos) > 5 else ''}")
    return h


def _sayi_modulu():
    yol = str(ROOT / "services" / "report-service")
    if yol not in sys.path:
        sys.path.insert(0, yol)
    from report_service.verify import numbers

    return numbers


def olgu_hatalari(o: object, tablolar: dict[str, dict]) -> list[str]:
    """Olgu kaydı şeması ve kaynağıyla tutarlılık: hücre var, ham metin aynı, değer hücreden yeniden üretilir."""
    if not isinstance(o, dict):
        return ["kayıt sözlük olmalı"]
    if set(o) != OLGU_ALANLARI:
        return [
            f"alanlar: eksik {sorted(OLGU_ALANLARI - o.keys())}, fazla {sorted(o.keys() - OLGU_ALANLARI)}"
        ]
    t = tablolar.get(o["tablo_id"])
    if t is None:
        return [f"{o['olgu_id']}: tablo yok ({o['tablo_id']})"]
    try:
        hucre = t["hucreler"][izgara(t)[o["satir"]][o["sutun"]]]
    except (IndexError, ValueError, TypeError):
        return [f"{o['olgu_id']}: ({o['satir']},{o['sutun']}) tabloda yok"]
    h: list[str] = []
    if hucre["metin"] != o["ham"]:
        h.append(f"{o['olgu_id']}: ham metin hücre metniyle aynı değil")
    hd = _sayi_modulu().hucre_degeri(hucre["metin"])
    if hd is None:
        h.append(f"{o['olgu_id']}: hücre sayısal değil")
    elif hd.eksik != o["eksik"]:
        h.append(f"{o['olgu_id']}: eksik işareti hücreyle uyuşmuyor")
    elif not hd.eksik:
        beklenen = hd.deger * (o["carpan"] if hd.birim is None else 1.0)
        if abs(beklenen - o["deger"]) > 1e-9 * max(1.0, abs(beklenen)):
            h.append(f"{o['olgu_id']}: değer {o['deger']} ≠ hücreden {beklenen}")
    if o["sema_surumu"] != OLGU_SURUMU:
        h.append(f"{o['olgu_id']}: sema_surumu {OLGU_SURUMU} olmalı")
    if o["donem"] is not None and not YIL.fullmatch(str(o["donem"])):
        h.append(f"{o['olgu_id']}: donem yıl olmalı")
    return h


def sekil_hatalari(s: object) -> list[str]:
    if not isinstance(s, dict):
        return ["kayıt sözlük olmalı"]
    if set(s) != SEKIL_ALANLARI:
        return [
            f"alanlar: eksik {sorted(SEKIL_ALANLARI - s.keys())}, fazla {sorted(s.keys() - SEKIL_ALANLARI)}"
        ]
    h: list[str] = []
    if s["tur"] not in SEKIL_TURLERI:
        h.append(f"{s['sekil_id']}: tur {sorted(SEKIL_TURLERI)} içinden olmalı")
    if s["veri_durumu"] not in VERI_DURUMLARI:
        h.append(f"{s['sekil_id']}: veri_durumu {sorted(VERI_DURUMLARI)} içinden olmalı")
    if (e := _bbox_hatasi(s["bbox"])) is not None or s["bbox"] is None:
        h.append(f"{s['sekil_id']}: {e or 'bbox gerekli'}")
    if s["sema_surumu"] != SEKIL_SURUMU:
        h.append(f"{s['sekil_id']}: sema_surumu {SEKIL_SURUMU} olmalı")
    for v in s["veri"] if isinstance(s["veri"], list) else [None]:
        if not isinstance(v, dict) or set(v) != {"kategori", "seri", "deger", "ham", "bbox"}:
            h.append(f"{s['sekil_id']}: veri öğesi {{kategori, seri, deger, ham, bbox}} olmalı")
            break
    if s["veri"] and s["veri_durumu"] != "vektor_etiket":
        h.append(f"{s['sekil_id']}: veri yalnızca vektor_etiket durumunda dolu olur")
    return h
