"""Etiket onayı (R-HIL-01): model önerilerini onayla, düzelt ya da reddet.

Kör pilot sürerken (kor.pilot_kilitli) pilot paragraflarının önerileri kuyruktan çıkarılır ve
gösterilmez; önce modelin önerisini görmek körlemeyi bozar (R-ETK-01).
Koşu (runs/) ve taslak kuyrukları S07/S17 görevlerinde eklenecek.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_KOK = str(Path(__file__).resolve().parents[1])
if _KOK not in sys.path:
    sys.path.insert(0, _KOK)
from review_ui import kor  # noqa: E402
from review_ui.logic import (  # noqa: E402
    KARSILAMA_PARAGRAF,
    Paths,
    catalog_lookup,
    decide,
    pending,
    proposal_files,
)
from review_ui.ortak import veri_dizini  # noqa: E402

paths = Paths(veri_dizini())
gizli = kor.pilot_kimlikleri(paths.data) if kor.pilot_kilitli(paths.data) else set()


st.title("EcoIzge · Etiket onayı")

reviewer = st.sidebar.text_input("İnceleyen (ad soyad)", key="reviewer")
files = proposal_files(paths)
if not files:
    st.info(f"Onay bekleyen öneri dosyası yok ({paths.proposals}).")
    st.stop()

choice = st.sidebar.selectbox("Öneri dosyası", [f.name for f in files], key="file")
proposal = paths.proposals / choice
queue = pending(paths, proposal)
saklanan = sum(r["paragraf_id"] in gizli for r in queue)
queue = [r for r in queue if r["paragraf_id"] not in gizli]
if saklanan:
    st.info(f"{saklanan} öneri pilot paragraflarına ait; kör etiketleme bitene kadar gösterilmiyor.")
st.sidebar.metric("Bekleyen", len(queue))
if not queue:
    if not saklanan:
        st.success("Bu dosyadaki tüm öneriler karara bağlandı.")
    st.stop()

row = queue[0]
if row["paragraf_id"] in kor.pilot_kimlikleri(paths.data):
    # Pilot paragrafının model önerisi insana ilk kez gösteriliyor: körleme açılır, kör etiketler donar (K1).
    kor.korlemeyi_ac(paths.data, f"onay ekranında pilot önerisi gösterildi ({choice})")
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
