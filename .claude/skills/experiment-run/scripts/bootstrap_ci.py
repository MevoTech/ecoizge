#!/usr/bin/env python3
"""Rapor bazında gruplu bootstrap ile ortalama ve %95 güven aralığı (R-EVL-01, R-EVL-04).

    python .claude/skills/experiment-run/scripts/bootstrap_ci.py sonuclar.csv --grup rapor_id --deger dogru --seed 43

Neden gruplu: aynı raporun paragrafları birbirine bağımlıdır. Paragrafları tek tek yeniden
örneklemek aralığı yapay olarak daraltır. Burada raporlar (gruplar) yerine konarak örneklenir.
`--deger` sütunu 0/1 (doğru/yanlış) ya da sayısal olabilir.
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path


def grouped_bootstrap(
    groups: dict[str, list[float]], n_boot: int = 2000, seed: int = 43, alpha: float = 0.05
):
    keys = sorted(groups)
    if not keys:
        raise ValueError("boş veri")
    flat = [v for k in keys for v in groups[k]]
    point = sum(flat) / len(flat)
    rng = random.Random(seed)
    stats = []
    for _ in range(n_boot):
        pick = [groups[rng.choice(keys)] for _ in keys]
        vals = [v for g in pick for v in g]
        stats.append(sum(vals) / len(vals))
    stats.sort()
    lo = stats[int(alpha / 2 * n_boot)]
    hi = stats[min(int((1 - alpha / 2) * n_boot), n_boot - 1)]
    return point, lo, hi


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--grup", default="rapor_id")
    ap.add_argument("--deger", required=True)
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=43)
    args = ap.parse_args(argv)
    groups: dict[str, list[float]] = defaultdict(list)
    with args.csv.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            groups[r[args.grup]].append(float(r[args.deger]))
    point, lo, hi = grouped_bootstrap(groups, args.n, args.seed)
    n = sum(len(v) for v in groups.values())
    print(
        f"{args.deger}: {point:.4f}  %95 GA [{lo:.4f}, {hi:.4f}]  (n={n}, grup={len(groups)}, B={args.n}, tohum={args.seed})"
    )
    if len(groups) < 5:
        print("UYARI: 5'ten az grup; aralık güvenilir değil, tezde bunu belirt.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
