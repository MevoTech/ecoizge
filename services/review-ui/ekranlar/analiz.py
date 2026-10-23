"""Analiz (R-ETK-01, R-PDF-02): çıkarım kontrolü ve kör etiketleme dağılımları; pilot bitince uyum.

Kör pilot sürerken yalnızca bu ekranı açan kişinin kendi kayıtları özetlenir (körleme).
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

_KOK = str(Path(__file__).resolve().parents[1])
if _KOK not in sys.path:
    sys.path.insert(0, _KOK)
from review_ui import analiz, kor, qa  # noqa: E402
from review_ui.ortak import ad_al, deney_dizini, veri_dizini  # noqa: E402


def _yuzde(pay: int, payda: int) -> str:
    return f"%{100 * pay / payda:.0f}".replace(".", ",") if payda else "—"


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


def _csv(satirlar: list[dict]) -> bytes:
    tampon = io.StringIO()
    if satirlar:
        w = csv.DictWriter(tampon, fieldnames=list(satirlar[0]))
        w.writeheader()
        w.writerows(satirlar)
    return tampon.getvalue().encode("utf-8-sig")  # Excel Türkçe karakterleri doğru açsın


st.title("4 · Analiz")
ad = ad_al(st, "ad_analiz")
data = veri_dizini()
if not ad:
    st.info("Analiz kendi kayıtların üzerinden yapılır; sol menüye adını yaz.")
    st.stop()
kilitli = kor.pilot_kilitli(data)

# ---------- 1. çıkarım kontrolü ----------
st.header("1 · Çıkarım kontrolü")
qa_oz = analiz.qa_ozeti(qa.kayitlar(deney_dizini() / "extraction-qa-elle.csv"), ad)
c1, c2, c3 = st.columns(3)
c1.metric("Kontrol edilen sayfa", str(qa_oz["sayfa"]))
c2.metric("Hatasız sayfa", _yuzde(qa_oz["hatasiz"], qa_oz["sayfa"]))
c3.metric("Hata işareti", str(sum(qa_oz["turler"].values())))
if qa_oz["turler"]:
    st.caption("Hata türleri (bir sayfada birden çok tür olabilir)")
    _cubuk({qa.HATA_TURLERI[h].split(" (")[0]: n for h, n in qa_oz["turler"].items()})
    rapor_tablosu = [
        r | {"hatasiz_oran": _yuzde(round(r["hatasiz_oran"] * r["sayfa"]), r["sayfa"])}
        for r in qa_oz["rapor"]
    ]
    st.dataframe(pd.DataFrame(rapor_tablosu), hide_index=True)

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
c2.metric("NONE", _yuzde(oz["duzey"].get("NONE", 0), oz["etiketli"]))
c3.metric("Emin değilim", _yuzde(oz["emin_degil"], oz["etiketli"]))
c4.metric("Medyan süre", f"{oz['sure_medyan_sn']} sn" if oz["sure_medyan_sn"] is not None else "—")
if oz["etiketli"]:
    sol, sag = st.columns(2)
    with sol:
        st.caption("Karşılama düzeyi (paragraf × madde; NONE paragraf başına)")
        _cubuk({k: oz["duzey"].get(k, 0) for k in ("2", "1", "U", "NONE")})
        if oz["belirsizlik"]:
            st.caption("Belirsizlik nedenleri")
            _cubuk({kor.BELIRSIZLIK_NEDENLERI[k].split(":")[0]: n for k, n in oz["belirsizlik"].items()})
    with sag:
        st.caption("Beyan türü (bir paragrafta birden çok olabilir)")
        _cubuk({kor.BEYAN_TURLERI[k].split(":")[0]: n for k, n in oz["beyan"].items()})
    st.caption("Rapor bazında")
    st.dataframe(pd.DataFrame(oz["rapor"]), hide_index=True)
    st.caption("En çok etiketlenen maddeler")
    st.dataframe(
        pd.DataFrame(
            [{"madde_id": m, **{k: c.get(k, 0) for k in ("2", "1", "U")}} for m, c in oz["madde"].items()][
                :20
            ]
        ),
        hide_index=True,
    )
    st.download_button(
        "Paragraf tablosunu indir (CSV)",
        _csv(analiz.paragraf_tablosu(orneklem, yapilan, kayitlar)),
        file_name=f"pilot-analiz-{kor.ad_kimligi(ad)}.csv",
        mime="text/csv",
    )

# ---------- 3. uyum ----------
st.header("3 · Uyum (κ)")
model = data / "labels" / "proposals" / f"{kor.ORNEKLEM_SURUMU}.csv"
if kilitli:
    st.info("Uyum, kör etiketleme bitince hesaplanır (pilot bitince). Şimdi model önerileri gizli.")
elif not model.exists():
    st.info(f"Model önerileri henüz yok: {model.name}. Pilot bitti; bana 'bitti' yazdığında üretilecek.")
else:
    u = analiz.uyum(cikti, model)
    c1, c2, c3 = st.columns(3)
    c1.metric("κ (insan–model, kareli ağırlık)", f"{u['kappa']:.3f}".replace(".", ","))
    c2.metric("Ortak paragraf", str(u["paragraf_ortak"]))
    c3.metric("Anlaşmazlık", str(len(u["anlasmazlik"])))
    st.caption("κ için 50 paragraf küçüktür; asıl amaç kılavuzdaki belirsizlikleri bulmak (kılavuz §7).")
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
