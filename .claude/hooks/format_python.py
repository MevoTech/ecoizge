#!/usr/bin/env python3
"""PostToolUse kancası: düzenlenen .py dosyasında `ruff format` çalıştırır.

Engelleyici değildir: ruff yoksa veya hata verirse sessizce çıkar (çıkış 0).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys


def main() -> None:
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return
    path = (event.get("tool_input") or {}).get("file_path", "")
    ruff = shutil.which("ruff")
    if not path.endswith(".py") or not os.path.isfile(path) or ruff is None:
        return
    subprocess.run([ruff, "format", "--quiet", path], check=False, timeout=30)


if __name__ == "__main__":
    main()
    sys.exit(0)
