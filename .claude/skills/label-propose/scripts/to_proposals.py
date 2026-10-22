#!/usr/bin/env python3
"""Model kararlarını (JSONL) doğrulanmış öneri CSV'sine dönüştürür (R-ETK-01).

    python .claude/skills/label-propose/scripts/to_proposals.py \
        --paragraphs data/labels/pilot/orneklem.jsonl --judgments kararlar.jsonl \
        --out data/labels/proposals/pilot-kor-karel-2026-10-23.csv --tarih 2026-10-23

`kararlar.jsonl` her satırda: {"paragraf_id", "madde_id", "karsilama", "guven", "gerekce"}
- Bir paragrafın hiçbir maddeyle ilgisi yoksa açıkça {"madde_id": "NONE", "karsilama": "NONE", ...} yazılır.
- Kararı olmayan paragraf HATA'dır: sessizce NONE sayılmaz (incelenmediği bilinmeli).
- Çıktı tools/validate_data.py ile doğrulanır; hata varsa dosya yazılmaz ve çıkış 1 olur.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))
from validate_data import LABEL_HEADER, validate_file  # noqa: E402


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_rows(
    paragraphs: list[dict], judgments: list[dict], tarih: str, etiketleyen: str
) -> tuple[list[dict], list[str]]:
    by_pid = {p["paragraf_id"]: p for p in paragraphs}
    errors = [
        f"kararda bilinmeyen paragraf: {j['paragraf_id']}"
        for j in judgments
        if j["paragraf_id"] not in by_pid
    ]
    judged = {j["paragraf_id"] for j in judgments}
    errors += [f"karar verilmemiş paragraf: {pid}" for pid in by_pid if pid not in judged]
    rows = []
    for j in judgments:
        p = by_pid.get(j["paragraf_id"])
        if p is None:
            continue
        rows.append(
            {
                "etiket_id": f"{p['paragraf_id']}::{j['madde_id']}",
                "tur": "paragraf",
                "rapor_id": p["rapor_id"],
                "sirket": p.get("sirket", ""),
                "yil": str(p.get("yil", "")),
                "paragraf_id": p["paragraf_id"],
                "sayfa": str(p.get("sayfa", "")),
                "bolum_basligi": p.get("bolum_basligi", ""),
                "metin": p["metin"],
                "madde_id": j["madde_id"],
                "karsilama": str(j["karsilama"]),
                "guven": f"{float(j['guven']):.2f}",
                "gerekce": j["gerekce"].strip(),
                "etiketleyen": etiketleyen,
                "kaynak": "model_onerisi",
                "tarih": tarih,
            }
        )
    return rows, errors


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paragraphs", type=Path, required=True)
    ap.add_argument("--judgments", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tarih", required=True)
    ap.add_argument("--etiketleyen", default="claude")
    args = ap.parse_args(argv)
    rows, errors = build_rows(
        read_jsonl(args.paragraphs), read_jsonl(args.judgments), args.tarih, args.etiketleyen
    )
    if errors:
        print("\n".join("HATA: " + e for e in errors))
        return 1
    tmp = args.out.with_suffix(".tmp.csv")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LABEL_HEADER)
        w.writeheader()
        w.writerows(rows)
    problems = validate_file(tmp)
    if problems:
        tmp.unlink()
        print("\n".join("HATA: " + e for e in problems))
        return 1
    tmp.replace(args.out)
    print(f"{len(rows)} öneri satırı, {len({r['paragraf_id'] for r in rows})} paragraf → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
