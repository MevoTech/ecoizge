#!/usr/bin/env python3
"""Ajan–skill–kural–belge–görev sisteminin bütünlük denetleyicisi (kural 4, 7, 9).

    python tools/check_consistency.py [--root <repo>]

Mekanik olarak doğrulanabilen her şeyi denetler. Hata varsa listeler ve 1 ile çıkar:
 1. Ajanlar: önbilgi, ad = dosya adı, tek ana ajan, settings.json "agent" değeri, zorunlu bölümler.
 2. Alt ajanlarda `Agent` aracı yok ve `tools` tanımlı (koordinasyon yalnızca orkestratörde).
 3. Ajanların "Yazma alanı" bölümü ile write_scopes.json birebir aynı; alanlar ajanlar arasında ayrık.
 4. Ajanların kullandığı skill'ler var; her skill en az bir ajan tarafından kullanılıyor.
 5. Skill'ler: SKILL.md önbilgisi, ad = dizin adı, açıklama ≤ 1536 karakter.
 6. Yetkinlik matrisi: 18 zorunlu yetkinlik var; ajan ve skill var; skill o ajanın listesinde.
 7. Plan (docs/DEVELOPMENT_PLAN.md): aşama alanları, durum, sorumlu ajan, skill, gereksinim,
    bağımlılık (aşama ya da görev); ✋ görevde U-xx; aşama durumu ile görev simgeleri uyumu;
    PROGRESS §1 tablosu ile durum uyumu; ✅ aşamanın §4 kaydı, 🔒 ✅ aşamanın denetim raporu.
 8. Gereksinimler: her R-* plandaki en az bir aşamada ve TRACEABILITY.md'de.
 9. ADR, D-xx, C-xx (DECISIONS), KL-xx (KNOWN_LIMITATIONS) ve U-xx (PROGRESS §2.1) atıfları tanımlı.
10. Belgelerdeki yol atıfları ve göreli bağlantılar gerçek dosyalara işaret ediyor
    (henüz kurulmamış hedef dizinler FUTURE_PREFIXES ile açıkça listelenir).
11. settings.json kanca betikleri var; CLAUDE.md AGENTS.md'yi içe aktarıyor; ikisi de 200 satırın altında.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ORCHESTRATOR = "engineering-orchestrator"
REQUIRED_COMPETENCIES = [
    "Yazılım mimarisi", "Algoritmalar", "Veri yapıları", "İşletim sistemleri",
    "Bilgisayar ağları", "Veritabanları", "Backend", "Frontend", "Mobil", "Yapay zekâ",
    "Makine öğrenmesi", "NLP / RAG", "Bilgisayarlı görü", "Gömülü sistemler",
    "Siber güvenlik", "DevOps", "Performans", "Test",
]  # fmt: skip
SUBAGENT_SECTIONS = [
    "Rol ve sınırlar", "Yazma alanı", "Girdi sözleşmesi", "Prosedür", "Çıktı sözleşmesi",
    "Kabul kriterleri", "Kullandığı skill'ler", "Orkestratöre dön",
    "Yapamayacakları / onay gerektirenler", "Projeye özgü bilgiler", "Örnek",
]  # fmt: skip
ORCH_SECTIONS = [
    "Sorumluluklar (yalnızca sende)", "Yazma alanı", "Girdi sözleşmesi", "Çıktı sözleşmesi (kullanıcıya)",
    "Hata durumunda", "Kullandığı skill'ler", "Yapamayacakları / onay gerektirenler",
    "Proje bağlamı", "Örnek",
]  # fmt: skip
SKILL_SECTIONS = ["Adımlar", "Tuzaklar", "Örnek", "Kontrol listesi"]
CATALOG_ID_RE = re.compile(
    r"^(?:TSRS\d-[A-Z]{3}-\d+[A-Za-z0-9-]*|VSME-[BC]\d+-[A-Za-z0-9-]+|GRI-\d+[A-Za-z0-9-]*)$"
)
PLAN_FIELDS = [
    "Durum", "Sorumlu", "Skill'ler", "Gereksinimler", "Bağımlılık", "Amaç", "Girdi", "Görevler", "Kabul",
    "Doğrulama", "Geri dönüş",
]  # fmt: skip
STAGE_STATES = {"⬜", "🟨", "✅", "✅ (✋ hariç)", "⛔"}
TASK_MARKS = "✅|🟨|⬜|✋|⛔"
# Henüz var olmayan ama belgelerde anılan yollar: (a) tasarımı yazılmış, kurulmamış bileşenler;
# (b) çalışma zamanında üretilen dosyalar (manifest, onay günlüğü, yerel ayar); (c) görev çıktıları.
# Kuruldukça buradan çıkarılır; liste bilinçli ve kısa tutulur.
FUTURE_PREFIXES = (
    "data/gold/", "data/reviews/", ".claude/settings.local.json", "data/catalog/catalog_v1.csv", "reports/experiments/",
    "web/", "db/", "docker/", "docker-compose.yml", "data/processed/",
    "data/raw/pilot/", "services/forecast-service/", "requirements-train.txt",
    "services/report-service/report_service/api/", "services/report-service/report_service/db/",
    "services/report-service/report_service/core/",
    "docs/research/", "docs/labeling/etiket_kilavuzu_v1.md", "data/labels/proposals/pilot_v0.csv", "data/labels/blind/",
    "data/labels/pilot/etiketleyiciler.json",
)  # fmt: skip
PATH_ROOTS = (
    ".claude/", ".agents/", "docs/", "tools/", "services/", "shared/", "data/", "tests/",
    "notebooks/", "pipelines/", "runs/", "reports/", "db/", "docker/", "web/", ".github/",
)  # fmt: skip
ROOT_FILES = {
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    "pyproject.toml",
    "docker-compose.yml",
    "requirements-dev.txt",
}
PLACEHOLDER_CHARS = set("<>*{}$…") | {"YYYY", "NNN", "Sxx", "<N"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checks = 0

    def check(self, ok: bool, msg: str) -> None:
        self.checks += 1
        if not ok:
            self.errors.append(msg)


def frontmatter(text: str) -> tuple[dict, str]:
    """YAML önbilgisi. Geçersiz YAML'da {'__yaml_error__': mesaj} döner (Claude Code da okuyamaz)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    try:
        meta = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as exc:
        meta = {"__yaml_error__": str(exc).splitlines()[0]}
    return meta, text[end + 4 :]


