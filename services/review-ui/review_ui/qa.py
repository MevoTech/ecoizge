"""Çıkarım kalitesinin elle kontrolü (S04, R-PDF-02). Streamlit olmadan test edilir.

Her pilot raporundan seed ile seçilen sayfalar PDF görüntüsüyle yan yana gösterilir; kontrol eden
kişi hata türlerini işaretler. Sonuç `reports/experiments/extraction-qa-elle.csv` dosyasına yazılır.

Sayfa seçimi `pdf-extract` skill'indeki `qa_report.analyze` ile aynıdır (testte karşılaştırılır).
"""

from __future__ import annotations

import csv
import json
import os
import random
from collections import Counter
from datetime import date
from pathlib import Path

HATA_TURLERI = {
    "eksik_metin": "Eksik metin (PDF'te olup çıkarımda olmayan)",
    "fazla_metin": "Fazla metin (sayfada olmayan ya da tekrar eden)",
    "kirik_tablo": "Kırık tablo (hücre kaymış, satırlar karışmış)",
    "sutun_karismasi": "Sütun karışması (iki sütunun metni iç içe)",
    "yanlis_baslik": "Yanlış bölüm başlığı",
    "turkce_harf_kaybi": "Türkçe harf kaybı (ş, ı, ğ yerine · ya da boşluk)",
    "ust_alt_bilgi": "Üst/alt bilgi kalmış (sayfa no, rapor adı)",
    "bolunmus_paragraf": "Bölünmüş ya da birleşmiş paragraf",
}
QA_HEADER = ["rapor_id", "sayfa", *HATA_TURLERI, "hatasiz", "not", "kontrol_eden", "tarih"]
SAYFA_SAYISI = 5
SEED = 43


def birimler_oku(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def kontrol_sayfalari(birimler: list[dict], n: int = SAYFA_SAYISI, seed: int = SEED) -> list[int]:
    pages = sorted({u["sayfa"] for u in birimler})
    return sorted(random.Random(seed).sample(pages, min(n, len(pages))))


def sayfa_birimleri(birimler: list[dict], sayfa: int) -> list[dict]:
    return [u for u in birimler if u["sayfa"] == sayfa]


def rapor_dizini(repo_data: Path) -> Path:
    """PDF'lerin aranacağı yer: ECOIZGE_RAPOR_DIR > ~/Documents/ecoizge-raporlar > data/raw/public."""
    if os.environ.get("ECOIZGE_RAPOR_DIR"):
        return Path(os.environ["ECOIZGE_RAPOR_DIR"]).expanduser()
    belgeler = Path.home() / "Documents" / "ecoizge-raporlar"
    return belgeler if belgeler.exists() else repo_data / "raw" / "public"


def pdf_yolu(dizin: Path, rapor_id: str) -> Path | None:
    for ad in (f"ecoizge__{rapor_id}.pdf", f"{rapor_id}.pdf"):
        bulunan = sorted(dizin.rglob(ad))
        if bulunan:
            return bulunan[0]
    return None


def sayfa_goruntusu(pdf: Path, sayfa: int, dpi: int = 110) -> bytes:
    """PDF sayfasını PNG olarak döndürür (sayfa 1'den başlar)."""
    import fitz  # PyMuPDF; yalnızca bu ekranda gerekir

    with fitz.open(pdf) as doc:
        return doc[sayfa - 1].get_pixmap(dpi=dpi).tobytes("png")


def kayitlar(cikti: Path) -> list[dict[str, str]]:
    if not cikti.exists():
        return []
    with cikti.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def kaydet(
    cikti: Path,
    rapor_id: str,
    sayfa: int,
    hatalar: set[str],
    kontrol_eden: str,
    not_: str = "",
    bugun: date | None = None,
) -> dict[str, str]:
    """Bir sayfanın kontrolünü yazar; aynı sayfanın önceki kaydını değiştirir."""
    if not kontrol_eden.strip():
        raise ValueError("kontrol eden adı zorunlu")
    bilinmeyen = hatalar - HATA_TURLERI.keys()
    if bilinmeyen:
        raise ValueError(f"bilinmeyen hata türü: {sorted(bilinmeyen)}")
    if hatalar and not not_.strip():
        raise ValueError("hata işaretlendiyse not zorunlu: ne gördüğünü bir cümleyle yaz")
    satir = {
        "rapor_id": rapor_id,
        "sayfa": str(sayfa),
        **{h: "1" if h in hatalar else "0" for h in HATA_TURLERI},
        "hatasiz": "0" if hatalar else "1",
        "not": not_.strip(),
        "kontrol_eden": kontrol_eden.strip(),
        "tarih": (bugun or date.today()).isoformat(),
    }
    kalan = [r for r in kayitlar(cikti) if (r["rapor_id"], r["sayfa"]) != (rapor_id, str(sayfa))]
    cikti.parent.mkdir(parents=True, exist_ok=True)
    gecici = cikti.with_suffix(".tmp")
    with gecici.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=QA_HEADER)
        w.writeheader()
        w.writerows(kalan + [satir])
    gecici.replace(cikti)
    return satir


def ozet(cikti: Path) -> dict:
    """Kontrol edilen sayfa sayısı, hatasız sayfa oranı ve hata türü sayıları."""
    rows = kayitlar(cikti)
    turler = Counter({h: sum(r[h] == "1" for r in rows) for h in HATA_TURLERI})
    return {
        "sayfa": len(rows),
        "hatasiz": sum(r["hatasiz"] == "1" for r in rows),
        "turler": {h: n for h, n in turler.most_common() if n},
    }
