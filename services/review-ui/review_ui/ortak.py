"""Sayfaların ortak ayarları: veri dizini ve kullanıcı adı (oturum boyunca saklanır)."""

from __future__ import annotations

import csv
import io
import os
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def veri_dizini() -> Path:
    """Varsayılan repodaki `data/`; `ECOIZGE_DATA_DIR` ortam değişkeniyle değişir."""
    return Path(os.environ.get("ECOIZGE_DATA_DIR", REPO / "data"))


def deney_dizini() -> Path:
    return Path(os.environ.get("ECOIZGE_REPORTS_DIR", REPO / "reports" / "experiments"))


def ad_al(st, anahtar: str, etiket: str = "Adın soyadın") -> str:
    """Kenar çubuğunda ad kutusu. Ad bir kez yazılınca diğer sayfalarda da dolu gelir."""
    ad = st.sidebar.text_input(etiket, value=st.session_state.get("_ad", ""), key=anahtar)
    st.session_state["_ad"] = ad
    return ad.strip()


def md_kacis(metin: str) -> str:
    """Rapor metnini Markdown olarak yorumlanmadan göstermek için özel karakterleri kaçırır."""
    for ch in "\\`*_{}[]<>()#+-.!|$~":
        metin = metin.replace(ch, "\\" + ch)
    return metin.replace("\n", "  \n")


def tr_kucuk(metin: str) -> str:
    """Türkçe kurallı küçük harf: I → ı, İ → i (`str.lower()` "İ"yi "i̇" yapar)."""
    return metin.replace("I", "ı").replace("İ", "i").lower()


_DENEME = 3
_BEKLEME = 0.2  # saniye; testte 0


def atomik_csv_yaz(path: Path, alanlar: list[str], satirlar: list[dict[str, str]]) -> None:
    """CSV'yi atomik yazar (`atomik_metin_yaz`); yarım dosya kalmaz.

    Windows'ta dosya Excel'de açıksa (ya da OneDrive eşitliyorsa) `replace` PermissionError verir.
    Kısa aralıklarla yeniden denenir; olmazsa geçici dosya silinir ve anlaşılır bir hata verilir
    (ekranlar ValueError'ı kullanıcıya gösterir). KL-11.
    """
    tampon = io.StringIO(newline="")
    w = csv.DictWriter(tampon, fieldnames=alanlar)
    w.writeheader()
    w.writerows(satirlar)
    atomik_metin_yaz(path, tampon.getvalue())


def atomik_metin_yaz(path: Path, metin: str) -> None:
    """Metni önce `.tmp`'ye yazar, sonra yerine koyar; kilitli dosyada anlaşılır hata verir."""
    path.parent.mkdir(parents=True, exist_ok=True)
    gecici = path.with_name(path.name + ".tmp")
    with gecici.open("w", encoding="utf-8", newline="") as fh:
        fh.write(metin)
    for deneme in range(_DENEME):
        try:
            gecici.replace(path)
            return
        except PermissionError:
            if deneme + 1 < _DENEME:
                time.sleep(_BEKLEME)
    gecici.unlink(missing_ok=True)
    raise KayitHatasi(
        f"{path.name} başka bir programda açık (Excel?). Dosyayı kapatıp yeniden kaydet; kaydın kaybolmadı."
    )


class KayitHatasi(ValueError):
    """Dosya yazılamadı; ekranda kullanıcıya gösterilir."""


def csv_oku(path: Path) -> list[dict[str, str]]:
    """UTF-8 CSV okur; Excel'in eklediği BOM'u atar."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))