def section(body: str, title: str) -> str | None:
    m = re.search(rf"^## {re.escape(title)}[^\n]*$", body, flags=re.M)
    if not m:
        return None
    rest = body[m.end() :]
    nxt = re.search(r"^## ", rest, flags=re.M)
    return rest[: nxt.start()] if nxt else rest


def bullets(sec: str) -> list[str]:
    return re.findall(r"^- `([^`]+)`", sec, flags=re.M)


def as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return [str(v) for v in value]


def witness(pattern: str) -> str:
    return pattern.replace("**", "w/x").replace("*", "w").replace("?", "w")


def glob_re(pattern: str) -> re.Pattern[str]:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".claude" / "hooks"))
    from guard import glob_to_regex  # tek kaynak: guard ile aynı eşleme

    return glob_to_regex(pattern)


def is_path_ref(tok: str) -> bool:
    if tok in ROOT_FILES:
        return True
    if not tok.startswith(PATH_ROOTS):
        return False
    if any(c in tok for c in PLACEHOLDER_CHARS) or " " in tok:
        return False
    return not re.search(r"\.\.\.|xx|NN|<", tok)


def parse_plan(text: str) -> dict[str, dict]:
    """DEVELOPMENT_PLAN.md → {Sxx: {title, fields, tasks: {Tm: (simge, metin)}}}.

    Aşama başlığı `## Sxx: ad`, alanlar `- **Alan:** değer` (aynı satırda `·` ile birden çok),
    görevler `  - Tm <simge> metin`.
    """
    stages: dict[str, dict] = {}
    parts = re.split(r"^## (S\d{2}): (.*)$", text, flags=re.M)
    for i in range(1, len(parts), 3):
        sid, title, block = parts[i], parts[i + 1], parts[i + 2]
        block = re.split(r"^(?:## |---)", block, maxsplit=1, flags=re.M)[0]
        fields: dict[str, str] = {}
        for m in re.finditer(r"\*\*([^*]+):\*\*\s*([^·\n]*)", block):
            fields[m.group(1).strip()] = m.group(2).strip()
        tasks = {
            m.group(1): (m.group(2), m.group(3))
            for m in re.finditer(rf"^\s+- (T\d+) ({TASK_MARKS}) (.*)$", block, flags=re.M)
        }
        stages[sid] = {"title": title, "fields": fields, "tasks": tasks}
    return stages


def run(root: Path) -> Report:
    r = Report()
    agents_dir, skills_dir = root / ".claude" / "agents", root / ".claude" / "skills"
    scopes = json.loads((root / ".claude" / "hooks" / "write_scopes.json").read_text())
    settings = json.loads((root / ".claude" / "settings.json").read_text())

    # 1–4: ajanlar
    agents: dict[str, dict] = {}
    for f in sorted(agents_dir.glob("*.md")):
        meta, body = frontmatter(f.read_text(encoding="utf-8"))
        r.check("__yaml_error__" not in meta, f"{f}: geçersiz YAML önbilgisi: {meta.get('__yaml_error__')}")
        name = meta.get("name")
        r.check(name == f.stem, f"{f}: name={name!r} dosya adıyla ({f.stem}) aynı değil")
        r.check(bool(meta.get("description")), f"{f}: description boş")
        agents[f.stem] = {"meta": meta, "body": body}
    r.check(ORCHESTRATOR in agents, f"ana ajan {ORCHESTRATOR} yok")
    r.check(settings.get("agent") == ORCHESTRATOR, "settings.json 'agent' ana ajan değil")
    depth = settings.get("env", {}).get("CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH")
    r.check(depth == "1", "settings.json env CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1 değil")

    agent_skills: dict[str, list[str]] = {}
    for name, a in agents.items():
        body, meta = a["body"], a["meta"]
        required = ORCH_SECTIONS if name == ORCHESTRATOR else SUBAGENT_SECTIONS
        for title in required:
            r.check(section(body, title) is not None, f"{name}: '## {title}' bölümü yok")
        if name != ORCHESTRATOR:
            tools = as_list(meta.get("tools"))
            r.check(bool(tools), f"{name}: tools tanımlı değil (her şeyi devralır)")
            r.check(not ({"Agent", "Task"} & set(tools)), f"{name}: alt ajan Agent aracına sahip")
            if not scopes["agents"].get(name):
                writers = {"Write", "Edit", "MultiEdit", "NotebookEdit", "Bash"} & set(tools)
                r.check(not writers, f"{name}: salt-okunur ama yazabilen araçları var {writers}")
        sec = section(body, "Yazma alanı") or ""
        declared = bullets(sec)
        expected = scopes["agents"].get(name)
        r.check(expected is not None, f"{name}: write_scopes.json'da yok")
        if expected is not None:
            r.check(
                sorted(declared) == sorted(expected),
                f"{name}: Yazma alanı bölümü {sorted(declared)} ≠ write_scopes.json {sorted(expected)}",
            )
        agent_skills[name] = bullets(section(body, "Kullandığı skill'ler") or "")
    for name in scopes["agents"]:
        r.check(name in agents, f"write_scopes.json'daki {name} için ajan dosyası yok")

    names = [n for n in scopes["agents"] if n != ORCHESTRATOR]
    for a in names:
        for b in names:
            if a >= b:
                continue
            for pa in scopes["agents"][a]:
                for pb in scopes["agents"][b]:
                    clash = glob_re(pb).match(witness(pa)) or glob_re(pa).match(witness(pb))
                    r.check(not clash, f"yazma alanı çakışması: {a}:{pa} ↔ {b}:{pb}")

    # 5: skill'ler
    skills: set[str] = set()
    for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        f = d / "SKILL.md"
        r.check(f.exists(), f"{d}: SKILL.md yok")
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        r.check(text.startswith("---\n"), f"{f}: önbilgi ilk satırda başlamıyor")
        meta, _ = frontmatter(text)
        r.check("__yaml_error__" not in meta, f"{f}: geçersiz YAML önbilgisi: {meta.get('__yaml_error__')}")
        r.check(meta.get("name") == d.name, f"{f}: name={meta.get('name')!r} ≠ {d.name}")
        desc = str(meta.get("description") or "")
        r.check(0 < len(desc) <= 1536, f"{f}: description boş ya da 1536 karakterden uzun")
        _, sbody = frontmatter(text)
        for title in SKILL_SECTIONS:
            r.check(section(sbody, title) is not None, f"{f}: '## {title}' bölümü yok")
        for tok in set(re.findall(r"`((?:scripts|references|assets)/[^`\s]+)`", sbody)):
            r.check((d / tok).exists(), f"{f}: skill içi dosya yok `{tok}`")
        skill_tests = (root / "tests" / "skills").glob("test_*.py")
        tested = "\n".join(t.read_text(encoding="utf-8") for t in skill_tests)
        for script in sorted((d / "scripts").glob("*.py")):
            needle = f'load("{d.name}", "{script.stem}")'
            r.check(
                needle in tested, f"{d.name}/scripts/{script.name}: tests/skills altında testi yok ({needle})"
            )
        skills.add(d.name)
    used = {s for lst in agent_skills.values() for s in lst}
    for a, lst in agent_skills.items():
        for s in lst:
            r.check(s in skills, f"{a}: olmayan skill '{s}'")
    for s in sorted(skills - used):
        r.errors.append(f"skill '{s}' hiçbir ajanın listesinde değil (sahipsiz)")

    # 6: yetkinlik matrisi
    matrix = (root / "docs" / "COMPETENCY_MATRIX.md").read_text(encoding="utf-8")
    found = set()
    for line in matrix.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        idx = next((i for i, c in enumerate(cells) if re.fullmatch(r"`[a-z-]+`", c)), None)
        if idx is None or idx + 1 >= len(cells):
            continue
        comp = cells[idx - 1]
        agent = cells[idx].strip("`")
        msk = re.findall(r"`([a-z0-9-]+)`", cells[idx + 1])
        found.add(comp)
        r.check(agent in agents, f"matris '{comp}': ajan {agent} yok")
        for s in msk:
            r.check(s in skills, f"matris '{comp}': skill {s} yok")
            r.check(s in agent_skills.get(agent, []), f"matris '{comp}': {s}, {agent} listesinde yok")
    for comp in REQUIRED_COMPETENCIES:
        r.check(comp in found, f"matriste zorunlu yetkinlik yok: {comp}")

    # 7–8: plan, PROGRESS ve gereksinimler
    req_text = (root / "docs" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    reqs = set(re.findall(r"^\|\s*(R-[A-Z]{3}-\d{2})\s*\|", req_text, flags=re.M))
    r.check(bool(reqs), "REQUIREMENTS.md'de R-* tanımı yok")
    trace = (root / "docs" / "TRACEABILITY.md").read_text(encoding="utf-8")
    traced = set(re.findall(r"^\|\s*(R-[A-Z]{3}-\d{2})\s*\|", trace, flags=re.M))
    plan_text = (root / "docs" / "DEVELOPMENT_PLAN.md").read_text(encoding="utf-8")
    progress = (root / "docs" / "PROGRESS.md").read_text(encoding="utf-8")
    stages = parse_plan(plan_text)
    r.check(bool(stages), "DEVELOPMENT_PLAN.md'de aşama yok")
    all_tasks = {f"{sid}.{tid}" for sid, s in stages.items() for tid in s["tasks"]}
    users = set(re.findall(r"^\|\s*(U-\d{2})\s*\|", progress, flags=re.M))
    status_sec = section(progress, "1. Aşama durumu") or ""
    status_rows = dict(re.findall(r"^\|\s*(S\d{2})\s*\|[^|]*\|\s*([^|]*?)\s*\|", status_sec, flags=re.M))
    evidence = section(progress, "4. Kanıt günlüğü") or ""
    audits = root / "docs" / "audits"
    for sid, s in stages.items():
        for field in PLAN_FIELDS:
            r.check(field in s["fields"], f"plan {sid}: '{field}' alanı yok")
        durum = s["fields"].get("Durum", "")
        r.check(durum in STAGE_STATES, f"plan {sid}: geçersiz durum {durum!r}")
        sorumlu = re.findall(r"`([a-z-]+)`", s["fields"].get("Sorumlu", ""))
        r.check(
            bool(sorumlu) and all(a in agents for a in sorumlu),
            f"plan {sid}: sorumlu ajan geçersiz {sorumlu}",
        )
        for sk in re.findall(r"`([a-z-]+)`", s["fields"].get("Skill'ler", "")):
            r.check(sk in skills, f"plan {sid}: olmayan skill {sk}")
        sreqs = re.findall(r"R-[A-Z]{3}-\d{2}", s["fields"].get("Gereksinimler", ""))
        for q in sreqs:
            r.check(q in reqs, f"plan {sid}: tanımsız gereksinim {q}")
        for dep in re.findall(r"S\d{2}(?:\.T\d+)?", s["fields"].get("Bağımlılık", "")):
            known = dep in stages if "." not in dep else dep in all_tasks
            r.check(known, f"plan {sid}: bilinmeyen bağımlılık {dep}")
        r.check(bool(s["tasks"]), f"plan {sid}: görev yok")
        marks = [m for m, _ in s["tasks"].values()]
        for tid, (mark, text) in s["tasks"].items():
            if mark == "✋":
                r.check(bool(re.search(r"U-\d{2}", text)), f"plan {sid}.{tid}: ✋ görevde U-xx yok")
        if durum == "✅":
            r.check(all(m == "✅" for m in marks), f"plan {sid}: aşama ✅ ama tamamlanmamış görev var")
        elif durum == "✅ (✋ hariç)":
            r.check(
                all(m in ("✅", "✋") for m in marks),
                f"plan {sid}: '✅ (✋ hariç)' ama ✋ dışında açık görev var",
            )
        elif durum == "⬜":
            r.check(
                not ({"✅", "🟨"} & set(marks)), f"plan {sid}: aşama ⬜ ama başlamış görev var (🟨 olmalı)"
            )
        elif durum == "🟨":
            r.check(any(m != "✅" for m in marks), f"plan {sid}: bütün görevler ✅ ama aşama 🟨")
        row = status_rows.get(sid)
        r.check(row is not None, f"PROGRESS §1 tablosunda {sid} yok")
        if row is not None:
            r.check(row.startswith(durum), f"{sid}: PROGRESS durumu {row!r} ≠ plan {durum!r}")
        if durum.startswith("✅"):
            r.check(
                bool(re.search(rf"^### .*\b{sid}\b", evidence, flags=re.M)),
                f"{sid}: ✅ ama PROGRESS §4'te kaydı yok",
            )
            if "🔒" in s["title"]:
                r.check((audits / f"{sid}.md").exists(), f"{sid}: 🔒 aşama ✅ ama docs/audits/{sid}.md yok")
    for sid in status_rows:
        r.check(sid in stages, f"PROGRESS §1'deki {sid} planda yok")
    plan_reqs = {
        q
        for s in stages.values()
        for q in re.findall(r"R-[A-Z]{3}-\d{2}", s["fields"].get("Gereksinimler", ""))
    }
    for q in sorted(reqs):
        r.check(q in plan_reqs, f"{q} plandaki hiçbir aşamada yok")
        r.check(q in traced, f"{q} TRACEABILITY.md'de yok")
    for sid in set(re.findall(r"\bS\d{2}\b", trace)):
        r.check(sid in stages, f"TRACEABILITY.md: planda olmayan aşama {sid}")
    limits = (root / "docs" / "KNOWN_LIMITATIONS.md").read_text(encoding="utf-8")
    kls = set(re.findall(r"^\|\s*(KL-\d{2})\s*\|", limits, flags=re.M))
    # 9–10: ADR ve yol atıfları
    decisions = (root / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    adrs = set(re.findall(r"^## (ADR-\d{3})", decisions, flags=re.M))
    open_ids = set(re.findall(r"^\|\s*([DC]-\d{2})\s*\|", decisions, flags=re.M))
    catalogs = sorted((root / "data" / "catalog").glob("catalog_v*.csv"))
    catalog_ids = set()
    for c in catalogs:
        catalog_ids |= {ln.split(",", 1)[0] for ln in c.read_text(encoding="utf-8").splitlines()[1:] if ln}
    scan = [root / "CLAUDE.md", root / "README.md", root / "AGENTS.md"]
    scan += sorted((root / ".claude").rglob("*.md")) + sorted((root / ".agents").rglob("*.md"))
    scan += sorted((root / "docs").glob("*.md")) + sorted((root / "docs" / "kullanim").glob("*.md"))
    scan += sorted((root / "docs" / "audits").glob("*.md"))
    for f in scan:
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(root)
        for adr in set(re.findall(r"ADR-\d{3}", text)):
            r.check(adr in adrs, f"{rel}: tanımsız {adr}")
        for ref in set(re.findall(r"\b([DC]-\d{2})\b", text)):
            r.check(ref in open_ids, f"{rel}: tanımsız {ref}")
        for ref in set(re.findall(r"\b(KL-\d{2})\b", text)):
            r.check(ref in kls, f"{rel}: tanımsız {ref}")
        for ref in set(re.findall(r"\b(U-\d{2})\b", text)):
            r.check(ref in users, f"{rel}: tanımsız {ref} (PROGRESS §2.1)")
        for tok in set(re.findall(r"`([^`\n]+)`", text)):
            tok = tok.split("::")[0].split("#")[0].rstrip("/.,:;")
            if (
                not is_path_ref(tok)
                or (tok + "/").startswith(FUTURE_PREFIXES)
                or tok.startswith(FUTURE_PREFIXES)
            ):
                continue
            r.check((root / tok).exists(), f"{rel}: var olmayan yol `{tok}`")
        for tok in set(re.findall(r"`([^`\n]+)`", text)):
            if CATALOG_ID_RE.match(tok) and catalog_ids:
                r.check(tok in catalog_ids, f"{rel}: katalogda olmayan madde `{tok}`")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if link.startswith(("http", "#", "mailto:")):
                continue
            target = (f.parent / link.split("#")[0]).resolve()
            r.check(target.exists(), f"{rel}: kırık bağlantı ({link})")

    # 11: settings ve CLAUDE.md
    for ev in settings.get("hooks", {}).values():
        for group in ev:
            for h in group.get("hooks", []):
                for p in re.findall(r"\$CLAUDE_PROJECT_DIR/([^\"\s]+)", h.get("command", "")):
                    r.check((root / p).exists(), f"settings.json: kanca betiği yok {p}")
    for name in ("CLAUDE.md", "AGENTS.md"):
        lines = (root / name).read_text(encoding="utf-8").count("\n")
        r.check(lines < 200, f"{name} {lines} satır (≥ 200)")
    r.check(
        "@AGENTS.md" in (root / "CLAUDE.md").read_text(encoding="utf-8"),
        "CLAUDE.md AGENTS.md'yi içe aktarmıyor",
    )
    return r


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = ap.parse_args(argv)
    rep = run(args.root)
    for e in rep.errors:
        print("HATA:", e)
    print(f"{rep.checks} kontrol, {len(rep.errors)} hata")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
