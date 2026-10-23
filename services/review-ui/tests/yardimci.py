"""Ekran ve mantık testlerinin ortak yardımcıları (fikstür `veri` conftest.py'de)."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI = ROOT / "services/review-ui"
KATALOG = ROOT / "data/catalog/catalog_v0.csv"
IDS = {r["madde_id"] for r in csv.DictReader(KATALOG.open(encoding="utf-8"))}


def _birim(i: int, sayfa: int = 3, rapor: str = "sirket-ornek-2025") -> dict:
    return {
        "paragraf_id": f"{rapor}-p{sayfa:03d}-{i:02d}",
        "rapor_id": rapor,
        "sayfa": sayfa,
        "bolum_basligi": "Yönetişim",
        "tur": "paragraf",
        "metin": f"Sürdürülebilirlik Komitesi yılda iki kez Yönetim Kurulu'na sunum yapar. #{i} *kalın değil*",
        "kaynak": "metin",
    }


def _oneri_yaz(data: Path, birimler: list[dict], metin_on: str) -> Path:
    from review_ui.logic import LABEL_HEADER, write_rows

    satirlar = [
        dict.fromkeys(LABEL_HEADER, "")
        | {
            "etiket_id": f"{b['paragraf_id']}:TSRS2-YON-06a",
            "tur": "paragraf",
            "rapor_id": b["rapor_id"],
            "paragraf_id": b["paragraf_id"],
            "sayfa": str(b["sayfa"]),
            "metin": f"{metin_on} {b['paragraf_id']}",
            "madde_id": "TSRS2-YON-06a",
            "karsilama": "2",
            "guven": "0.9",
            "gerekce": "model gerekçesi",
            "etiketleyen": "annotation-assistant",
            "kaynak": "model",
        }
        for b in birimler
    ]
    hedef = data / "labels" / "proposals" / "pilot_v0.csv"
    write_rows(hedef, satirlar)
    return hedef
