#!/usr/bin/env python3
"""Çıkarım kalite raporu: şüpheli birimleri işaretler ve elle kontrol örneklemi seçer (R-PDF-02, S04).

    python .claude/skills/pdf-extract/scripts/qa_report.py data/processed/karel-2025/paragraphs.jsonl --sayfa 20 --seed 43

Otomatik işaretler (her biri bir hata türü; tezdeki çıkarım hata tablosuna girer):
- bozuk_sayi     "12 450 ." gibi ayrılmış binlik/ondalık (tablo okuyucu hatası)
- tire_kalintisi satır içinde "sürdürüle- bilirlik" gibi birleşmemiş tireleme
- cok_uzun       > 1500 karakter: birden çok paragraf ya da sütun karışmış olabilir
- tablo_sizintisi tur=paragraf ama satırların çoğu ' | ' ya da çok sayı içeriyor
- basliksiz      bolum_basligi boş (başlık tespiti kaçırmış olabilir)
Sonra rastgele N sayfa seçilir: insan bu sayfaları PDF ile yan yana açıp kontrol eder.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

CHECKS = {
    "bozuk_sayi": lambda u: re.search(r"\b\d{1,3} \d{3}\b|\d \.(?:\s|$)", u["metin"]) is not None,
    "tire_kalintisi": lambda u: re.search(r"[a-zçğıöşü]- [a-zçğıöşü]", u["metin"]) is not None,
    "cok_uzun": lambda u: len(u["metin"]) > 1500,
    "tablo_sizintisi": lambda u: (
        u["tur"] == "paragraf" and len(re.findall(r"\d", u["metin"])) > 0.35 * max(len(u["metin"]), 1)
    ),
    "basliksiz": lambda u: not u.get("bolum_basligi"),
}


def analyze(units: list[dict], n_pages: int, seed: int) -> dict:
    flags = Counter()
    flagged = []
    for u in units:
        hits = [name for name, fn in CHECKS.items() if fn(u)]
        flags.update(hits)
        if hits and hits != ["basliksiz"]:
            flagged.append(
                {
                    "paragraf_id": u["paragraf_id"],
                    "sayfa": u["sayfa"],
                    "isaretler": hits,
                    "metin": u["metin"][:160],
                }
            )
    pages = sorted({u["sayfa"] for u in units})
    sample = sorted(random.Random(seed).sample(pages, min(n_pages, len(pages))))
    return {
        "birim": len(units),
        "tur": dict(Counter(u["tur"] for u in units)),
        "isaret_sayilari": dict(flags),
        "isaretli_birimler": flagged,
        "elle_kontrol_sayfalari": sample,
    }


def to_markdown(rep: dict, src: Path) -> str:
    lines = [
        f"# Çıkarım kalite raporu · `{src}`",
        f"- Birim: {rep['birim']} · türler: {rep['tur']}",
        f"- Otomatik işaretler: {rep['isaret_sayilari'] or 'yok'}",
        f"- Elle kontrol edilecek sayfalar: {rep['elle_kontrol_sayfalari']}",
        "",
        "## Elle kontrol tablosu (PDF ile yan yana doldur)",
        "| sayfa | eksik metin | fazla metin | kırık tablo | sütun karışması | yanlış başlık | not |",
        "|---|---|---|---|---|---|---|",
    ]
    lines += [f"| {p} |  |  |  |  |  |  |" for p in rep["elle_kontrol_sayfalari"]]
    lines += [
        "",
        "## Otomatik işaretli birimler",
        "| paragraf_id | sayfa | işaret | metin (ilk 160) |",
        "|---|---|---|---|",
    ]
    lines += [
        f"| {f['paragraf_id']} | {f['sayfa']} | {', '.join(f['isaretler'])} | {f['metin']} |"
        for f in rep["isaretli_birimler"]
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paragraphs", type=Path)
    ap.add_argument("--sayfa", type=int, default=20)
    ap.add_argument("--seed", type=int, default=43)
    args = ap.parse_args(argv)
    with args.paragraphs.open(encoding="utf-8") as fh:
        units = [json.loads(x) for x in fh if x.strip()]
    print(to_markdown(analyze(units, args.sayfa, args.seed), args.paragraphs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
