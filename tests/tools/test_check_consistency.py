"""Tutarlılık denetleyicisinin kendisinin testi: gerçek repo temiz, bozulan kopya yakalanır."""

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
    for name in [".claude", ".agents", "docs", "tools", "services", "shared", "data", "tests"]:
        shutil.copytree(ROOT / name, tmp_path / name)
    for name in ["CLAUDE.md", "AGENTS.md", "README.md", "pyproject.toml", "requirements-dev.txt"]:
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


def test_r_agt_01_plan_ile_progress_durum_uyumsuzlugu(copy):
    _edit(copy / "docs/PROGRESS.md", "| S02 | Katalog v1 🔒 | ⬜ |", "| S02 | Katalog v1 🔒 | 🟨 |")
    assert any("S02: PROGRESS durumu" in e for e in run(copy).errors)


def test_r_agt_01_baslamamis_asamada_tamamlanmis_gorev(copy):
    _edit(copy / "docs/DEVELOPMENT_PLAN.md", "  - T1 ⬜ TSRS 1 çekirdek", "  - T1 ✅ TSRS 1 çekirdek")
    assert any("plan S02: aşama ⬜ ama başlamış görev" in e for e in run(copy).errors)


def test_r_agt_01_tamam_asamada_acik_gorev_ve_kanit(copy):
    _edit(copy / "docs/DEVELOPMENT_PLAN.md", "  - T3 ✅ Kasıtlı bozma", "  - T3 🟨 Kasıtlı bozma")
    assert any("plan S15: aşama ✅ ama tamamlanmamış" in e for e in run(copy).errors)


def test_r_agt_01_kullanici_eylemi_kimliksiz_ya_da_tanimsiz(copy):
    _edit(
        copy / "docs/DEVELOPMENT_PLAN.md",
        "  - T4 ✋ U-09: Mehmet katalog v1'i onaylar.",
        "  - T4 ✋ Mehmet onaylar.",
    )
    _edit(copy / "docs/DEVELOPMENT_PLAN.md", "  - T3 ✋ U-10:", "  - T3 ✋ U-99:")
    errs = run(copy).errors
    assert any("plan S02.T4: ✋ görevde U-xx yok" in e for e in errs)
    assert any("tanımsız U-99" in e for e in errs)


def test_r_agt_01_tanimsiz_kisit_karar_ve_bagimlilik(copy):
    _edit(copy / "docs/DEVELOPMENT_PLAN.md", "(KL-02, KL-04 adayları)", "(KL-77, D-77 adayları)")
    _edit(copy / "docs/DEVELOPMENT_PLAN.md", "**Bağımlılık:** S03.T3", "**Bağımlılık:** S03.T9")
    errs = run(copy).errors
    assert any("tanımsız KL-77" in e for e in errs)
    assert any("tanımsız D-77" in e for e in errs)
    assert any("bilinmeyen bağımlılık S03.T9" in e for e in errs)


def test_r_agt_01_kapsanmayan_gereksinim(copy):
    _edit(copy / "docs/DEVELOPMENT_PLAN.md", "**Gereksinimler:** R-EXP-01", "**Gereksinimler:** —")
    assert any("R-EXP-01 plandaki hiçbir aşamada yok" in e for e in run(copy).errors)


def test_claude_md_agents_md_icermeli(copy):
    _edit(copy / "CLAUDE.md", "@AGENTS.md", "AGENTS.md")
    assert any("içe aktarmıyor" in e for e in run(copy).errors)


def test_detects_undefined_adr_and_broken_path(copy):
    _edit(copy / "AGENTS.md", "# AGENTS.md", "# AGENTS.md (ADR-999, `docs/YOK.md`)")
    errs = run(copy).errors
    assert any("ADR-999" in e for e in errs)
    assert any("docs/YOK.md" in e for e in errs)
