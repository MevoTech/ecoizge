"""Analiz (R-ETK-01, R-PDF-02, ADR-013): çıkarım kontrolü ve kör etiketleme dağılımları; pilot bitince uyum.

- Ad, diğer ekranlardan paylaşılmaz; burada ayrıca yazılır (aynı tarayıcıda başka biri açarsa önceki
  kişinin kayıtları kendiliğinden gelmesin, Ö4). Yerel bir araçtır; kimlik doğrulama yoktur (KL-12).
- Uyum (κ) ilk kez gösterildiği anda körleme açılmış sayılır ve kör etiketler donar (kor.korlemeyi_ac).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

_KOK = str(Path(__file__).resolve().parents[1])
if _KOK not in sys.path:
    sys.path.insert(0, _KOK)
from review_ui import analiz, kor, qa  # noqa: E402
from review_ui.ortak import deney_dizini, veri_dizini  # noqa: E402


def _cubuk(sayilar: dict[str, int]) -> None:
    """Yatay çubuk grafik; kategoriler verilen sırada, etiketler okunur."""
    df = pd.DataFrame({"kategori": list(sayilar), "sayı": list(sayilar.values())})
    st.bar_chart(
        df,
        x="kategori",
        y="sayı",
        horizontal=True,
        sort=False,
        height=60 + 32 * len(df),
        x_label="",
        y_label="",
    )


st.title("4 · Analiz")
ad = st.sidebar.text_input(
    "Adın soyadın (analiz yalnızca bu adın kayıtlarını gösterir)", key="ad_analiz"
).strip()
data = veri_dizini()
if not ad:
    st.info("Analiz kendi kayıtların üzerinden yapılır; sol menüye adını yaz.")
    st.stop()

# ---------- 1. çıkarım kontrolü ----------
st.header("1 · Çıkarım kontrolü")
qa_oz = analiz.qa_ozeti(qa.kayitlar(deney_dizini() / "extraction-qa-elle.csv"), ad)
c1, c2, c3 = st.columns(3)
c1.metric("Kontrol edilen sayfa", str(qa_oz["sayfa"]))
c2.metric("Hatasız sayfa", analiz.yuzde(qa_oz["hatasiz"], qa_oz["sayfa"]))
c3.metric("Hata işareti", str(sum(qa_oz["turler"].values())))
if qa_oz["turler"]:
    st.caption("Hata türleri (bir sayfada birden çok tür olabilir)")
    _cubuk({qa.HATA_TURLERI[h].split(" (")[0]: n for h, n in qa_oz["turler"].items()})
    tablo = [
        r | {"hatasiz_oran": analiz.yuzde(round(r["hatasiz_oran"] * r["sayfa"]), r["sayfa"])}
        for r in qa_oz["rapor"]
    ]
    st.dataframe(pd.DataFrame(tablo), hide_index=True)

# ---------- 2. kör etiketleme ----------
st.header("2 · Kör etiketleme")
yollar = kor.KorYollar(data)
if not yollar.orneklem.exists():
    st.warning(f"Pilot örneklemi yok: {yollar.orneklem}")
    st.stop()
try:
    cikti = yollar.cikti(ad)
except ValueError:
    st.error("Ad en az bir harf ya da rakam içermeli.")
    st.stop()
orneklem = kor.orneklem_oku(yollar.orneklem)
yapilan = kor.yapilanlar(cikti)
kayitlar = kor.paragraf_kayitlari(cikti)
oz = analiz.kor_ozeti(orneklem, yapilan, kayitlar)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Etiketlenen paragraf", f"{oz['etiketli']} / {oz['orneklem']}")
c2.metric("NONE (ilgisiz)", analiz.yuzde(oz["duzey"].get("NONE", 0), oz["etiketli"]))
c3.metric("Emin değilim", analiz.yuzde(oz["emin_degil"], oz["etiketli"]))
c4.metric(
    "Medyan süre",
    f"{oz['sure_medyan_sn']} sn" if oz["sure_medyan_sn"] is not None else "—",
    help="Ekranda etkin kalınan süre. 10 dakikayı aşan paragraflar ara verilmiş sayılır, medyana girmez.",
)
st.caption(
    f"Süre: n = {oz['sure_n']}, toplam {analiz.sayi(oz['sure_toplam_sn'] / 60, 1)} dk"
    + (f", ara verilmiş {oz['sure_kesintili']} paragraf" if oz["sure_kesintili"] else "")
    + (f" · çıkarım hatası nedeniyle etiketlenemeyen: {oz['cikarim_hatasi']}" if oz["cikarim_hatasi"] else "")
)
if oz["etiketli"]:
    sol, sag = st.columns(2)
    with sol:
        st.caption("Karşılama düzeyi (paragraf × madde; NONE paragraf başına)")
        _cubuk({k: oz["duzey"].get(k, 0) for k in ("2", "1", "U", "NONE")})
        if oz["belirsizlik"]:
            st.caption("Belirsizlik nedenleri")
            _cubuk({analiz.etiket_adi(kor.BELIRSIZLIK_NEDENLERI, k): n for k, n in oz["belirsizlik"].items()})
    with sag:
        if oz["beyan"]:
            st.caption("Beyan türü (bir paragrafta birden çok olabilir)")
            _cubuk({analiz.etiket_adi(kor.BEYAN_TURLERI, k): n for k, n in oz["beyan"].items()})
    st.caption("Rapor bazında")
    st.dataframe(pd.DataFrame(oz["rapor"]), hide_index=True)
    if oz["madde"]:
        st.caption("En çok etiketlenen maddeler")
        st.dataframe(
            pd.DataFrame(
                [
                    {"madde_id": m, **{k: c.get(k, 0) for k in ("2", "1", "U")}}
                    for m, c in oz["madde"].items()
                ][:20]
            ),
            hide_index=True,
        )
    st.download_button(
        "Paragraf tablosunu indir (CSV, Excel için ; ayraçlı)",
        analiz.csv_baytlari(analiz.paragraf_tablosu(orneklem, yapilan, kayitlar)),
        file_name=f"pilot-analiz-{kor.ad_kimligi(ad)}.csv",
        mime="text/csv",
    )

# ---------- 3. uyum ----------
st.header("3 · Uyum (κ)")
model = data / "labels" / "proposals" / f"{kor.ORNEKLEM_SURUMU}.csv"
if kor.pilot_kilitli(data):
    st.info("Uyum, kör etiketleme bitince hesaplanır (pilot bitince). Şimdi model önerileri gizli.")
elif not model.exists():
    st.info(f"Model önerileri henüz yok: {model.name}. Pilot bitti; bana 'bitti' yazdığında üretilecek.")
elif not cikti.exists():
    st.info(f"'{ad}' adına kör etiket dosyası yok; uyum, etiketleme yapan kişinin adıyla görülür.")
else:
    u = analiz.uyum(cikti, model)
    kor.korlemeyi_ac(data, f"analiz ekranında κ gösterildi ({kor.ad_kimligi(ad)})")
    if not u["olculen"] or math.isnan(u["kappa"]):
        st.info("κ ölçülecek (paragraf, madde) çifti yok: iki tarafta da yalnızca NONE ya da U var.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("κ (insan–model, kareli ağırlık)", analiz.sayi(u["kappa"], 3))
        c2.metric("Ortak paragraf", str(u["paragraf_ortak"]))
        c3.metric("Anlaşmazlık", str(len(u["anlasmazlik"])))
    st.caption(
        "κ için 50 paragraf küçüktür; asıl amaç kılavuzdaki belirsizlikleri bulmak (kılavuz §7). "
        "Körleme açıldı: kör etiketler artık değiştirilemez."
    )
    if u["anlasmazlik"]:
        st.dataframe(
            pd.DataFrame(
                [
                    {"paragraf_id": k[0], "madde_id": k[1], "insan": a, "model": b}
                    for k, a, b in u["anlasmazlik"]
                ]
            ),
            hide_index=True,
        )
