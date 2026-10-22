#!/usr/bin/env python3
"""İki katalog sürümü arasındaki farkı onay için Markdown olarak üretir (R-KAT-01).

    python .claude/skills/catalog-update/scripts/diff_catalog.py data/catalog/catalog_v0.csv data/catalog/catalog_v1.csv

Çıktı: eklenen, silinen ve alan bazında değişen maddeler. Kullanıcıya onay için bu tablo gösterilir.
Silinen madde varsa ayrıca uyarı basar: o maddeye bağlı etiketler yetim kalır.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


def load(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return {r["madde_id"]: r for r in csv.DictReader(fh)}


def diff(old: dict[str, dict], new: dict[str, dict]) -> dict[str, list]:
    added = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())
    changed = []
    for mid in sorted(old.keys() & new.keys()):
        for col in sorted(set(old[mid]) | set(new[mid])):
            a, b = old[mid].get(col, "∅"), new[mid].get(col, "∅")
            if a != b:
                changed.append((mid, col, a, b))
    return {"eklenen": added, "silinen": removed, "degisen": changed}


def to_markdown(d: dict, new: dict[str, dict]) -> str:
    out = [
        f"**Eklenen:** {len(d['eklenen'])} · **Silinen:** {len(d['silinen'])} · **Değişen alan:** {len(d['degisen'])}",
        "",
    ]
    if d["eklenen"]:
        out += ["### Eklenen", "| madde_id | başlık | üst madde |", "|---|---|---|"]
        out += [f"| {m} | {new[m]['baslik']} | {new[m].get('ust_madde', '')} |" for m in d["eklenen"]]
    if d["silinen"]:
        out += [
            "",
            "### Silinen",
            "⚠ Bu maddelere bağlı etiketler yetim kalır; etiket dosyalarını kontrol et.",
        ]
        out += [f"- {m}" for m in d["silinen"]]
    if d["degisen"]:
        out += ["", "### Değişen", "| madde_id | alan | eski | yeni |", "|---|---|---|---|"]
        out += [f"| {m} | {c} | {a} | {b} |" for m, c, a, b in d["degisen"]]
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    old, new = load(Path(argv[0])), load(Path(argv[1]))
    print(to_markdown(diff(old, new), new))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
