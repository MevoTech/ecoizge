"""Çıkarım kalitesinin elle kontrolü (S04, R-PDF-02). Streamlit olmadan test edilir.

Her pilot raporundan seed ile seçilen sayfalar PDF görüntüsüyle yan yana gösterilir; kontrol eden
kişi hata türlerini işaretler. Sonuç `reports/experiments/extraction-qa-elle.csv` dosyasına yazılır.

Sayfa seçimi `pdf-extract` skill'indeki `qa_report.analyze` ile aynıdır (testte karşılaştırılır).
"""

from __future__ import annotations

import json
import os
import random
from collections import Counter
from datetime import date
from pathlib import Path

from review_ui.ortak import atomik_csv_yaz, csv_oku

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


def kontrol_sayfalari(
    birimler: list[dict], n: int = SAYFA_SAYISI, seed: int = SEED, sayfa_sayisi: int | None = None
) -> list[int]:
    """Elle kontrol edilecek sayfalar. `sayfa_sayisi` verilirse birim üretmeyen sayfalar da
    (görüntü, metni kaçan sayfa) seçilebilir; yoksa yalnızca birimi olan sayfalar."""
    pages = list(range(1, sayfa_sayisi + 1)) if sayfa_sayisi else sorted({u["sayfa"] for u in birimler})
    return sorted(random.Random(seed).sample(pages, min(n, len(pages))))


def sayfa_sayisi(rapor_id: str, manifest: Path, pdf: Path | None, birimler: list[dict]) -> int:
    """Raporun sayfa sayısı: derlem manifesti > PDF > birimlerdeki en büyük sayfa."""
    for r in csv_oku(manifest):
        if r.get("rapor_id") == rapor_id and (r.get("sayfa") or "").isdigit():
            return int(r["sayfa"])
    if pdf is not None:
        import fitz

        with fitz.open(pdf) as doc:
            return doc.page_count
    return max((u["sayfa"] for u in birimler), default=0)


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
        if not 1 <= sayfa <= doc.page_count:
            raise ValueError(f"PDF'te {doc.page_count} sayfa var, {sayfa}. sayfa yok")
        return doc[sayfa - 1].get_pixmap(dpi=dpi).tobytes("png")


def kayitlar(cikti: Path) -> list[dict[str, str]]:
    return csv_oku(cikti)


def kaydet(
    cikti: Path,
    rapor_id: str,
    sayfa: int,
    hatalar: set[str],
    kontrol_eden: str,
    not_: str = "",
    bugun: date | None = None,
) -> dict[str, str]:
    """Bir sayfanın kontrolünü yazar; aynı kişinin aynı sayfadaki önceki kaydını değiştirir.
    Farklı kişilerin kontrolleri ayrı satırlardır (iki kontrol eden karşılaştırılabilir)."""
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
    anahtar = (rapor_id, str(sayfa), satir["kontrol_eden"])
    kalan = [r for r in kayitlar(cikti) if (r["rapor_id"], r["sayfa"], r["kontrol_eden"]) != anahtar]
    atomik_csv_yaz(cikti, QA_HEADER, kalan + [satir])
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
