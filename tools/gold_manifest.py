#!/usr/bin/env python3
"""Altın test kümesinin dondurulması ve doğrulanması (R-ETK-02, B11).

    python tools/gold_manifest.py freeze --by "<ad soyad>"   # YALNIZCA İNSAN (guard ajanlara kapalı)
    python tools/gold_manifest.py verify                      # CI ve evaluator

`freeze`, data/gold/ altındaki dosyaların SHA-256 özetlerini data/gold/MANIFEST.json'a yazar.
`verify`, dosyalar değişmişse, eklenmiş veya silinmişse 1 ile çıkar.
Küme henüz yoksa (dizin boş veya yok) `verify` bilgi verir ve 0 ile çıkar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "MANIFEST.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current(gold: Path) -> dict[str, str]:
    if not gold.is_dir():
        return {}
    return {
        p.relative_to(gold).as_posix(): digest(p)
        for p in sorted(gold.rglob("*"))
        if p.is_file() and p.name != MANIFEST and p.name != ".gitkeep"
    }


def freeze(gold: Path, by: str) -> int:
    files = current(gold)
    if not files:
        print("data/gold/ boş; dondurulacak dosya yok.")
        return 1
    manifest = {
        "frozen_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "frozen_by": by,
        "files": files,
    }
    (gold / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(files)} dosya donduruldu → {gold / MANIFEST}")
    return 0


def verify(gold: Path) -> int:
    files = current(gold)
    mpath = gold / MANIFEST
    if not mpath.exists():
        if files:
            print(f"HATA: {len(files)} dosya var ama MANIFEST.json yok (dondurulmamış küme).")
            return 1
        print("Altın küme henüz yok (doğrulanacak bir şey yok).")
        return 0
    expected = json.loads(mpath.read_text())["files"]
    problems = []
    for name in sorted(expected.keys() | files.keys()):
        if name not in files:
            problems.append(f"eksik: {name}")
        elif name not in expected:
            problems.append(f"manifestte yok (sonradan eklenmiş): {name}")
        elif files[name] != expected[name]:
            problems.append(f"değişmiş: {name}")
    for p in problems:
        print("HATA:", p)
    if not problems:
        print(f"Altın küme doğrulandı ({len(files)} dosya).")
    return 1 if problems else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("komut", choices=["freeze", "verify"])
    ap.add_argument("--by", default="")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    gold = args.root / "data" / "gold"
    if args.komut == "freeze":
        if not args.by:
            ap.error("freeze için --by '<ad soyad>' zorunlu")
        return freeze(gold, args.by)
    return verify(gold)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
