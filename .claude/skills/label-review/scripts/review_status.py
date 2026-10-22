#!/usr/bin/env python3
"""Onay kuyruğunun durumu: dosya başına bekleyen / onaylanan / düzeltilen / reddedilen (R-HIL-01).

    python .claude/skills/label-review/scripts/review_status.py [--data data]

Ajanlar onaylı dosyaları ve günlüğü komut satırında adıyla anamaz (guard engeller). Bu betik
onları kod içinden salt-okunur olarak okur ve yalnızca sayıları basar; içerik yazmaz.
Düzeltme oranı yüksekse (> %30) kılavuz veya öneri kalitesi sorunu vardır; orkestratöre raporla.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "services" / "review-ui"))
from review_ui.logic import Paths, proposal_files, read_rows  # noqa: E402


def status(paths: Paths) -> list[dict]:
    decisions: dict[str, Counter] = {}
    if paths.log.exists():
        for line in paths.log.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            decisions.setdefault(rec["dosya"], Counter())[rec["karar"]] += 1
    out = []
    for f in proposal_files(paths):
        total = len(read_rows(f))
        c = decisions.get(f.name, Counter())
        done = sum(c.values())
        out.append(
            {
                "dosya": f.name,
                "toplam": total,
                "bekleyen": max(total - done, 0),
                "onayla": c["onayla"],
                "duzelt": c["duzelt"],
                "reddet": c["reddet"],
                "duzeltme_orani": round((c["duzelt"] + c["reddet"]) / done, 3) if done else None,
            }
        )
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=ROOT / "data")
    args = ap.parse_args(argv)
    rows = status(Paths(args.data))
    if not rows:
        print("Öneri dosyası yok.")
        return 0
    print("| dosya | toplam | bekleyen | onay | düzeltme | red | düzeltme+red oranı |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        oran = "—" if r["duzeltme_orani"] is None else f"{r['duzeltme_orani']:.0%}"
        print(
            f"| {r['dosya']} | {r['toplam']} | {r['bekleyen']} | {r['onayla']} | {r['duzelt']} | {r['reddet']} | {oran} |"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
