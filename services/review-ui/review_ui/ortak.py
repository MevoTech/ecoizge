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


_DENEME = 5
_BEKLEME = 0.2  # saniye, her denemede artar; testte 0


def csv_metni(alanlar: list[str], satirlar: list[dict[str, str]]) -> str:
    tampon = io.StringIO(newline="")
    w = csv.DictWriter(tampon, fieldnames=alanlar)
    w.writeheader()
    w.writerows(satirlar)
    return tampon.getvalue()


def atomik_csv_yaz(path: Path, alanlar: list[str], satirlar: list[dict[str, str]]) -> None:
    """CSV'yi atomik yazar (`atomik_coklu_yaz`); yarım dosya kalmaz.

    Windows'ta dosya Excel'de açıksa (ya da Defender/dizinleyici tutuyorsa) `replace` PermissionError
    verir. Artan aralıklarla yeniden denenir; olmazsa geçici dosya silinir ve anlaşılır bir hata
    verilir (ekranlar ValueError'ı kullanıcıya gösterir). KL-11.
    """
    atomik_coklu_yaz([(path, csv_metni(alanlar, satirlar))])


def atomik_metin_yaz(path: Path, metin: str) -> None:
    atomik_coklu_yaz([(path, metin)])


def _yerine_koy(gecici: Path, hedef: Path) -> bool:
    for deneme in range(_DENEME):
        try:
            gecici.replace(hedef)
            return True
        except PermissionError:
            if deneme + 1 < _DENEME:
                time.sleep(_BEKLEME * (deneme + 1))
    return False


def atomik_coklu_yaz(dosyalar: list[tuple[Path, str]]) -> None:
    """Birden çok dosyayı birlikte yazar: ya hepsi yeni içerikte kalır ya hepsi eski içerikte.

    Önce bütün `.tmp` dosyaları yazılıp diske zorlanır (fsync), sonra sırayla yerine konur. Biri
    yerine konamazsa önceden konanlar eski içeriğe döndürülür (Ö1: çekirdek CSV ile paragraf kaydı
    ayrışmasın).
    """
    hazir: list[tuple[Path, Path, bytes | None]] = []
    try:
        for hedef, metin in dosyalar:
            hedef.parent.mkdir(parents=True, exist_ok=True)
            gecici = hedef.with_name(hedef.name + ".tmp")
            with gecici.open("w", encoding="utf-8", newline="") as fh:
                fh.write(metin)
                fh.flush()
                os.fsync(fh.fileno())
            hazir.append((hedef, gecici, hedef.read_bytes() if hedef.exists() else None))
        konan: list[tuple[Path, bytes | None]] = []
        for hedef, gecici, eski in hazir:
            if not _yerine_koy(gecici, hedef):
                for geri, icerik in reversed(konan):
                    if icerik is None:
                        geri.unlink(missing_ok=True)
                    else:
                        geri.write_bytes(icerik)
                raise KayitHatasi(
                    f"{hedef.name} başka bir programda açık (Excel?). Dosyayı kapatıp yeniden kaydet; "
                    "bu kayıt yazılmadı, önceki kayıtların duruyor."
                )
            konan.append((hedef, eski))
    finally:
        for _, gecici, _ in hazir:
            gecici.unlink(missing_ok=True)


class KayitHatasi(ValueError):
    """Dosya yazılamadı; ekranda kullanıcıya gösterilir."""


def csv_oku(path: Path) -> list[dict[str, str]]:
    """UTF-8 CSV okur; Excel'in eklediği BOM'u atar."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))
