"""Kör etiketleme (S05): pilot paragraflarını modelin etiketini görmeden etiketle.

Bu sayfa öneri dosyalarını ve onay günlüğünü okumaz (körleme). Çıktı:
data/labels/blind/<ad>/pilot_v0.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ui import kor  # noqa: E402
from review_ui.logic import Paths, catalog_lookup  # noqa: E402
from review_ui.ortak import ad_al, md_kacis, veri_dizini  # noqa: E402

st.title("2 · Kör etiketleme")
ad = ad_al(st, "ad_kor")

data = veri_dizini()
yollar = kor.KorYollar(data)
if not yollar.orneklem.exists():
    st.error(f"Pilot örneklemi yok: {yollar.orneklem}")
    st.stop()
if not ad:
    st.info(
        "Başlamak için sol menüye adını soyadını yaz. Etiketlerin bu ada göre ayrı bir dosyaya kaydedilir."
    )
    st.stop()

orneklem = kor.orneklem_oku(yollar.orneklem)
katalog = catalog_lookup(Paths(data))
cikti = yollar.cikti(ad)
yapilan = kor.yapilanlar(cikti)

st.sidebar.progress(len(yapilan) / len(orneklem), text=f"{len(yapilan)} / {len(orneklem)} paragraf")
sonraki = kor.sonraki_sira(orneklem, yapilan)
if sonraki is None:
    st.sidebar.success("Pilot bitti. Bana 'bitti' yaz; κ ölçümüne geçeyim.")
sira = st.sidebar.number_input(
    "Paragraf sırası (geri dönüp düzeltebilirsin)",
    min_value=1,
    max_value=len(orneklem),
    value=(sonraki if sonraki is not None else len(orneklem) - 1) + 1,
    key=f"sira-{len(yapilan)}",  # her kayıttan sonra bir sonraki etiketlenmemiş paragrafa geçer
)
birim = orneklem[int(sira) - 1]
pid = birim["paragraf_id"]
onceki = {r["madde_id"]: r["karsilama"] for r in yapilan.get(pid, []) if r["madde_id"] != "NONE"}
onceki_gerekce = next((r["gerekce"] for r in yapilan.get(pid, [])), "")

with st.expander("Karşılama düzeyleri (kılavuz §3–4)", expanded=not yapilan):
    st.markdown(
        "- **2 · Tam:** maddenin istediği unsurların **tamamı**, şirkete özgü ve somut. Sayısal maddede değer + birim + dönem.\n"
        "- **1 · Kısmi:** konuya değiniyor ama unsur eksik, ifade genel ya da birim/dönem/kapsam eksik. **Emin değilsen 1 ver ve gerekçe yaz.**\n"
        "- **U · Uygulanamaz:** koşullu madde için rapor, uygulanamaz olduğunu **gerekçesiyle** söylüyor.\n"
        "- **Hiçbir madde seçmezsen** paragraf NONE (ilgisiz) kaydedilir.\n"
        "- Çıkarım bozuksa (kırık tablo, karışık metin) etiketleme; gerekçeye **çıkarım hatası** yaz ve NONE kaydet."
    )

st.caption(
    f"{sira}/{len(orneklem)} · {birim['rapor_id']} · s.{birim['sayfa']} · "
    f"bölüm: {birim.get('bolum_basligi') or '—'} · {birim['tur']}"
    + (" · ✓ etiketlendi" if pid in yapilan else "")
)
with st.container(border=True):
    st.markdown(md_kacis(birim["metin"]))

st.subheader("Bu paragraf hangi maddeleri karşılıyor?")
f1, f2, f3 = st.columns([1, 1, 2])
standart = f1.selectbox("Standart", ["Tümü", *sorted({m["standart"] for m in katalog.values()})], key="std")
bolumler = sorted({m["bolum"] for m in katalog.values() if standart in ("Tümü", m["standart"])})
bolum = f2.selectbox("Bölüm", ["Tümü", *bolumler], key="bolum")
arama = f3.text_input("Ara (başlık ya da açıklamada)", key="ara").strip().lower()


def _uygun(m: dict) -> bool:
    if standart != "Tümü" and m["standart"] != standart:
        return False
    if bolum != "Tümü" and m["bolum"] != bolum:
        return False
    return not arama or arama in f"{m['madde_id']} {m['baslik']} {m['gereklilik_ozeti']}".lower()


secenekler = sorted({mid for mid, m in katalog.items() if _uygun(m)} | set(onceki))
secili = st.multiselect(
    "Maddeler (birden çok seçebilirsin; filtre yalnızca listeyi daraltır)",
    secenekler,
    default=sorted(onceki),
    format_func=lambda mid: f"{mid} · {katalog[mid]['baslik']}" if mid in katalog else mid,
    key=f"secili-{pid}",
    placeholder="Madde seç ya da yazarak ara…",
)

secimler: dict[str, str] = {}
for mid in secili:
    m = katalog.get(mid, {})
    with st.container(border=True):
        st.markdown(f"**{mid} · {m.get('baslik', '')}** ({m.get('standart', '')} {m.get('madde_ref', '')})")
        st.caption(m.get("gereklilik_ozeti", ""))
        secimler[mid] = st.radio(
            "Karşılama",
            kor.SEVIYELER,
            index=kor.SEVIYELER.index(onceki.get(mid, "1")),
            format_func=kor.SEVIYE_ADI.get,
            horizontal=True,
            key=f"seviye-{pid}-{mid}",
        )

gerekce = st.text_input(
    "Gerekçe (U için zorunlu; emin olmadığında ya da çıkarım hatasında yaz)",
    value=onceki_gerekce,
    key=f"gerekce-{pid}",
)
etiket = "Kaydet: NONE (hiçbir madde)" if not secimler else f"Kaydet: {len(secimler)} madde"
if st.button(etiket, type="primary", key=f"kaydet-{pid}"):
    try:
        kor.kaydet(cikti, birim, secimler, ad, set(katalog), gerekce)
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))
