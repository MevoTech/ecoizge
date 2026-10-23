"""Kör etiketleme (S05): pilot paragraflarını modelin etiketini görmeden etiketle.

Bu sayfa öneri dosyalarını ve onay günlüğünü okumaz (körleme). Çıktı:
data/labels/blind/<ad>/pilot_v0.csv (paragraf × madde × düzey; kappa ve doğrulayıcıyla uyumlu)
      + pilot_v0.paragraf.jsonl (beyan türü, kanıt cümlesi, belirsizlik, süre; ADR-013)
      + örneklemin SHA-256 özeti (örneklem değişirse kayıt durur)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

_KOK = str(Path(__file__).resolve().parents[1])
if _KOK not in sys.path:
    sys.path.insert(0, _KOK)
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
try:
    cikti = yollar.cikti(ad)
except ValueError:
    st.error("Ad en az bir harf ya da rakam içermeli (dosya adı buna göre oluşur).")
    st.stop()

orneklem = kor.orneklem_oku(yollar.orneklem)
ozet = kor.orneklem_ozeti(yollar.orneklem)
uyari = kor.ozet_denetle(cikti, ozet)
if uyari:
    st.error(uyari)
    st.stop()
katalog = catalog_lookup(Paths(data))
yapilan = kor.yapilanlar(cikti)
if kor.korleme_acildi(data):
    biten, toplam, _ = kor.ilerleme(orneklem, yapilan)
    st.info(
        f"Körleme açıldı: model önerileri ya da uyum (κ) gösterildi. Kör etiketler donduruldu "
        f"({biten} / {toplam} paragraf). Düzeltmeler kılavuz v1 turunda yapılır; sonuçlar '4 · Analiz' ekranında."
    )
    st.stop()

biten, toplam, sahipsiz = kor.ilerleme(orneklem, yapilan)
st.sidebar.progress(biten / toplam, text=f"{biten} / {toplam} paragraf")
if sahipsiz:
    st.sidebar.warning(
        f"Etiket dosyasında örneklemde olmayan {len(sahipsiz)} paragraf var; orkestratöre bildir."
    )
sonraki = kor.sonraki_sira(orneklem, yapilan)
if sonraki is None:
    st.sidebar.success("Pilot bitti. Bana 'bitti' yaz; κ ölçümüne geçeyim.")
sira = st.sidebar.number_input(
    "Paragraf sırası (geri dönüp düzeltebilirsin)",
    min_value=1,
    max_value=len(orneklem),
    value=(sonraki if sonraki is not None else len(orneklem) - 1) + 1,
    key=f"sira-{biten}",  # her kayıttan sonra bir sonraki etiketlenmemiş paragrafa geçer
)
birim = orneklem[int(sira) - 1]
pid = birim["paragraf_id"]
onceki = {r["madde_id"]: r["karsilama"] for r in yapilan.get(pid, []) if r["madde_id"] != "NONE"}
onceki_gerekce = next((r["gerekce"] for r in yapilan.get(pid, [])), "")
onceki_kayit = kor.paragraf_kayitlari(cikti).get(pid, {})
cumleler = kor.cumlelere_bol(birim["metin"], birim["tur"])
# Süre: yalnızca paragraf ekranda etkinken sayılır; başka paragrafa geçince durur (Ö6).
sure_durumu = st.session_state.setdefault("_sure", {})
kor.sure_guncelle(sure_durumu, pid, time.monotonic())

with st.expander("Nasıl karar veririm? (kılavuz §3–4)", expanded=not yapilan):
    st.markdown(
        "**Sıra:** 1) beyan türü → 2) maddeler ve düzey → 3) her madde için kanıt cümlesi → 4) emin değilsen nedeni.\n\n"
        "- **2 · Tam:** maddenin istediği unsurların **tamamı**, şirkete özgü ve somut. Sayısal maddede değer + birim + dönem.\n"
        "- **1 · Kısmi:** konuya değiniyor ama unsur eksik, ifade genel ya da birim/dönem/kapsam eksik. Emin değilsen 1 ver, **Emin değilim**'i işaretle.\n"
        "- **U · Uygulanamaz:** koşullu madde için rapor, uygulanamaz olduğunu **gerekçesiyle** söylüyor.\n"
        "- **Hiçbir madde seçmezsen** paragraf NONE (ilgisiz) kaydedilir.\n"
        "- **Kanıt cümlesi:** 2 ya da 1 verdiğin her madde için o maddeyi karşılayan cümle(ler)in numarası.\n"
        "- Çıkarım bozuksa (kırık tablo, karışık metin) madde seçme; nedenlerden **Çıkarım hatası**'nı seç ve NONE kaydet."
    )

st.caption(
    f"{sira}/{len(orneklem)} · {birim['rapor_id']} · s.{birim['sayfa']} · "
    f"bölüm: {birim.get('bolum_basligi') or '—'} · {birim['tur']}"
    + (" · ✓ etiketlendi" if pid in yapilan else "")
)
with st.container(border=True):
    st.markdown("  \n".join(f"**[{i}]** {md_kacis(c)}" for i, c in enumerate(cumleler, start=1)))

beyan = st.multiselect(
    "Beyan türü (bu paragraf ne söylüyor? birden çok seçebilirsin; çıkarım hatasında boş bırakılabilir)",
    list(kor.BEYAN_TURLERI),
    default=None if f"beyan-{pid}" in st.session_state else onceki_kayit.get("beyan_turleri", []),
    format_func=kor.BEYAN_TURLERI.get,
    key=f"beyan-{pid}",
    placeholder="Politika, hedef, gerçekleşen sonuç…",
)

st.subheader("Bu paragraf hangi maddeleri karşılıyor?")
f1, f2, f3 = st.columns([1, 1, 2])
standart = f1.selectbox("Standart", ["Tümü", *sorted({m["standart"] for m in katalog.values()})], key="std")
bolumler = sorted({m["bolum"] for m in katalog.values() if standart in ("Tümü", m["standart"])})
bolum = f2.selectbox("Bölüm", ["Tümü", *bolumler], key="bolum")
arama = f3.text_input("Ara (başlık ya da açıklamada)", key="ara")

secim_anahtari = f"secili-{pid}"
# Filtre yalnızca listeyi daraltır: kaydedilmiş ve henüz kaydedilmemiş seçimler listede kalır.
secenekler = sorted(
    kor.madde_filtrele(katalog, standart, bolum, arama)
    | set(onceki)
    | set(st.session_state.get(secim_anahtari, []))
)
secili = st.multiselect(
    "Maddeler (birden çok seçebilirsin; filtre yalnızca listeyi daraltır)",
    secenekler,
    default=None if secim_anahtari in st.session_state else sorted(onceki),
    format_func=lambda mid: f"{mid} · {katalog[mid]['baslik']}" if mid in katalog else mid,
    key=secim_anahtari,
    placeholder="Madde seç ya da yazarak ara…",
)

secimler: dict[str, str | None] = {}
kanit: dict[str, list[int]] = {}
for mid in secili:
    m = katalog.get(mid, {})
    with st.container(border=True):
        st.markdown(f"**{mid} · {m.get('baslik', '')}** ({m.get('standart', '')} {m.get('madde_ref', '')})")
        st.caption(m.get("gereklilik_ozeti", ""))
        secimler[mid] = st.radio(
            "Karşılama",
            kor.SEVIYELER,
            index=kor.SEVIYELER.index(onceki[mid]) if mid in onceki else None,  # varsayılan yok: çapa etkisi
            format_func=kor.SEVIYE_ADI.get,
            horizontal=True,
            key=f"seviye-{pid}-{mid}",
        )
        if secimler[mid] in ("2", "1"):
            anahtar = f"kanit-{pid}-{mid}"
            kanit[mid] = st.multiselect(
                "Kanıt cümlesi (bu maddeyi hangi cümle karşılıyor?)",
                list(range(1, len(cumleler) + 1)),
                default=None
                if anahtar in st.session_state
                else kor.kanit_varsayilan(onceki_kayit, mid, cumleler),
                format_func=lambda i: (
                    f"[{i}] {cumleler[i - 1][:70]}{'…' if len(cumleler[i - 1]) > 70 else ''}"
                ),
                key=anahtar,
                placeholder="Cümle numarası seç",
            )

b1, b2 = st.columns([1, 3])
emin_degil = b1.checkbox("Emin değilim", value=onceki_kayit.get("emin") is False, key=f"emin-degil-{pid}")
nedenler = b2.multiselect(
    "Belirsizlik nedeni (emin değilsen zorunlu; neden seçmek 'emin değilim' demektir)",
    list(kor.BELIRSIZLIK_NEDENLERI),
    default=None if f"neden-{pid}" in st.session_state else onceki_kayit.get("belirsizlik", []),
    format_func=kor.BELIRSIZLIK_NEDENLERI.get,
    key=f"neden-{pid}",
    placeholder="Eksik bağlam, çıkarım hatası…",
)
gerekce = st.text_input(
    "Gerekçe (U için zorunlu; serbest not)",
    value=onceki_gerekce,
    key=f"gerekce-{pid}",
)
etiket = "Kaydet: NONE (hiçbir madde)" if not secimler else f"Kaydet: {len(secimler)} madde"
if st.button(etiket, type="primary", key=f"kaydet-{pid}"):
    try:
        kor.kaydet(
            cikti,
            birim,
            secimler,
            ad,
            set(katalog),
            gerekce,
            orneklem_ozeti=ozet,
            beyan_turleri=beyan,
            kanit=kanit,
            belirsizlik=nedenler,
            emin=not (emin_degil or nedenler),  # kılavuz §3c: neden seçildiyse emin değil
            sure_sn=kor.sure_al(sure_durumu, pid, time.monotonic()),
        )
        kor.sure_sifirla(sure_durumu, pid, time.monotonic())
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))
