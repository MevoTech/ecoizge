#!/usr/bin/env python3
"""İnsanın PDF'ten elle yazdığı tablo CSV'sini altın tablo ve olgu kaydına çevirir (table-eval skill'i, S28.T6).

    python .claude/skills/table-eval/scripts/altin_donustur.py tablo.csv --rapor-id klimasan-2025 --sayfa 51 \
        --sira 1 --baslik-satiri 2 [--baslik "Tablo 6. Sera gazı emisyonları"] --out-dir data/gold/tables

CSV kuralları (Excel'de `;` ayraçlı, UTF-8):
- Her satır tablonun bir satırı, her hücre bir sütun; metin PDF'te göründüğü gibi (sayı biçimi değiştirilmez).
- Birleşik hücre: soldakiyle birleşikse `<`, üsttekiyle birleşikse `^` yazılır.
- `--baslik-satiri`: üstteki sütun başlığı satırı sayısı (insan belirler; sezgi kullanılmaz).

Çıktı: `<out-dir>/<rapor-id>.tables.jsonl` ve `.facts.jsonl` (aynı `tablo_id` varsa yerine yazılır). Kutu
koordinatı yoktur ([0, 0, 0, 0]); ölçümde eşleme içerikle yapılır (`tools/tablo_olcum.py`). `data/gold/**`
korumalıdır: bu komutu kullanıcı koşar (U-16); olguların birim ve dönemini de kullanıcı kontrol eder.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

_KOK = Path(__file__).resolve().parents[4]
for _yol in (_KOK / "pipelines", _KOK / "tools", _KOK / "services" / "report-service"):
    if str(_yol) not in sys.path:
        sys.path.insert(0, str(_yol))

import tables as tb  # noqa: E402
import tablo_kurallari as tk  # noqa: E402


def _utf8_cikti() -> None:
    """Windows'ta yönlendirilen çıktı cp1254 olabilir; '→', '₂' yazarken çökmesin (inceleme bulgu 15)."""
    for akim in (sys.stdout, sys.stderr):
        if hasattr(akim, "reconfigure"):
            akim.reconfigure(encoding="utf-8", errors="replace")


class CSVHatasi(ValueError):
    pass


def izgaraya_cevir(satirlar: list[list[str]], sayfa: int) -> tuple[list[dict], int, int]:
    """`<` / `^` işaretli metin ızgarasından kapsamlı hücreler."""
    n = len(satirlar)
    m = max((len(s) for s in satirlar), default=0)
    if not n or not m:
        raise CSVHatasi("boş tablo")
    g = [[(s[c].strip() if c < len(s) else "") for c in range(m)] for s in satirlar]
    sahip: list[list[tuple[int, int]]] = [[(r, c) for c in range(m)] for r in range(n)]
    for r in range(n):
        for c in range(m):
            if g[r][c] == "<":
                if c == 0:
                    raise CSVHatasi(f"({r + 1},{c + 1}): '<' ilk sütunda olamaz")
                sahip[r][c] = sahip[r][c - 1]
            elif g[r][c] == "^":
                if r == 0:
                    raise CSVHatasi(f"({r + 1},{c + 1}): '^' ilk satırda olamaz")
                sahip[r][c] = sahip[r - 1][c]
    alanlar: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for r in range(n):
        for c in range(m):
            alanlar.setdefault(sahip[r][c], []).append((r, c))
    hucreler = []
    for (r0, c0), konumlar in alanlar.items():
        r1 = max(r for r, _ in konumlar) + 1
        c1 = max(c for _, c in konumlar) + 1
        if len(konumlar) != (r1 - r0) * (c1 - c0):
            raise CSVHatasi(f"({r0 + 1},{c0 + 1}) birleşik hücresi dikdörtgen değil")
        h = tb.bos_hucre(r0, c0, sayfa)
        h.update(satir_kapsam=r1 - r0, sutun_kapsam=c1 - c0, metin=g[r0][c0])
        hucreler.append(h)
    return hucreler, n, m


