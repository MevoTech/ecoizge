#!/usr/bin/env python3
"""Etiketleyiciler arası uyum: ağırlıklı Cohen's κ (R-ETK-01, B6).

Kullanım:
    python tools/kappa.py A.csv B.csv [--weights quadratic|linear|none] [--out rapor.md]

Eşleme anahtarı (paragraf_id, madde_id). Yalnızca iki dosyada da incelenmiş paragraflar
karşılaştırılır; bir tarafta olmayan (paragraf, madde) çifti NONE sayılır.
Sıralı ölçek: NONE=0, 1=1, 2=2. 'U' (uygulanamaz) sıralı ölçeğe girmez, ayrı sayılır.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ORDINAL = {"NONE": 0, "1": 1, "2": 2}


def weighted_kappa(a: list[int], b: list[int], k: int, weights: str = "quadratic") -> float:
    """k kategorili (0..k-1) iki etiket dizisi için ağırlıklı Cohen's κ."""
    if len(a) != len(b) or not a:
        raise ValueError("diziler boş olmayan ve eşit uzunlukta olmalı")
    n = len(a)
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b, strict=True):
        obs[x][y] += 1
    row = [sum(obs[i]) for i in range(k)]
    col = [sum(obs[i][j] for i in range(k)) for j in range(k)]

    def w(i: int, j: int) -> float:
        if weights == "none":
            return 0.0 if i == j else 1.0
        d = abs(i - j) / (k - 1) if k > 1 else 0.0
        return d if weights == "linear" else d * d

    num = sum(w(i, j) * obs[i][j] for i in range(k) for j in range(k)) / n
    den = sum(w(i, j) * row[i] * col[j] for i in range(k) for j in range(k)) / (n * n)
    if den == 0:
        return 1.0 if num == 0 else 0.0
    return 1.0 - num / den


def load(path: Path) -> tuple[dict[tuple[str, str], str], set[str]]:
    labels: dict[tuple[str, str], str] = {}
    paragraphs: set[str] = set()
    with path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["tur"] != "paragraf":
                continue
            paragraphs.add(r["paragraf_id"])
            if r["madde_id"] != "NONE":
                labels[(r["paragraf_id"], r["madde_id"])] = r["karsilama"]
    return labels, paragraphs


def compare(path_a: Path, path_b: Path, weights: str) -> dict:
    la, pa = load(path_a)
    lb, pb = load(path_b)
    common = pa & pb
    keys = sorted({k for k in la.keys() | lb.keys() if k[0] in common})
    a, b, disagreements, u_pairs = [], [], [], 0
    for key in keys:
        va, vb = la.get(key, "NONE"), lb.get(key, "NONE")
        if "U" in (va, vb):
            u_pairs += 1
            if va != vb:
                disagreements.append((key, va, vb))
            continue
        a.append(ORDINAL[va])
        b.append(ORDINAL[vb])
        if va != vb:
            disagreements.append((key, va, vb))
    kappa = weighted_kappa(a, b, 3, weights) if a else float("nan")
    return {
        "paragraf_ortak": len(common),
        "cift": len(keys),
        "olculen": len(a),
        "u_cift": u_pairs,
        "kappa": kappa,
        "agirlik": weights,
        "anlasmazlik": disagreements,
    }


def to_markdown(res: dict, path_a: Path, path_b: Path) -> str:
    lines = [
        "# Uyum raporu",
        f"- A: `{path_a}`  ·  B: `{path_b}`",
        f"- Ortak paragraf: {res['paragraf_ortak']}  ·  çift: {res['cift']}  ·  "
        f"κ'ya giren: {res['olculen']}  ·  U içeren çift: {res['u_cift']}",
        f"- Ağırlıklı κ ({res['agirlik']}): **{res['kappa']:.3f}**",
        "",
        "## Anlaşmazlıklar",
        "| paragraf_id | madde_id | A | B |",
        "|---|---|---|---|",
    ]
    lines += [f"| {k[0]} | {k[1]} | {va} | {vb} |" for k, va, vb in res["anlasmazlik"]]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--weights", choices=["quadratic", "linear", "none"], default="quadratic")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    res = compare(args.a, args.b, args.weights)
    md = to_markdown(res, args.a, args.b)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
