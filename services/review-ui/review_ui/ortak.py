"""Sayfaların ortak ayarları: veri dizini ve kullanıcı adı (oturum boyunca saklanır)."""

from __future__ import annotations

import os
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