def csv_oku(yol: Path, ayrac: str = ";") -> list[list[str]]:
    """Türkçe Excel CSV'si: ayraç varsayılan `;` (Türkçe ondalık virgülüyle karışmasın, inceleme bulgu 11).

    "CSV UTF-8" seçeneği UTF-8 (BOM'lu) yazar; düz "CSV" seçeneği Windows-1254 yazar: UTF-8 çözülemezse
    cp1254 denenir ve uyarı verilir.
    """
    ham = yol.read_bytes()
    try:
        metin = ham.decode("utf-8-sig")
    except UnicodeDecodeError:
        metin = ham.decode("cp1254")
        print(f"UYARI: {yol.name} UTF-8 değil, Windows-1254 olarak okundu", file=sys.stderr)
    return [s for s in csv.reader(io.StringIO(metin), delimiter=ayrac) if any(x.strip() for x in s)]


def donustur(
    satirlar, rapor_id: str, sayfa: int, sira: int, baslik_satiri: int, baslik: str = ""
) -> tuple[dict, list[dict]]:
    hucreler, n, m = izgaraya_cevir(satirlar, sayfa)
    if not 0 <= baslik_satiri < n:
        raise CSVHatasi(f"--baslik-satiri 0…{n - 1} olmalı")
    for h in hucreler:
        h["sutun_basligi"] = h["satir"] < baslik_satiri
    t = tb.tablo_kaydi(rapor_id, sayfa, sira, hucreler, n, m, "insan", [0, 0, 0, 0], baslik=baslik,
                       uyarilar=["altin_insan"])  # fmt: skip
    if baslik_satiri:  # satır başlığı ve bölüm satırı sezgiyle; sütun başlığı insanın verdiği kalır
        tb.basliklari_belirle(t)
    hatalar = tk.tablo_hatalari(t)
    if hatalar:
        raise CSVHatasi("; ".join(hatalar))
    return t, tb.olgular(t)


def _yerine_yaz(yol: Path, yeni: list[dict], anahtar: str, tablo_id: str) -> None:
    eski = (
        [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]
        if yol.exists()
        else []
    )
    kalan = [k for k in eski if k.get(anahtar) != tablo_id]
    yol.parent.mkdir(parents=True, exist_ok=True)
    tmp = yol.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(k, ensure_ascii=False) + "\n" for k in kalan + yeni), encoding="utf-8")
    tmp.replace(yol)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--rapor-id", required=True)
    ap.add_argument("--sayfa", type=int, required=True)
    ap.add_argument("--sira", type=int, default=1)
    ap.add_argument("--baslik-satiri", type=int, required=True)
    ap.add_argument("--baslik", default="")
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--ayrac", default=";", help="CSV ayracı (Türkçe Excel: ;)")
    a = ap.parse_args(argv)
    _utf8_cikti()
    try:
        t, olgular = donustur(csv_oku(a.csv, a.ayrac), a.rapor_id, a.sayfa, a.sira, a.baslik_satiri, a.baslik)
    except CSVHatasi as e:
        print(f"HATA: {e}", file=sys.stderr)
        return 1
    _yerine_yaz(a.out_dir / f"{a.rapor_id}.tables.jsonl", [t], "tablo_id", t["tablo_id"])
    _yerine_yaz(a.out_dir / f"{a.rapor_id}.facts.jsonl", olgular, "tablo_id", t["tablo_id"])
    print(f"{t['tablo_id']}: {t['satir_sayisi']}×{t['sutun_sayisi']}, {len(olgular)} olgu → {a.out_dir}")
    for o in olgular:
        print(
            f"  {' > '.join(o['satir_yolu'])} | {' > '.join(o['sutun_yolu'])}: {o['ham']} → birim {o['birim']}, dönem {o['donem']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
