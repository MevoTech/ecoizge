"""Onay arayüzünün UI'dan bağımsız mantığı (R-HIL-01). Streamlit olmadan test edilir.

Akış: data/labels/proposals/*.csv → insan kararı → data/labels/reviewed/<aynı ad>.csv
      + data/reviews/reviews.jsonl (yalnızca ekleme; kayıt silinmez).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from review_ui.ortak import atomik_csv_yaz, csv_oku

LABEL_HEADER = [
    "etiket_id", "tur", "rapor_id", "sirket", "yil", "paragraf_id", "sayfa", "bolum_basligi",
    "metin", "madde_id", "karsilama", "guven", "gerekce", "etiketleyen", "kaynak", "tarih",
]  # fmt: skip
DECISIONS = {"onayla", "duzelt", "reddet"}
KARSILAMA_PARAGRAF = ["2", "1", "U", "NONE"]


@dataclass(frozen=True)
class Paths:
    data: Path

    @property
    def proposals(self) -> Path:
        return self.data / "labels" / "proposals"

    @property
    def reviewed(self) -> Path:
        return self.data / "labels" / "reviewed"

    @property
    def log(self) -> Path:
        return self.data / "reviews" / "reviews.jsonl"

    @property
    def catalog_dir(self) -> Path:
        return self.data / "catalog"


def read_rows(path: Path) -> list[dict[str, str]]:
    return csv_oku(path)


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    atomik_csv_yaz(path, LABEL_HEADER, rows)  # yarım dosya kalmasın; kilitli dosyada anlaşılır hata


def proposal_files(paths: Paths) -> list[Path]:
    return sorted(paths.proposals.glob("*.csv"))


def decided_ids(paths: Paths, proposal: Path) -> set[str]:
    """Bu öneri dosyası için kararı verilmiş etiket kimlikleri (reddedilenler dahil)."""
    ids: set[str] = set()
    if paths.log.exists():
        for line in paths.log.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec.get("dosya") == proposal.name:
                ids.add(rec["etiket_id"])
    return ids


def pending(paths: Paths, proposal: Path) -> list[dict[str, str]]:
    done = decided_ids(paths, proposal)
    return [r for r in read_rows(proposal) if r["etiket_id"] not in done]


def catalog_lookup(paths: Paths) -> dict[str, dict[str, str]]:
    files = sorted(paths.catalog_dir.glob("catalog_v*.csv"))
    return {r["madde_id"]: r for r in read_rows(files[-1])} if files else {}


def decide(
    paths: Paths,
    proposal: Path,
    row: dict[str, str],
    decision: str,
    reviewer: str,
    new_karsilama: str | None = None,
    gerekce: str = "",
    today: date | None = None,
) -> dict:
    """Kararı uygular: reviewed dosyasını günceller, günlüğe bir satır ekler, kaydı döndürür."""
    if decision not in DECISIONS:
        raise ValueError(f"karar {decision!r} geçersiz")
    if not reviewer.strip():
        raise ValueError("inceleyen adı zorunlu")
    if decision == "duzelt" and new_karsilama not in KARSILAMA_PARAGRAF:
        raise ValueError("düzeltmede yeni karşılama değeri zorunlu")
    if decision in {"duzelt", "reddet"} and not gerekce.strip():
        raise ValueError("düzeltme ve redde gerekçe zorunlu")
    today = today or date.today()

    out_path = paths.reviewed / proposal.name
    reviewed = [r for r in read_rows(out_path) if r["etiket_id"] != row["etiket_id"]]
    new_row = None
    if decision != "reddet":
        new_row = dict(row)
        new_row["etiketleyen"] = reviewer
        new_row["tarih"] = today.isoformat()
        if decision == "onayla":
            new_row["kaynak"] = "insan_onayli"
        else:
            new_row["kaynak"] = "insan"
            new_row["karsilama"] = new_karsilama or ""
            if new_karsilama == "NONE":
                new_row["madde_id"] = "NONE"
            new_row["gerekce"] = gerekce
        reviewed.append(new_row)
    write_rows(out_path, reviewed)

    record = {
        "zaman": datetime.now(UTC).isoformat(timespec="seconds"),
        "inceleyen": reviewer,
        "dosya": proposal.name,
        "etiket_id": row["etiket_id"],
        "karar": decision,
        "eski": {"madde_id": row["madde_id"], "karsilama": row["karsilama"]},
        "yeni": None
        if new_row is None
        else {"madde_id": new_row["madde_id"], "karsilama": new_row["karsilama"]},
        "gerekce": gerekce,
    }
    paths.log.parent.mkdir(parents=True, exist_ok=True)
    with paths.log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
