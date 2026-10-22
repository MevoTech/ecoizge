"""Tutarlılık denetleyicisinin kendisinin testi: gerçek repo temiz, bozulan kopya yakalanır."""

import re
import shutil
from pathlib import Path

import pytest

from check_consistency import run

ROOT = Path(__file__).resolve().parents[2]


def test_repository_is_consistent():
    rep = run(ROOT)
    assert rep.errors == [], "\n".join(rep.errors)
    assert rep.checks > 300


@pytest.fixture
def copy(tmp_path) -> Path:
    for name in [".claude", "docs", "tasks", "tools", "services", "shared", "data", "tests"]:
        shutil.copytree(ROOT / name, tmp_path / name)
    for name in ["CLAUDE.md", "README.md", "pyproject.toml", "requirements-dev.txt"]:
        shutil.copy(ROOT / name, tmp_path / name)
    (tmp_path / ".github").mkdir()
    shutil.copytree(ROOT / ".github/workflows", tmp_path / ".github/workflows")
    return tmp_path


def _edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, old
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_detects_subagent_with_agent_tool(copy):
    _edit(copy / ".claude/agents/architect.md", "tools: Read,", "tools: Agent, Read,")
    assert any("Agent aracına sahip" in e for e in run(copy).errors)


def test_detects_scope_mismatch(copy):
    _edit(copy / ".claude/agents/evaluator.md", "- `reports/experiments/**`", "- `reports/**`")
    assert any("evaluator: Yazma alanı" in e for e in run(copy).errors)


def test_detects_missing_skill(copy):
    shutil.rmtree(copy / ".claude/skills/numeric-verify")
    errs = run(copy).errors
    assert any("olmayan skill 'numeric-verify'" in e for e in errs)


def test_detects_task_status_drift(copy):
    readme = copy / "tasks/README.md"
    text = readme.read_text(encoding="utf-8")
    m = re.search(r"^\|\s*\[S02\][^\n]*\|\s*(bekliyor|devam|tamam|engelli)\s*\|", text, re.M)
    assert m
    new_line = m.group(0).replace(m.group(1), "tamam" if m.group(1) != "tamam" else "bekliyor")
    readme.write_text(text.replace(m.group(0), new_line), encoding="utf-8")
    assert any("S02: README durumu" in e for e in run(copy).errors)


def test_detects_undefined_adr_and_broken_path(copy):
    _edit(copy / "CLAUDE.md", "# EcoIzge", "# EcoIzge (ADR-999, `docs/YOK.md`)")
    errs = run(copy).errors
    assert any("ADR-999" in e for e in errs)
    assert any("docs/YOK.md" in e for e in errs)
