#!/usr/bin/env python3
"""Pilot etiketleme örneklemi: aday + rastgele paragraf seçimi (S05, kılavuz §7.1, bulgu B5).

    python .claude/skills/label-propose/scripts/sample_pilot.py \
        data/processed/karel-2025/paragraphs.jsonl [data/processed/<diğer>/paragraphs.jsonl ...] \
        --catalog data/catalog/catalog_v0.csv --aday 30 --rastgele 20 --seed 43 \
        --out data/labels/pilot/orneklem.jsonl --hints data/labels/pilot/ipuclari.json

Neden iki parça:
- **Aday** paragraflar katalog maddeleriyle kelime örtüşmesi en yüksek olanlardır; pozitif örnek toplar.
- **Rastgele** paragraflar aday olmayanlardan seçilir. Sistemin kaçırabileceği pozitifleri ve
  NONE oranını ölçmek için gereklidir. Yalnız aday seçmek recall'u yapay olarak yükseltir (B5).

`orneklem.jsonl` etiketleyiciye gider ve madde ipucu İÇERMEZ (körleme). `ipuclari.json` yalnızca
model önerisi turunda kullanılır.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
from pathlib import Path

STOP = set(
    [
        "ve",
        "ile",
        "için",
        "bir",
        "bu",
        "da",
        "de",
        "olarak",
        "olan",
        "ise",
        "gibi",
        "daha",
        "en",
        "çok",
        "her",
        "şirket",
        "şirketimiz",
        "ilgili",
        "kadar",
        "sonra",
        "önce",
        "veya",
        "ya",
        "hem",
        "ancak",
        "ayrıca",
        "tüm",
        "olan",
        "olup",
        "olduğu",
        "olduğunu",
        "bilgi",
        "açıklanması",
        "açıklama",
        "kapsamında",
        "yer",
        "alan",
    ]
)


def tr_lower(text: str) -> str:
    return text.replace("I", "ı").replace("İ", "i").lower()


def tokens(text: str) -> set[str]:
    """Türkçe küçük harf + durak sözcük çıkarma + 5 karakterlik kök yaklaşımı."""
    words = re.findall(r"[a-zçğıöşü0-9]+", tr_lower(text))
    return {w[:5] for w in words if len(w) > 2 and w not in STOP}


def load_paragraphs(paths: list[Path], min_len: int) -> list[dict]:
    out = []
    for p in paths:
        with p.open(encoding="utf-8") as fh:
            out += [json.loads(line) for line in fh if line.strip()]
    return [u for u in out if len(u["metin"]) >= min_len]


def item_tokens(catalog: Path) -> dict[str, set[str]]:
    with catalog.open(encoding="utf-8", newline="") as fh:
        return {r["madde_id"]: tokens(f"{r['baslik']} {r['gereklilik_ozeti']}") for r in csv.DictReader(fh)}


def score(par: set[str], item: set[str]) -> float:
    """Madde terimlerinin paragrafta bulunma oranı."""
    return len(par & item) / len(item) if item else 0.0


def sample(paragraphs: list[dict], items: dict[str, set[str]], n_aday: int, n_rastgele: int, seed: int):
    scored = []
    for u in paragraphs:
        pt = tokens(u["metin"])
        ranked = sorted(((score(pt, it), mid) for mid, it in items.items()), reverse=True)
        scored.append((ranked[0][0] if ranked else 0.0, u, [m for _, m in ranked[:3]]))

    # Adaylar raporlar arasında sırayla (round-robin) seçilir; tek rapor örneklemi domine etmez.
    by_report: dict[str, list] = {}
    for s in sorted(scored, key=lambda x: (-x[0], x[1]["paragraf_id"])):
        by_report.setdefault(s[1]["rapor_id"], []).append(s)
    aday: list = []
    while len(aday) < n_aday and any(by_report.values()):
        for rid in sorted(by_report):
            if by_report[rid] and len(aday) < n_aday:
                aday.append(by_report[rid].pop(0))
    chosen = {s[1]["paragraf_id"] for s in aday}
    rest = [s for s in scored if s[1]["paragraf_id"] not in chosen]
    rnd = random.Random(seed).sample(rest, min(n_rastgele, len(rest)))

    rows, hints = [], {}
    for secim, group in (("aday", aday), ("rastgele", rnd)):
        for sc, u, top in group:
            rows.append(u | {"secim": secim})
            hints[u["paragraf_id"]] = {"skor": round(sc, 3), "aday_maddeler": top}
    random.Random(seed + 1).shuffle(rows)  # etiketleyici aday/rastgele sırasını görmesin
    return rows, hints


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paragraphs", type=Path, nargs="+")
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--aday", type=int, default=30)
    ap.add_argument("--rastgele", type=int, default=20)
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--min-len", type=int, default=40)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--hints", type=Path, required=True)
    args = ap.parse_args(argv)
    paras = load_paragraphs(args.paragraphs, args.min_len)
    rows, hints = sample(paras, item_tokens(args.catalog), args.aday, args.rastgele, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps({k: v for k, v in r.items() if k != "secim"}, ensure_ascii=False) + "\n")
    args.hints.write_text(
        json.dumps(
            {r["paragraf_id"]: hints[r["paragraf_id"]] | {"secim": r["secim"]} for r in rows},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    n_a = sum(r["secim"] == "aday" for r in rows)
    print(f"{len(rows)} paragraf ({n_a} aday, {len(rows) - n_a} rastgele) / havuz {len(paras)} → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
