"""Kör etiketleme mantığı (S05, R-ETK-01). Streamlit olmadan test edilir.

Akış: data/labels/pilot/orneklem.jsonl → insan, modelin etiketini GÖRMEDEN etiketler →
      data/labels/blind/<etiketleyen>/pilot_v0.csv (etiket şablonu biçimi, kaynak = insan).

Körleme kuralları:
- Bu modül öneri dosyalarını (data/labels/proposals/) ve onay günlüğünü okumaz.
- annotation-assistant, data/labels/blind/** dizinini okuyamaz (.claude/hooks/write_scopes.json).
- κ yalnızca iki taraf da bitirdikten sonra hesaplanır (agreement-kappa skill'i).
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from review_ui import ortak
from review_ui.logic import LABEL_HEADER, read_rows, write_rows

SEVIYELER = ["2", "1", "U"]  # NONE ayrı: hiçbir madde seçilmezse yazılır
SEVIYE_ADI = {"2": "2 · Tam", "1": "1 · Kısmi / yüzeysel", "U": "U · Uygulanamaz (gerekçeli)"}
ORNEKLEM_SURUMU = "pilot_v0"


def ad_kimligi(ad: str) -> str:
    """'Mehmet Güneş' → 'mehmet-gunes' (dizin adı için)."""
    s = ortak.tr_kucuk(ad)
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
            raise ValueError("etiketleyen adı zorunlu ve en az bir harf ya da rakam içermeli")
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


def ilerleme(orneklem: list[dict], yapilan: dict) -> tuple[int, int, list[str]]:
    """(örneklemden etiketlenen, örneklem büyüklüğü, örneklemde olmayan paragraf kimlikleri)."""
    kimlikler = {u["paragraf_id"] for u in orneklem}
    return len(kimlikler & yapilan.keys()), len(kimlikler), sorted(yapilan.keys() - kimlikler)


def orneklem_ozeti(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ozet_yolu(cikti: Path) -> Path:
    return cikti.with_suffix(".orneklem.sha256")


def ozet_denetle(cikti: Path, ozet: str) -> str | None:
    """Etiket dosyası başka bir örneklemle başlatıldıysa hata mesajı döner (κ karışmasın)."""
    yol = _ozet_yolu(cikti)
    if not yol.exists():
        return None
    eski = yol.read_text(encoding="utf-8").strip()
    if eski == ozet:
        return None
    return (
        "Pilot örneklem değişmiş: bu etiket dosyası başka bir örneklemle başlatılmış "
        f"({eski[:12]}…, şimdiki {ozet[:12]}…). Kayıt durduruldu; orkestratöre bildir."
    )


def pilot_kimlikleri(data: Path) -> set[str]:
    yol = KorYollar(data).orneklem
    return {u["paragraf_id"] for u in orneklem_oku(yol)} if yol.exists() else set()


def pilot_kilitli(data: Path) -> bool:
    """Kör etiketleme sürüyor mu? Hiç kör dosya yoksa ya da biri örneklemi bitirmediyse evet.

    Kilitliyken onay ekranı pilot paragraflarının model önerilerini göstermez (R-ETK-01).
    """
    kimlikler = pilot_kimlikleri(data)
    if not kimlikler:
        return False
    dosyalar = sorted((data / "labels" / "blind").glob(f"*/{ORNEKLEM_SURUMU}.csv"))
    if not dosyalar:
        return True
    return any(not kimlikler <= yapilanlar(f).keys() for f in dosyalar)


def madde_filtrele(katalog: dict[str, dict], standart: str, bolum: str, arama: str) -> set[str]:
    """Standart, bölüm ve serbest aramaya uyan madde kimlikleri (Türkçe büyük/küçük harf duyarsız)."""
    arama = ortak.tr_kucuk(arama.strip())
    out = set()
    for mid, m in katalog.items():
        if standart != "Tümü" and m["standart"] != standart:
            continue
        if bolum != "Tümü" and m["bolum"] != bolum:
            continue
        if arama and arama not in ortak.tr_kucuk(f"{mid} {m['baslik']} {m['gereklilik_ozeti']}"):
            continue
        out.add(mid)
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
    orneklem_ozeti: str | None = None,
) -> list[dict[str, str]]:
    """Bir paragrafın kararını yazar; aynı paragrafın önceki kararını değiştirir.

    `secimler` boşsa paragraf hiçbir maddeyle ilgili değildir ve tek NONE satırı yazılır.
    """
    if not etiketleyen.strip():
        raise ValueError("etiketleyen adı zorunlu")
    for madde, seviye in secimler.items():
        if seviye is None:
            raise ValueError(f"{madde}: karşılama düzeyini seç (2, 1 ya da U)")
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
    if orneklem_ozeti and not _ozet_yolu(cikti).exists():
        _ozet_yolu(cikti).write_text(orneklem_ozeti + "\n", encoding="utf-8")
    return yeni
