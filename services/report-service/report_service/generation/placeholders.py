"""Yer tutuculu sayı üretimi (R-GEN-03, ADR-004, bulgu B10).

Dil modeli taslakta hiçbir sayıyı kendisi yazmaz. Her sayısal değer için şu yer tutucuyu üretir:

    {{KPI:<kpi>:<yil>:<gerceklesmis|tahmin>}}

Bu modül:
1. `validate_draft`: taslağı doldurmadan önce denetler.
   - Serbest metinde yıl dışında sayı olmamalı.
   - Her yer tutucunun kaydı bulunmalı ve türü kayıtla aynı olmalı.
   - Tahmin içeren cümle öngörü kipinde olmalı.
2. `render`: değeri, birimi ve tahmin etiketini deterministik olarak yerleştirir.
   Her yerleşimi bir iddia (claim) kaydı olarak döndürür; bunlar `draft_claim` tablosuna gider.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from report_service.verify.numbers import extract_numbers, format_tr
from report_service.verify.tense import check_sentence

PLACEHOLDER = re.compile(r"\{\{KPI:(?P<kpi>[a-z0-9_]+):(?P<yil>\d{4}):(?P<tur>gerceklesmis|tahmin)\}\}")
CITATION = re.compile(r"\[\d+(?:\s*,\s*\d+)*\]")
# Değer olmayan, ad parçası sayılar: "Kapsam 1", "TSRS 2", "GRI 305", "ISO 14001", "madde 29(a)"
IDENTIFIER = re.compile(
    r"\b(?:Kapsam|Scope|TSRS|GRI|ESRS|ISO|SKA|SDG|madde|paragraf)\s*-?\s*\d+[a-z]?(?:\([a-z0-9]+\))*",
    flags=re.IGNORECASE,
)
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class Record:
    """Şirket KPI kaydı veya tahmin kaydı (shared/contracts/forecast_record.schema.json)."""

    kpi: str
    yil: int
    deger: float
    birim: str
    veri_turu: str  # "gerceklesmis" | "tahmin"
    kaynak: str
    model_id: str | None = None
    senaryo_id: str | None = None
    guven_araligi: tuple[float, float] | None = None


@dataclass
class RenderResult:
    text: str
    claims: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _index(records: list[Record]) -> dict[tuple[str, int], Record]:
    return {(r.kpi, r.yil): r for r in records}


def check_free_text(draft: str) -> list[str]:
    """Yer tutucu, atıf ve ad parçası sayılar çıkarıldıktan sonra yıl dışı sayı varsa hata."""
    stripped = IDENTIFIER.sub(" ", CITATION.sub(" ", PLACEHOLDER.sub(" ", draft)))
    return [
        f"serbest metinde sayı: {q.raw!r} (sayılar yalnızca yer tutucuyla yazılır)"
        for q in extract_numbers(stripped)
        if not q.is_year
    ]


def validate_draft(draft: str, records: list[Record]) -> list[str]:
    errors = check_free_text(draft)
    idx = _index(records)
    for m in PLACEHOLDER.finditer(draft):
        rec = idx.get((m["kpi"], int(m["yil"])))
        if rec is None:
            errors.append(f"kaynak kaydı yok: {m.group(0)} (veri eksik denmeli, uydurulmamalı)")
        elif rec.veri_turu != m["tur"]:
            errors.append(f"tür uyuşmazlığı: {m.group(0)} ama kayıt '{rec.veri_turu}'")
    for sentence in SENTENCE_END.split(draft):
        kinds = {m["tur"] for m in PLACEHOLDER.finditer(sentence)}
        for kind in sorted(kinds):
            problem = check_sentence(PLACEHOLDER.sub(" ", sentence), kind)
            if problem:
                errors.append(f"kip hatası: {problem}: {sentence.strip()!r}")
    return errors


def _format(rec: Record) -> str:
    decimals = 0 if float(rec.deger).is_integer() else 1
    text = f"{format_tr(rec.deger, decimals)} {rec.birim}"
    if rec.veri_turu == "tahmin":
        text += " (tahmin)"
    return text


def render(draft: str, records: list[Record]) -> RenderResult:
    """Taslağı doğrular; hata yoksa yer tutucuları değerlerle doldurur."""
    errors = validate_draft(draft, records)
    if errors:
        return RenderResult(text=draft, errors=errors)
    idx = _index(records)
    claims: list[dict] = []

    def _sub(m: re.Match[str]) -> str:
        rec = idx[(m["kpi"], int(m["yil"]))]
        claims.append(
            {
                "yer_tutucu": m.group(0),
                "kpi": rec.kpi,
                "yil": rec.yil,
                "deger": rec.deger,
                "birim": rec.birim,
                "veri_turu": rec.veri_turu,
                "kaynak": rec.kaynak,
                "model_id": rec.model_id,
                "senaryo_id": rec.senaryo_id,
            }
        )
        return _format(rec)

    return RenderResult(text=PLACEHOLDER.sub(_sub, draft), claims=claims)
