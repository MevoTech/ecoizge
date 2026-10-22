#!/usr/bin/env python3
"""Bir taslağı (yer tutuculu metin) kaynak kayıtlarla denetler ve doldurur (R-GEN-03, R-VER-01, R-VER-03).

    python .claude/skills/numeric-verify/scripts/check_draft.py --draft taslak.txt --records kayitlar.json

`kayitlar.json`: shared/contracts/forecast_record.schema.json biçiminde kayıt listesi
(gerçekleşmiş kayıtlarda model alanları yok). Çıktı JSON: {ok, errors, text, claims}. Hata varsa çıkış 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "services" / "report-service"))
from report_service.generation.placeholders import Record, render  # noqa: E402


def to_record(d: dict) -> Record:
    ci = d.get("guven_araligi")
    return Record(
        kpi=d["kpi"],
        yil=int(d["yil"]),
        deger=float(d["deger"]),
        birim=d["birim"],
        veri_turu=d["veri_turu"],
        kaynak=d["kaynak"],
        model_id=d.get("model_id"),
        senaryo_id=d.get("senaryo_id"),
        guven_araligi=tuple(ci) if ci else None,
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", type=Path, required=True)
    ap.add_argument("--records", type=Path, required=True)
    args = ap.parse_args(argv)
    records = [to_record(d) for d in json.loads(args.records.read_text(encoding="utf-8"))]
    res = render(args.draft.read_text(encoding="utf-8"), records)
    print(
        json.dumps(
            {"ok": res.ok, "errors": res.errors, "text": res.text, "claims": res.claims},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if res.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
