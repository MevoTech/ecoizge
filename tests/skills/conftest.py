"""Skill betiklerini test için içe aktarılabilir yapar (`.claude/skills/<ad>/scripts/`)."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".claude" / "skills"


def load(skill: str, script: str):
    path = SKILLS / skill / "scripts" / f"{script}.py"
    spec = importlib.util.spec_from_file_location(f"skill_{skill.replace('-', '_')}_{script}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod
