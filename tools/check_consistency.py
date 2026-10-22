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
 7. Görevler: önbilgi alanları, durum değerleri, sorumlu ajan, skill, gereksinim, bağımlılık;
    tasks/README.md tablosu ile durum uyumu.
 8. Gereksinimler: her R-* en az bir görevde ve TRACEABILITY.md'de.
 9. ADR atıfları DECISIONS.md'de tanımlı.
10. Belgelerdeki yol atıfları ve göreli bağlantılar gerçek dosyalara işaret ediyor
    (henüz kurulmamış hedef dizinler FUTURE_PREFIXES ile açıkça listelenir).
11. settings.json kanca betikleri var; CLAUDE.md 200 satırın altında.
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
    "Yapamayacakları / onay gerektirenler",
]  # fmt: skip
ORCH_SECTIONS = [
    "Sorumluluklar (yalnızca sende)", "Yazma alanı", "Girdi sözleşmesi", "Çıktı sözleşmesi (kullanıcıya)",
    "Hata durumunda", "Kullandığı skill'ler", "Yapamayacakları / onay gerektirenler",
]  # fmt: skip
TASK_FIELDS = [
    "id", "baslik", "faz", "durum", "sorumlu", "skills", "gereksinimler", "bagimlilik", "insan_onayi",
]  # fmt: skip
TASK_STATES = {"bekliyor", "devam", "tamam", "engelli"}
# Henüz var olmayan ama belgelerde anılan yollar: (a) tasarımı yazılmış, kurulmamış bileşenler;
# (b) çalışma zamanında üretilen dosyalar (manifest, onay günlüğü, yerel ayar); (c) görev çıktıları.
# Kuruldukça buradan çıkarılır; liste bilinçli ve kısa tutulur.
FUTURE_PREFIXES = (
    "data/gold/", "data/reviews/", ".claude/settings.local.json", "data/catalog/catalog_v1.csv",
    "web/", "db/", "docker/", "docker-compose.yml", "pipelines/", "data/processed/",
    "data/raw/pilot/", "services/forecast-service/", "requirements-train.txt",
    "services/report-service/report_service/api/", "services/report-service/report_service/db/",
    "services/report-service/report_service/core/", "services/report-service/report_service/nlp/",
)  # fmt: skip
PATH_ROOTS = (
    ".claude/", "docs/", "tasks/", "tools/", "services/", "shared/", "data/", "tests/",
    "notebooks/", "pipelines/", "runs/", "reports/", "db/", "docker/", "web/", ".github/",
)  # fmt: skip
ROOT_FILES = {"CLAUDE.md", "README.md", "pyproject.toml", "docker-compose.yml", "requirements-dev.txt"}
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
    m = re.search(rf"^## {re.escape(title)}\s*$", body, flags=re.M)
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
        r.check(bool(msk), f"matris '{comp}': skill yok")
        for s in msk:
            r.check(s in skills, f"matris '{comp}': skill {s} yok")
            r.check(s in agent_skills.get(agent, []), f"matris '{comp}': {s}, {agent} listesinde yok")
    for comp in REQUIRED_COMPETENCIES:
        r.check(comp in found, f"matriste zorunlu yetkinlik yok: {comp}")

    # 7–8: gereksinimler ve görevler
    req_text = (root / "docs" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    reqs = set(re.findall(r"^\|\s*(R-[A-Z]{3}-\d{2})\s*\|", req_text, flags=re.M))
    r.check(bool(reqs), "REQUIREMENTS.md'de R-* tanımı yok")
    trace = (root / "docs" / "TRACEABILITY.md").read_text(encoding="utf-8")
    traced = set(re.findall(r"^\|\s*(R-[A-Z]{3}-\d{2})\s*\|", trace, flags=re.M))
    tasks: dict[str, dict] = {}
    for f in sorted((root / "tasks").glob("S[0-9][0-9]-*.md")):
        meta, body = frontmatter(f.read_text(encoding="utf-8"))
        r.check("__yaml_error__" not in meta, f"{f.name}: geçersiz YAML önbilgisi")
        for k in TASK_FIELDS:
            r.check(k in meta, f"{f.name}: önbilgide '{k}' yok")
        tid = str(meta.get("id", ""))
        r.check(f.name.startswith(tid + "-"), f"{f.name}: id={tid} dosya adıyla uyumsuz")
        r.check(meta.get("durum") in TASK_STATES, f"{f.name}: durum={meta.get('durum')!r} geçersiz")
        r.check(meta.get("sorumlu") in agents, f"{f.name}: sorumlu {meta.get('sorumlu')} ajan değil")
        for s in as_list(meta.get("skills")):
            r.check(s in skills, f"{f.name}: olmayan skill {s}")
        for q in as_list(meta.get("gereksinimler")):
            r.check(q in reqs, f"{f.name}: tanımsız gereksinim {q}")
        for title in ("Kabul kriterleri", "Test komutu", "Kanıt", "Hata durumunda"):
            r.check(section(body, title) is not None, f"{f.name}: '## {title}' bölümü yok")
        tasks[tid] = meta
    for tid, meta in tasks.items():
        for dep in as_list(meta.get("bagimlilik")):
            r.check(dep in tasks, f"{tid}: bilinmeyen bağımlılık {dep}")
    idx_text = (root / "tasks" / "README.md").read_text(encoding="utf-8")
    for tid, meta in tasks.items():
        m = re.search(rf"^\|\s*\[{tid}\]\([^)]+\)\s*\|[^|]*\|[^|]*\|\s*([a-z]+)\s*\|", idx_text, re.M)
        r.check(bool(m), f"tasks/README.md tablosunda {tid} yok")
        if m:
            r.check(
                m.group(1) == meta.get("durum"), f"{tid}: README durumu {m.group(1)} ≠ {meta.get('durum')}"
            )
    task_reqs = {q for m in tasks.values() for q in as_list(m.get("gereksinimler"))}
    for q in sorted(reqs):
        r.check(q in task_reqs, f"{q} hiçbir görevde yok")
        r.check(q in traced, f"{q} TRACEABILITY.md'de yok")

    # 9–10: ADR ve yol atıfları
    decisions = (root / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    adrs = set(re.findall(r"^## (ADR-\d{3})", decisions, flags=re.M))
    scan = [root / "CLAUDE.md", root / "README.md"]
    scan += sorted((root / ".claude").rglob("*.md"))
    scan += sorted((root / "docs").glob("*.md")) + sorted((root / "tasks").glob("*.md"))
    for f in scan:
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(root)
        for adr in set(re.findall(r"ADR-\d{3}", text)):
            r.check(adr in adrs, f"{rel}: tanımsız {adr}")
        for tok in set(re.findall(r"`([^`\n]+)`", text)):
            tok = tok.split("::")[0].split("#")[0].rstrip("/.,:;")
            if (
                not is_path_ref(tok)
                or (tok + "/").startswith(FUTURE_PREFIXES)
                or tok.startswith(FUTURE_PREFIXES)
            ):
                continue
            r.check((root / tok).exists(), f"{rel}: var olmayan yol `{tok}`")
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
    lines = (root / "CLAUDE.md").read_text(encoding="utf-8").count("\n")
    r.check(lines < 200, f"CLAUDE.md {lines} satır (≥ 200)")
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
