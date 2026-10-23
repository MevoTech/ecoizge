"""Çıkarım kontrolü (S04): PDF sayfası ile çıkarılan birimleri yan yana karşılaştır."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ui import qa  # noqa: E402
from review_ui.ortak import ad_al, deney_dizini, md_kacis, veri_dizini  # noqa: E402

st.title("1 · Çıkarım kontrolü")
ad = ad_al(st, "ad_qa")

data = veri_dizini()
birim_dizini = data / "labels" / "pilot" / "birimler"
raporlar = sorted(p.stem for p in birim_dizini.glob("*.jsonl"))
if not raporlar:
    st.error(f"Pilot birim dosyası yok: {birim_dizini}")
    st.stop()
cikti = deney_dizini() / "extraction-qa-elle.csv"
kayitli = {(r["rapor_id"], r["sayfa"]): r for r in qa.kayitlar(cikti)}
yapilan = set(kayitli)

rapor = st.sidebar.selectbox("Rapor", raporlar, key="qa_rapor")
birimler = qa.birimler_oku(birim_dizini / f"{rapor}.jsonl")
sayfalar = qa.kontrol_sayfalari(birimler)
etiketler = [f"s.{s} {'✓' if (rapor, str(s)) in yapilan else '·'}" for s in sayfalar]
secim = st.sidebar.radio(
    "Kontrol edilecek sayfa", range(len(sayfalar)), format_func=lambda i: etiketler[i], key="qa_sayfa"
)
sayfa = sayfalar[secim]
toplam = len(raporlar) * qa.SAYFA_SAYISI
st.sidebar.progress(len(yapilan) / toplam, text=f"{len(yapilan)} / {toplam} sayfa")

sol, sag = st.columns(2)
with sol:
    st.subheader(f"PDF · {rapor} · sayfa {sayfa}")
    pdf = qa.pdf_yolu(qa.rapor_dizini(data), rapor)
    if pdf is None:
        st.warning(f"PDF bulunamadı. Aranan klasör: {qa.rapor_dizini(data)} (ECOIZGE_RAPOR_DIR ile değiştir)")
    else:
        st.image(qa.sayfa_goruntusu(pdf, sayfa), width="stretch")
with sag:
    st.subheader("Çıkarılan birimler")
    for u in qa.sayfa_birimleri(birimler, sayfa):
        with st.container(border=True):
            st.caption(f"{u['paragraf_id']} · {u['tur']} · başlık: {u.get('bolum_basligi') or '—'}")
            st.markdown(md_kacis(u["metin"]))

st.divider()
st.write("**Bu sayfada gördüğün hatalar** (yoksa hiçbirini işaretleme):")
anahtar = f"{rapor}-{sayfa}"
mevcut = kayitli.get((rapor, str(sayfa)), {})  # kaydedilmiş sayfaya dönülürse önceki işaretler gelir
hatalar = {
    h
    for h, aciklama in qa.HATA_TURLERI.items()
    if st.checkbox(aciklama, value=mevcut.get(h) == "1", key=f"h-{h}-{anahtar}")
}
not_ = st.text_input("Not (hata işaretlediysen zorunlu)", value=mevcut.get("not", ""), key=f"not-{anahtar}")
if st.button("Kaydet", key=f"kaydet-{anahtar}", type="primary"):
    try:
        qa.kaydet(cikti, rapor, sayfa, hatalar, ad, not_)
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))

ozet = qa.ozet(cikti)
if ozet["sayfa"]:
    st.caption(f"Şimdiye kadar: {ozet['sayfa']} sayfa, {ozet['hatasiz']} hatasız · {ozet['turler']}")
