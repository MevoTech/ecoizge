"""Etiketleme ve çıkarım kontrolünün analizi (R-ETK-01, R-PDF-02, ADR-013). Streamlit olmadan test edilir.

Körleme: kör pilot sürerken (kor.pilot_kilitli) ekran yalnızca o anki etiketleyicinin kendi
kayıtlarını özetler; model önerisi ve başka etiketleyicinin kararı gösterilmez. Uyum (κ) yalnızca
pilot bitince ve model önerisi varsa hesaplanır.
"""

from __future__ import annotations

import importlib.util
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from review_ui import qa

REPO = Path(__file__).resolve().parents[3]


def _maddeler(satirlar: list[dict[str, str]]) -> list[tuple[str, str]]:
    return [(r["madde_id"], r["karsilama"]) for r in satirlar if r["madde_id"] != "NONE"]


def kor_ozeti(orneklem: list[dict], yapilan: dict[str, list[dict]], kayitlar: dict[str, dict]) -> dict:
    """Örneklemdeki paragraflar üzerinden dağılımlar. Örneklem dışı satırlar sayılmaz."""
    birimler = {u["paragraf_id"]: u for u in orneklem}
    etiketli = [pid for pid in birimler if pid in yapilan]
    duzey: Counter[str] = Counter()
    madde: dict[str, Counter[str]] = defaultdict(Counter)
    beyan: Counter[str] = Counter()
    neden: Counter[str] = Counter()
    sureler: list[int] = []
    emin_degil = 0
    rapor: dict[str, Counter[str]] = defaultdict(Counter)
    for pid in etiketli:
        ms = _maddeler(yapilan[pid])
        duzey.update([s for _, s in ms] or ["NONE"])
        for m, s in ms:
            madde[m][s] += 1
        r = rapor[birimler[pid]["rapor_id"]]
        r["etiketli"] += 1
        r["none"] += 0 if ms else 1
        r["madde"] += len(ms)
        k = kayitlar.get(pid)
        if k:
            beyan.update(k["beyan_turleri"])
            neden.update(k["belirsizlik"])
            emin_degil += 0 if k["emin"] else 1
            r["emin_degil"] += 0 if k["emin"] else 1
            if isinstance(k.get("sure_sn"), int):
                sureler.append(k["sure_sn"])
    for rid in {u["rapor_id"] for u in orneklem}:
        rapor[rid]["orneklem"] = sum(u["rapor_id"] == rid for u in orneklem)
    return {
        "orneklem": len(birimler),
        "etiketli": len(etiketli),
        "duzey": dict(duzey),
        "madde": {m: dict(c) for m, c in sorted(madde.items(), key=lambda x: -sum(x[1].values()))},
        "beyan": dict(beyan.most_common()),
        "belirsizlik": dict(neden.most_common()),
        "emin_degil": emin_degil,
        "sure_medyan_sn": int(statistics.median(sureler)) if sureler else None,
        "sure_toplam_sn": sum(sureler),
        "rapor": [{"rapor_id": rid, **dict(c)} for rid, c in sorted(rapor.items())],
    }


def paragraf_tablosu(
    orneklem: list[dict], yapilan: dict[str, list[dict]], kayitlar: dict[str, dict]
) -> list[dict]:
    """Paragraf başına tek satır; indirilebilir CSV ve tez ekleri için."""
    out = []
    for u in orneklem:
        pid = u["paragraf_id"]
        if pid not in yapilan:
            continue
        k = kayitlar.get(pid, {})
        out.append(
            {
                "paragraf_id": pid,
                "rapor_id": u["rapor_id"],
                "sayfa": u["sayfa"],
                "tur": u["tur"],
                "maddeler": "; ".join(f"{m}:{s}" for m, s in _maddeler(yapilan[pid])) or "NONE",
                "beyan_turleri": "; ".join(k.get("beyan_turleri", [])),
                "kanit": "; ".join(f"{m}:{','.join(map(str, v))}" for m, v in k.get("kanit", {}).items()),
                "belirsizlik": "; ".join(k.get("belirsizlik", [])),
                "emin": "" if not k else ("evet" if k["emin"] else "hayır"),
                "sure_sn": k.get("sure_sn", ""),
                "gerekce": next((r["gerekce"] for r in yapilan[pid]), ""),
            }
        )
    return out


def qa_ozeti(satirlar: list[dict[str, str]], kontrol_eden: str | None = None) -> dict:
    """Çıkarım kontrolü: hata türü sayıları ve rapor bazında hatasız sayfa oranı."""
    rows = [r for r in satirlar if kontrol_eden is None or r["kontrol_eden"] == kontrol_eden]
    turler = Counter({h: sum(r[h] == "1" for r in rows) for h in qa.HATA_TURLERI})
    rapor: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        rapor[r["rapor_id"]].append(r)
    return {
        "sayfa": len(rows),
        "hatasiz": sum(r["hatasiz"] == "1" for r in rows),
        "turler": {h: n for h, n in turler.most_common() if n},
        "rapor": [
            {
                "rapor_id": rid,
                "sayfa": len(rs),
                "hatasiz_oran": round(sum(r["hatasiz"] == "1" for r in rs) / len(rs), 3),
                **{h: sum(r[h] == "1" for r in rs) for h in qa.HATA_TURLERI},
            }
            for rid, rs in sorted(rapor.items())
        ],
    }


def uyum(insan: Path, model: Path) -> dict:
    """tools/kappa.py ile insan–model uyumu (ağırlıklı κ, anlaşmazlıklar). Tek hesaplama kaynağı."""
    spec = importlib.util.spec_from_file_location("kappa", REPO / "tools" / "kappa.py")
    kappa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kappa)
    return kappa.compare(insan, model, "quadratic")
