#!/usr/bin/env python3
"""Retrieval metrikleri: Recall@k ve MRR, rapor bazında ortalama (R-RET-01, B2).

    python .claude/skills/embed-eval/scripts/retrieval_metrics.py siralama.json --k 5 10 20

`siralama.json`:
{
  "model": "multilingual-e5-base",
  "sorgular": [
    {"madde_id": "TSRS2-YON-06a", "rapor_id": "karel-2025",
     "siralama": ["p1", "p7", ...],          # o rapordaki paragraflar, benzerliğe göre azalan
     "ilgili": ["p7"]}                         # etiketi 1 veya 2 olan paragraflar
  ]
}
İlgili paragrafı olmayan sorgular Recall/MRR'a girmez (tanımsız); sayısı ayrıca raporlanır.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    return len(set(ranked[:k]) & relevant) / len(relevant)


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    for i, pid in enumerate(ranked, start=1):
        if pid in relevant:
            return 1.0 / i
    return 0.0


def evaluate(queries: list[dict], ks: list[int]) -> dict:
    per_report: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    skipped = 0
    for q in queries:
        rel = set(q["ilgili"])
        if not rel:
            skipped += 1
            continue
        bucket = per_report[q["rapor_id"]]
        for k in ks:
            bucket[f"recall@{k}"].append(recall_at_k(q["siralama"], rel, k))
        bucket["mrr"].append(reciprocal_rank(q["siralama"], rel))
    metrics = {}
    names = [f"recall@{k}" for k in ks] + ["mrr"]
    for name in names:
        report_means = [mean(b[name]) for b in per_report.values() if b[name]]
        metrics[name] = round(mean(report_means), 4) if report_means else None
    return {"metrikler": metrics, "rapor_sayisi": len(per_report), "ilgilisiz_sorgu": skipped}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dosya", type=Path)
    ap.add_argument("--k", type=int, nargs="+", default=[5, 10, 20])
    args = ap.parse_args(argv)
    data = json.loads(args.dosya.read_text(encoding="utf-8"))
    res = evaluate(data["sorgular"], args.k) | {"model": data.get("model")}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
