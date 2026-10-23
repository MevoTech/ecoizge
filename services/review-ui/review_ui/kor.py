"""Kör etiketleme mantığı (S05, R-ETK-01). Streamlit olmadan test edilir.

Akış: data/labels/pilot/orneklem.jsonl → insan, modelin etiketini GÖRMEDEN etiketler →
      data/labels/blind/<etiketleyen>/pilot_v0.csv (etiket şablonu biçimi, kaynak = insan).

Körleme kuralları:
- Bu modül öneri dosyalarını (data/labels/proposals/) ve onay günlüğünü okumaz.
- annotation-assistant, data/labels/blind/** dizinini okuyamaz (.claude/hooks/write_scopes.json).
- κ yalnızca iki taraf da bitirdikten sonra hesaplanır (agreement-kappa skill'i).
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from review_ui.logic import LABEL_HEADER, read_rows, write_rows

SEVIYELER = ["2", "1", "U"]  # NONE ayrı: hiçbir madde seçilmezse yazılır
SEVIYE_ADI = {"2": "2 · Tam", "1": "1 · Kısmi / yüzeysel", "U": "U · Uygulanamaz (gerekçeli)"}
ORNEKLEM_SURUMU = "pilot_v0"


def ad_kimligi(ad: str) -> str:
    """'Mehmet Güneş' → 'mehmet-gunes' (dizin adı için)."""
    s = ad.replace("I", "ı").replace("İ", "i").lower()
    s = s.translate(str.maketrans("çğıöşü", "cgiosu"))
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


@dataclass(frozen=True)
class KorYollar:
    data: Path

    @property
    def orneklem(self) -> Path:
        return self.data / "labels" / "pilot" / "orneklem.jsonl"

    def cikti(self, etiketleyen: str) -> Path:
        kimlik = ad_kimligi(etiketleyen)
        if not kimlik:
            raise ValueError("etiketleyen adı zorunlu")
        return self.data / "labels" / "blind" / kimlik / f"{ORNEKLEM_SURUMU}.csv"


def orneklem_oku(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def yapilanlar(cikti: Path) -> dict[str, list[dict[str, str]]]:
    """paragraf_id → o paragraf için yazılmış satırlar."""
    out: dict[str, list[dict[str, str]]] = {}
    for r in read_rows(cikti):
        out.setdefault(r["paragraf_id"], []).append(r)
    return out


def sonraki_sira(orneklem: list[dict], yapilan: dict) -> int | None:
    """İlk etiketlenmemiş paragrafın sırası; hepsi bittiyse None."""
    for i, u in enumerate(orneklem):
        if u["paragraf_id"] not in yapilan:
            return i
    return None


def _sirket_yil(rapor_id: str) -> tuple[str, str]:
    """'sirket-akbank-2025' → ('akbank', '2025')."""
    m = re.fullmatch(r"(?:sirket|kap)-(.+)-(\d{4})", rapor_id)
    return (m.group(1), m.group(2)) if m else ("", "")


def kaydet(
    cikti: Path,
    birim: dict,
    secimler: dict[str, str],
    etiketleyen: str,
    katalog_kimlikleri: set[str],
    gerekce: str = "",
    bugun: date | None = None,
) -> list[dict[str, str]]:
    """Bir paragrafın kararını yazar; aynı paragrafın önceki kararını değiştirir.

    `secimler` boşsa paragraf hiçbir maddeyle ilgili değildir ve tek NONE satırı yazılır.
    """
    if not etiketleyen.strip():
        raise ValueError("etiketleyen adı zorunlu")
    for madde, seviye in secimler.items():
        if seviye not in SEVIYELER:
            raise ValueError(f"{madde}: karşılama {seviye!r} geçersiz, {SEVIYELER} olmalı")
        if madde not in katalog_kimlikleri:
            raise ValueError(f"{madde} katalogda yok")
    if "U" in secimler.values() and not gerekce.strip():
        raise ValueError("U (uygulanamaz) için gerekçe zorunlu (kılavuz §3)")

    sirket, yil = _sirket_yil(birim["rapor_id"])
    ortak = dict.fromkeys(LABEL_HEADER, "") | {
        "tur": "paragraf",
        "rapor_id": birim["rapor_id"],
        "sirket": sirket,
        "yil": yil,
        "paragraf_id": birim["paragraf_id"],
        "sayfa": str(birim["sayfa"]),
        "bolum_basligi": birim.get("bolum_basligi", ""),
        "metin": birim["metin"],
        "gerekce": gerekce.strip(),
        "etiketleyen": etiketleyen.strip(),
        "kaynak": "insan",
        "tarih": (bugun or date.today()).isoformat(),
    }
    yeni = [
        ortak | {"etiket_id": f"{birim['paragraf_id']}:{m}", "madde_id": m, "karsilama": s}
        for m, s in sorted(secimler.items())
    ] or [ortak | {"etiket_id": f"{birim['paragraf_id']}:NONE", "madde_id": "NONE", "karsilama": "NONE"}]

    kalan = [r for r in read_rows(cikti) if r["paragraf_id"] != birim["paragraf_id"]]
    write_rows(cikti, kalan + yeni)
    return yeni
