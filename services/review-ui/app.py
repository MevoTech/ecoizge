"""EcoIzge onay arayüzü (R-HIL-01). Çalıştırma: `streamlit run services/review-ui/app.py`

Veri dizini varsayılan olarak repodaki `data/`; `ECOIZGE_DATA_DIR` ortam değişkeniyle değişir.
Bu sürüm etiket önerilerini işler. Koşu (runs/) ve taslak kuyrukları S07/S17 görevlerinde eklenecek.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_ui.logic import (  # noqa: E402
    KARSILAMA_PARAGRAF,
    Paths,
    catalog_lookup,
    decide,
    pending,
    proposal_files,
)

DEFAULT_DATA = Path(__file__).resolve().parents[2] / "data"
paths = Paths(Path(os.environ.get("ECOIZGE_DATA_DIR", DEFAULT_DATA)))

st.set_page_config(page_title="EcoIzge Onay", layout="wide")
st.title("EcoIzge · Etiket onayı")

reviewer = st.sidebar.text_input("İnceleyen (ad soyad)", key="reviewer")
files = proposal_files(paths)
if not files:
    st.info(f"Onay bekleyen öneri dosyası yok ({paths.proposals}).")
    st.stop()

choice = st.sidebar.selectbox("Öneri dosyası", [f.name for f in files], key="file")
proposal = paths.proposals / choice
queue = pending(paths, proposal)
st.sidebar.metric("Bekleyen", len(queue))
if not queue:
    st.success("Bu dosyadaki tüm öneriler karara bağlandı.")
    st.stop()

row = queue[0]
catalog = catalog_lookup(paths)
item = catalog.get(row["madde_id"], {})

left, right = st.columns([3, 2])
with left:
    st.caption(f"{row['rapor_id']} · s.{row['sayfa']} · {row['bolum_basligi']}")
    st.markdown(f"> {row['metin']}")
with right:
    st.subheader(row["madde_id"])
    if item:
        st.write(f"**{item['baslik']}** ({item['standart']} {item['madde_ref']})")
        st.write(item["gereklilik_ozeti"])
    st.write(f"Öneri: **{row['karsilama']}** · güven {row['guven']}")
    st.write(f"Gerekçe: {row['gerekce']}")

new_value = st.selectbox("Düzeltilmiş karşılama", KARSILAMA_PARAGRAF, key="new_value")
note = st.text_input("Gerekçe (düzeltme/red için zorunlu)", key="note")
c1, c2, c3 = st.columns(3)
action = None
if c1.button("Onayla", key="approve"):
    action = ("onayla", None)
if c2.button("Düzelt", key="correct"):
    action = ("duzelt", new_value)
if c3.button("Reddet", key="reject"):
    action = ("reddet", None)

if action:
    try:
        decide(paths, proposal, row, action[0], reviewer, new_karsilama=action[1], gerekce=note)
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))
