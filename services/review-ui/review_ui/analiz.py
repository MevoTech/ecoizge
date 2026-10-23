"""Etiketleme ve çıkarım kontrolünün analizi (R-ETK-01, R-PDF-02, ADR-013). Streamlit olmadan test edilir.

Körleme: kör pilot sürerken (kor.pilot_kilitli) ekran yalnızca o anki etiketleyicinin kendi
kayıtlarını özetler; model önerisi ve başka etiketleyicinin kararı gösterilmez. Uyum (κ) yalnızca
pilot bitince ve model önerisi varsa hesaplanır.
"""

from __future__ import annotations

import csv
import importlib.util
import io
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from review_ui import kor, qa

REPO = Path(__file__).resolve().parents[3]


def _modul(ad: str, yol: Path):
    """Depodaki tek kaynak modülü dosya yolundan yükler (review-ui ayrı paket; sys.path'e dokunmaz)."""
    ad = f"_ecoizge_{ad}"
    if ad not in sys.modules:
        spec = importlib.util.spec_from_file_location(ad, yol)
        modul = importlib.util.module_from_spec(spec)
        sys.modules[ad] = modul  # dataclass ve ileri başvurular modülü sys.modules'ta arar
        spec.loader.exec_module(modul)
    return sys.modules[ad]


# Türkçe sayı biçiminin tek kaynağı (.claude/rules/turkce-tdk.md): format_tr.
_sayilar = _modul("sayilar", REPO / "services/report-service/report_service/verify/numbers.py")


def sayi(x: float, ondalik: int = 0) -> str:
    return _sayilar.format_tr(x, ondalik)


def yuzde(pay: int, payda: int) -> str:
    """%33,3 biçiminde (TDK: yüzde işareti önde, ondalık virgül); payda 0 ise "—"."""
    if not payda:
        return "—"
    deger = math.floor(1000 * pay / payda + 0.5) / 10  # yarım yukarı yuvarlanır (%12,5 → %12,5)
    return "%" + (sayi(deger, 0) if deger == int(deger) else sayi(deger, 1))


def etiket_adi(sozluk: dict[str, str], kod: str) -> str:
    """Şemadaki kısa ad; şemada olmayan (eski sürüm) kod çökmeden kendisiyle gösterilir (K-4)."""
    return sozluk.get(kod, kod).split(":")[0]


def csv_baytlari(satirlar: list[dict]) -> bytes:
    """Excel (Türkçe Windows) çift tıklamayla sütunlara ayırsın diye ';' ayraçlı, BOM'lu UTF-8 (K-2)."""
    tampon = io.StringIO()
    if satirlar:
        w = csv.DictWriter(tampon, fieldnames=list(satirlar[0]), delimiter=";")
        w.writeheader()
        w.writerows(satirlar)
    return tampon.getvalue().encode("utf-8-sig")


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
    kesintili = 0
    emin_degil = 0
    cikarim_hatasi = 0
    alanlar = ("etiketli", "none", "cikarim_hatasi", "madde", "emin_degil")
    rapor: dict[str, Counter[str]] = defaultdict(lambda: Counter(dict.fromkeys(alanlar, 0)))
    for pid in etiketli:
        ms = _maddeler(yapilan[pid])
        k = kayitlar.get(pid)
        bozuk = bool(k) and "cikarim_hatasi" in k["belirsizlik"]
        if bozuk:  # "ilgisiz" (NONE) ile "metin bozuk" ayrı sayılır (K-6)
            cikarim_hatasi += 1
        else:
            duzey.update([s for _, s in ms] or ["NONE"])
        for m, s in ms:
            madde[m][s] += 1
        r = rapor[birimler[pid]["rapor_id"]]
        r["etiketli"] += 1
        r["none"] += 0 if ms or bozuk else 1
        r["cikarim_hatasi"] += 1 if bozuk else 0
        r["madde"] += len(ms)
        if k:
            beyan.update(k["beyan_turleri"])
            neden.update(k["belirsizlik"])
            emin_degil += 0 if k["emin"] else 1
            r["emin_degil"] += 0 if k["emin"] else 1
            if isinstance(k.get("sure_sn"), int):
                if k["sure_sn"] > kor.KESINTI_ESIGI_SN:
                    kesintili += 1  # ara verilmiş; toplam ve medyana girmez (Ö6)
                else:
                    sureler.append(k["sure_sn"])
    for rid in sorted({u["rapor_id"] for u in orneklem}):
        rapor[rid]["orneklem"] = sum(u["rapor_id"] == rid for u in orneklem)
    return {
        "orneklem": len(birimler),
        "etiketli": len(etiketli),
        "duzey": dict(duzey),
        "madde": {m: dict(c) for m, c in sorted(madde.items(), key=lambda x: -sum(x[1].values()))},
        "beyan": dict(beyan.most_common()),
        "belirsizlik": dict(neden.most_common()),
        "emin_degil": emin_degil,
        "cikarim_hatasi": cikarim_hatasi,
        "sure_medyan_sn": int(statistics.median(sureler)) if sureler else None,
        "sure_toplam_sn": sum(sureler),
        "sure_n": len(sureler),
        "sure_kesintili": kesintili,
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
    kimlik = kor.ad_kimligi(kontrol_eden) if kontrol_eden is not None else None
    rows = [r for r in satirlar if kimlik is None or kor.ad_kimligi(r["kontrol_eden"]) == kimlik]
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
    return _modul("kappa", REPO / "tools" / "kappa.py").compare(insan, model, "quadratic")
