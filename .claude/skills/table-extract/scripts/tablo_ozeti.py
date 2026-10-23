#!/usr/bin/env python3
"""Yapısal tablo çıkarımının otomatik QA özeti ve elle kontrol örneklemi (table-extract skill'i, S28).

    python .claude/skills/table-extract/scripts/tablo_ozeti.py <cikti_dizini> [--pdf rapor.pdf] [--ornek 10 --seed 43]

`<cikti_dizini>`, `pipelines/structure.py`'nin yazdığı `tables.jsonl` ve `facts.jsonl`'u içerir. `--pdf`
verilirse "Tablo N" başlığı geçen ama hiçbir tablonun kapsamadığı sayfalar listelenir (kaçırılan tablo adayı).
Çıktı Markdown'dır; evaluator `reports/experiments/` altına kaydeder.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

BASLIK_RE = re.compile(r"^\s*(Tablo|Table)\s*\d+", re.IGNORECASE)


def oku(yol: Path) -> list[dict]:
    return (
        [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]
        if yol.exists()
        else []
    )


def baslikli_sayfalar(pdf: Path) -> list[int]:
    import pymupdf

    return [
        i
        for i, p in enumerate(pymupdf.open(pdf), start=1)
        if any(BASLIK_RE.match(b[4]) for b in p.get_text("blocks"))
    ]


def _oran(a: int, b: int) -> str:
    return f"%{100 * a / b:.1f}".replace(".", ",") if b else "—"


def ozet(
    tablolar: list[dict],
    olgular: list[dict],
    baslikli: list[int] | None = None,
    ornek: int = 10,
    seed: int = 43,
) -> str:
    satir = ["# Tablo çıkarımı özeti", ""]
    satir.append(f"- Tablo: {len(tablolar)} · motor: {dict(Counter(t['motor'] for t in tablolar))}")
    satir.append(f"- Sayfalar arası birleştirilen: {sum(len(t['sayfalar']) > 1 for t in tablolar)}")
    satir.append(f"- Başlığı (caption) olan: {sum(bool(t['baslik']) for t in tablolar)} · paragraf birimine bağlı: "
                 f"{sum(t['paragraf_id'] is not None for t in tablolar)}")  # fmt: skip
    uyari = Counter(u for t in tablolar for u in t["uyarilar"])
    satir.append(f"- Uyarılar: {dict(uyari) if uyari else 'yok'}")
    n = len(olgular)
    satir.append(
        f"- Olgu: {n} · birimli {_oran(sum(o['birim'] is not None for o in olgular), n)} · dönemli "
        f"{_oran(sum(o['donem'] is not None for o in olgular), n)} · eksik değer {sum(o['eksik'] for o in olgular)}"
    )
    if baslikli is not None:
        kapsanan = {s for t in tablolar for s in t["sayfalar"]}
        kacan = [s for s in baslikli if s not in kapsanan]
        satir.append(f'- "Tablo N" başlıklı sayfa: {len(baslikli)} · tablosu bulunmayan: {kacan or "yok"}')
    secilen = sorted(
        random.Random(seed).sample(tablolar, min(ornek, len(tablolar))), key=lambda t: t["tablo_id"]
    )
    satir += ["", f"## Elle kontrol örneklemi (seed {seed})", "",
              "| tablo_id | sayfa | boyut | motor | başlık | ızgara doğru mu? | başlıklar doğru mu? | olgular doğru mu? |",
              "|---|---|---|---|---|---|---|---|"]  # fmt: skip
    for t in secilen:
        sayfa = (
            "–".join(map(str, (t["sayfalar"][0], t["sayfalar"][-1])))
            if len(t["sayfalar"]) > 1
            else str(t["sayfalar"][0])
        )
        satir.append(f"| {t['tablo_id']} | {sayfa} | {t['satir_sayisi']}×{t['sutun_sayisi']} | {t['motor']} | "
                     f"{t['baslik'][:40].replace('|', '/')} | | | |")  # fmt: skip
    return "\n".join(satir) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dizin", type=Path)
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--ornek", type=int, default=10)
    ap.add_argument("--seed", type=int, default=43)
    a = ap.parse_args(argv)
    tablolar = oku(a.dizin / "tables.jsonl")
    if not tablolar and not (a.dizin / "tables.jsonl").exists():
        print(f"tables.jsonl yok: {a.dizin}", file=sys.stderr)
        return 1
    print(
        ozet(
            tablolar,
            oku(a.dizin / "facts.jsonl"),
            baslikli_sayfalar(a.pdf) if a.pdf else None,
            a.ornek,
            a.seed,
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
