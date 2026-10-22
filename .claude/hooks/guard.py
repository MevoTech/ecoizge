#!/usr/bin/env python3
"""PreToolUse koruma kancası (R-SEC-02, ADR-003).

Claude Code her araç çağrısından önce bu betiği çalıştırır ve çağrıyı JSON olarak stdin'den verir.
Çıkış kodu 2 aracı engeller; stderr Claude'a gerekçe olarak gösterilir. Çıkış 0 normal izin akışına bırakır.

Kurallar `.claude/hooks/write_scopes.json` dosyasından okunur (tek kaynak):
- Write/Edit/MultiEdit/NotebookEdit: korumalı yol → herkes için engel; ajanın yazma alanı dışı → engel.
- Read/Grep/Glob: okuma-korumalı yol → herkes için engel; ajana özel okuma yasağı → engel.
- Bash: yıkıcı kalıp veya korumalı yol geçen komut → engel.
Girdi çözümlenemezse ya da kurallar okunamazsa güvenli tarafta kalır ve engeller.
"""

from __future__ import annotations

import json
import os
import re
import sys

DEFAULT_AGENT = "engineering-orchestrator"
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}

BASH_DESTRUCTIVE = [
    (r"\brm\s+(-\w*\s+)*-\w*(r\w*f|f\w*r)\b", "rm -rf"),
    (r"\bgit\s+push\b.*(--force\b|--force-with-lease\b|\s-f\b)", "git push --force"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard"),
    (r"\bgit\s+clean\s+-\w*f", "git clean -f"),
    (r"gold_manifest\.py\s+freeze", "altın küme dondurma (yalnızca insan)"),
    (r"\b(curl|wget)\b[^|;&]*\|\s*(ba|z)?sh\b", "indirileni doğrudan çalıştırma"),
]
BASH_PROTECTED = [
    (r"data/gold\b", "data/gold"),
    (r"data/labels/reviewed\b", "data/labels/reviewed"),
    (r"data/reviews\b", "data/reviews"),
    (r"data/raw/pilot\b", "data/raw/pilot"),
    (r"(^|[\s'\"=:/<>(])\.env(?![\w.-])", ".env"),
    (r"(^|[\s'\"=:/<>(])secrets/", "secrets/"),
    (r"\.key(?![\w.-])", "*.key"),
]


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """`**` her derinliği, `*` tek yol parçasını, `?` tek karakteri eşler."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_any(rel: str, patterns: list[str]) -> bool:
    return any(glob_to_regex(p).match(rel) for p in patterns)


def block(reason: str) -> None:
    sys.stderr.write(f"[guard] ENGELLENDİ: {reason}\n")
    sys.exit(2)


def project_rel(path: str, project: str) -> str | None:
    """Proje köküne göreli POSIX yol; proje dışındaysa None."""
    if not path:
        return ""
    absolute = path if os.path.isabs(path) else os.path.join(project, path)
    real = os.path.realpath(absolute)
    root = os.path.realpath(project)
    if real != root and not real.startswith(root + os.sep):
        return None
    return os.path.relpath(real, root).replace(os.sep, "/")


def load_rules(project: str) -> dict:
    path = os.path.join(project, ".claude", "hooks", "write_scopes.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check(event: dict, project: str, rules: dict) -> None:
    tool = event.get("tool_name", "")
    params = event.get("tool_input") or {}
    agent = event.get("agent_type") or DEFAULT_AGENT

    if tool in WRITE_TOOLS:
        path = params.get("file_path") or params.get("notebook_path") or ""
        rel = project_rel(path, project)
        if rel is None:
            if agent != DEFAULT_AGENT:
                block(f"'{agent}' proje dışına yazamaz: {path}")
            return
        if matches_any(rel, rules["protected"]):
            block(f"korumalı yol, yalnızca insan değiştirir: {rel}")
        scopes = rules["agents"].get(agent)
        if scopes is None:
            block(f"tanımsız ajan '{agent}' için yazma kapalı: {rel}")
        if not matches_any(rel, scopes):
            allowed = ", ".join(scopes) if scopes else "yok (salt-okunur)"
            block(f"'{agent}' yazma alanı dışında: {rel}. İzinli: {allowed}")
        return

    if tool in READ_TOOLS:
        candidates = [params.get("file_path"), params.get("path")]
        if tool == "Glob" and params.get("pattern"):
            base = params.get("path") or ""
            candidates.append(os.path.join(base, params["pattern"]) if base else params["pattern"])
        denied = rules.get("read_denied", {}).get(agent, [])
        for cand in candidates:
            if not cand:
                continue
            rel = project_rel(cand, project)
            if rel is None:
                continue
            if matches_any(rel, rules.get("read_protected", [])):
                block(f"okuma-korumalı yol: {rel}")
            if denied and matches_any(rel, denied):
                block(f"'{agent}' bu yolu okuyamaz: {rel}")
        return

    if tool == "Bash":
        command = params.get("command", "")
        for pattern, label in BASH_DESTRUCTIVE:
            if re.search(pattern, command):
                block(f"yıkıcı komut ({label}); kullanıcı kendisi çalıştırmalı")
        for pattern, label in BASH_PROTECTED:
            if re.search(pattern, command):
                block(f"komut korumalı yola dokunuyor ({label})")


def main() -> None:
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        block("kanca girdisi çözümlenemedi (güvenli tarafta kalındı)")
    project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    try:
        rules = load_rules(project)
    except (OSError, json.JSONDecodeError) as exc:
        block(f"write_scopes.json okunamadı: {exc}")
    check(event, project, rules)
    sys.exit(0)


if __name__ == "__main__":
    main()
