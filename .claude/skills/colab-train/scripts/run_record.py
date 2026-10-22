#!/usr/bin/env python3
"""Koşu kaydı (run.json) üretir ve doğrular (R-REP-01, ADR-005).

Colab defterinin son hücresinde ya da yerelde:
    python .claude/skills/colab-train/scripts/run_record.py create --gorev S14 --veri-surumu reviewed-2026-11-20 \
        --katalog-surumu catalog_v1 --tohum 43 --metrikler '{"f1_makro": 0.61}' --out runs/
    python .claude/skills/colab-train/scripts/run_record.py validate runs/<run_id>/run.json

`create` git commit'ini, paket sürümlerini ve donanımı kendisi doldurur; elle yazılmaz.
`durum` her zaman `onay_bekliyor` başlar; `kabul`'e yalnızca onay arayüzünden geçer.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path

SCHEMA = Path(__file__).resolve().parent.parent / "references" / "run.schema.json"
PACKAGES = ["scikit-learn", "numpy", "torch", "transformers", "sentence-transformers", "pymupdf"]


def git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else "bilinmiyor"
    except (OSError, subprocess.SubprocessError):
        return "bilinmiyor"


def packages() -> dict[str, str]:
    found = {}
    for p in PACKAGES:
        try:
            found[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            continue
    return found


def hardware() -> str:
    desc = f"{platform.system()} {platform.machine()} · Python {platform.python_version()}"
    try:
        import torch

        if torch.cuda.is_available():
            desc += f" · GPU {torch.cuda.get_device_name(0)}"
    except ImportError:
        pass
    return desc


def create(gorev: str, veri: str, katalog: str, tohum: int, metrikler: dict, **extra) -> dict:
    now = datetime.now()
    slug = re.sub(r"[^a-z0-9-]+", "-", gorev.lower()).strip("-")
    return {
        "run_id": f"{now:%Y%m%d-%H%M%S}-{slug}",
        "git_sha": git_sha(),
        "gorev": gorev,
        "veri_surumu": veri,
        "katalog_surumu": katalog,
        "tohum": tohum,
        "paketler": packages(),
        "donanim": hardware(),
        "metrikler": metrikler,
        "durum": "onay_bekliyor",
        "olusturma": now.isoformat(timespec="seconds"),
    } | {k: v for k, v in extra.items() if v is not None}


def validate(record: dict) -> list[str]:
    from jsonschema import Draft202012Validator

    v = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    return [f"{'/'.join(map(str, e.path)) or '(kök)'}: {e.message}" for e in v.iter_errors(record)]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="komut", required=True)
    c = sub.add_parser("create")
    c.add_argument("--gorev", required=True)
    c.add_argument("--veri-surumu", required=True)
    c.add_argument("--katalog-surumu", required=True)
    c.add_argument("--tohum", type=int, required=True)
    c.add_argument("--metrikler", required=True, help="JSON nesnesi")
    c.add_argument("--parametreler", default=None, help="JSON nesnesi")
    c.add_argument("--model-yolu", default=None)
    c.add_argument("--altin-kume", action="store_true")
    c.add_argument("--out", type=Path, default=Path("runs"))
    v = sub.add_parser("validate")
    v.add_argument("dosya", type=Path)
    args = ap.parse_args(argv)
    if args.komut == "validate":
        errs = validate(json.loads(args.dosya.read_text(encoding="utf-8")))
        print("\n".join("HATA: " + e for e in errs) or f"geçerli: {args.dosya}")
        return 1 if errs else 0
    rec = create(
        args.gorev,
        args.veri_surumu,
        args.katalog_surumu,
        args.tohum,
        json.loads(args.metrikler),
        parametreler=json.loads(args.parametreler) if args.parametreler else None,
        model_yolu=args.model_yolu,
        altin_kume_kullanildi=args.altin_kume,
    )
    errs = validate(rec)
    if errs:
        print("\n".join("HATA: " + e for e in errs))
        return 1
    path = args.out / rec["run_id"] / "run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"koşu kaydı: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
