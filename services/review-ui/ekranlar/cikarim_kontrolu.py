"""Çıkarım kontrolü (S04): PDF sayfası ile çıkarılan birimleri yan yana karşılaştır."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_KOK = str(Path(__file__).resolve().parents[1])
if _KOK not in sys.path:
    sys.path.insert(0, _KOK)
from review_ui import qa  # noqa: E402
from review_ui.ortak import ad_al, deney_dizini, md_kacis, veri_dizini  # noqa: E402


@st.cache_data(show_spinner=False)
def _birimler(yol: str, _degisim: float) -> list[dict]:
    return qa.birimler_oku(Path(yol))


@st.cache_data(show_spinner="PDF sayfası hazırlanıyor…")
def _goruntu(pdf: str, sayfa: int, _degisim: float) -> bytes:
    return qa.sayfa_goruntusu(Path(pdf), sayfa)


st.title("1 · Çıkarım kontrolü")
ad = ad_al(st, "ad_qa")

data = veri_dizini()
birim_dizini = data / "labels" / "pilot" / "birimler"
raporlar = sorted(p.stem for p in birim_dizini.glob("*.jsonl"))
if not raporlar:
    st.error(f"Pilot birim dosyası yok: {birim_dizini}")
    st.stop()
manifest = data / "raw" / "public" / "KAYNAKLAR.csv"
pdf_dizini = qa.rapor_dizini(data)


def _secim(rapor: str) -> tuple[list[dict], Path | None, list[int]]:
    yol = birim_dizini / f"{rapor}.jsonl"
    birimler = _birimler(str(yol), yol.stat().st_mtime)
    pdf = qa.pdf_yolu(pdf_dizini, rapor)
    n = qa.sayfa_sayisi(rapor, manifest, pdf, birimler)
    return birimler, pdf, qa.kontrol_sayfalari(birimler, sayfa_sayisi=n)


cikti = deney_dizini() / "extraction-qa-elle.csv"
kayitli = {(r["rapor_id"], r["sayfa"]): r for r in qa.kayitlar(cikti) if r["kontrol_eden"] == ad}
hedef = {(r, str(s)) for r in raporlar for s in _secim(r)[2]}  # yalnızca bugünkü örneklem sayılır
biten = len(hedef & kayitli.keys())
st.sidebar.progress(biten / len(hedef), text=f"{biten} / {len(hedef)} sayfa")

rapor = st.sidebar.selectbox("Rapor", raporlar, key="qa_rapor")
birimler, pdf, sayfalar = _secim(rapor)
etiketler = [f"s.{s} {'✓' if (rapor, str(s)) in kayitli else '·'}" for s in sayfalar]
secim = st.sidebar.radio(
    "Kontrol edilecek sayfa", range(len(sayfalar)), format_func=lambda i: etiketler[i], key="qa_sayfa"
)
sayfa = sayfalar[secim]

sol, sag = st.columns(2)
with sol:
    st.subheader(f"PDF · {rapor} · sayfa {sayfa}")
    if pdf is None:
        st.warning(f"PDF bulunamadı. Aranan klasör: {pdf_dizini} (ECOIZGE_RAPOR_DIR ile değiştir)")
    else:
        try:
            st.image(_goruntu(str(pdf), sayfa, pdf.stat().st_mtime), width="stretch")
        except ValueError as exc:
            st.warning(str(exc))
with sag:
    st.subheader("Çıkarılan birimler")
    sayfadakiler = qa.sayfa_birimleri(birimler, sayfa)
    if not sayfadakiler:
        st.warning(
            "Bu sayfadan çıkarılan birim yok. Sayfada okunabilir metin varsa **Eksik metin** işaretle; "
            "sayfa yalnızca görsel ya da boşsa hiçbir şey işaretleme."
        )
    for u in sayfadakiler:
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
