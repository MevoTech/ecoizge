"""Madde düzeyi karar: paragraf etiketlerinden ya da skorlardan unsur kapsamasıyla (R-GAP-03, ADR-008).

Neden `max` değil: S-15'teki `C(r) = max_p Sim·s_spec` tek paragrafa bakar. "Kapsam 1, 2 ve 3
emisyonları" gibi çok unsurlu bir madde, unsurlar farklı paragraflara dağıldığında hiçbir zaman
"Tam" çıkmaz. Burada madde, alt unsurlarının (katalogda `-a`, `-b` … ile bölünmüş) her biri ayrı
değerlendirilip toplanarak karara bağlanır.

Düzeyler: "2" tam, "1" kısmi, "0" eksik, "U" uygulanamaz.
Paragraf etiketi sırası: NONE < 1 < 2; U ayrı tutulur (yalnızca 1/2 yoksa geçerlidir).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

_RANK = {"NONE": 0, "1": 1, "2": 2}


@dataclass(frozen=True)
class Decision:
    madde_id: str
    level: str  # "2" | "1" | "0" | "U"
    eksik_unsurlar: tuple[str, ...] = ()
    kismi_unsurlar: tuple[str, ...] = ()


def best_level(labels: Iterable[str]) -> str:
    """Bir madde için tüm paragraf etiketlerinden en iyi düzey ("0" = hiç karşılanmamış)."""
    labels = list(labels)
    top = max((_RANK[x] for x in labels if x in _RANK), default=0)
    if top > 0:
        return str(top)
    return "U" if "U" in labels else "0"


def level_from_score(score: float, tau1: float, tau2: float) -> str:
    """Model skorundan düzey: C < τ1 → 0 (eksik, `yaz` kipi); τ1 ≤ C < τ2 → 1 (`tamamla`); ≥ τ2 → 2."""
    if not 0.0 <= tau1 <= tau2:
        raise ValueError("0 ≤ τ1 ≤ τ2 olmalı")
    if score < tau1:
        return "0"
    return "1" if score < tau2 else "2"


def decide(
    madde_id: str,
    children: Mapping[str, list[str]],
    leaf_levels: Mapping[str, str],
) -> Decision:
    """`children[madde_id]` boş/yoksa madde yapraktır ve `leaf_levels`'tan okunur.

    Üst madde: tüm unsurlar 2 veya U → 2 (hepsi U ise U) · hiçbiri ≥1 değil → 0 · aksi → 1.
    """
    subs = children.get(madde_id) or []
    if not subs:
        return Decision(madde_id, leaf_levels.get(madde_id, "0"))
    results = [decide(s, children, leaf_levels) for s in subs]
    levels = [r.level for r in results]
    missing = tuple(r.madde_id for r in results if r.level == "0")
    partial = tuple(r.madde_id for r in results if r.level == "1")
    if all(lv == "U" for lv in levels):
        return Decision(madde_id, "U")
    if all(lv in {"2", "U"} for lv in levels):
        return Decision(madde_id, "2")
    if all(lv in {"0", "U"} for lv in levels):
        return Decision(madde_id, "0", missing)
    return Decision(madde_id, "1", missing, partial)


def children_from_catalog(rows: Iterable[Mapping[str, str]]) -> dict[str, list[str]]:
    """Katalogdaki `ust_madde` sütunundan (katalog v1, ADR-008) üst → alt eşlemesi."""
    tree: dict[str, list[str]] = {}
    for r in rows:
        parent = (r.get("ust_madde") or "").strip()
        if parent:
            tree.setdefault(parent, []).append(r["madde_id"])
    return tree
