#!/usr/bin/env python3
"""Tek komutluk kalite kapısı: yerelde ve CI'da aynı adımlar (`.claude/rules/quality-gates.md`).

    python tools/check_all.py

Adımlar sırayla koşar; biri başarısız olsa da diğerleri koşar ve sonunda özet basılır.
Herhangi bir adım başarısızsa çıkış kodu 1'dir.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

STEPS = [
    ("ruff check", ["ruff", "check", "."]),
    ("ruff format --check", ["ruff", "format", "--check", "."]),
    ("pytest", [PY, "-m", "pytest", "-q"]),
    ("veri doğrulayıcı", [PY, "tools/validate_data.py"]),
    ("tutarlılık denetleyicisi", [PY, "tools/check_consistency.py"]),
    ("altın küme manifesti", [PY, "tools/gold_manifest.py", "verify"]),
]


def main() -> int:
    results = []
    for name, cmd in STEPS:
        if cmd[0] == "ruff" and shutil.which("ruff") is None:
            results.append((name, None, "ruff kurulu değil"))
            continue
        print(f"\n=== {name}: {' '.join(cmd)}", flush=True)
        proc = subprocess.run(cmd, cwd=ROOT)
        results.append((name, proc.returncode, ""))
    print("\n=== ÖZET")
    failed = False
    for name, code, note in results:
        if code is None:
            status = f"KOŞULAMADI ({note})"
            failed = True
        elif code == 0:
            status = "GEÇTİ"
        else:
            status = f"BAŞARISIZ (çıkış {code})"
            failed = True
        print(f"  {status:<28} {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
