"""EcoIzge çalışma ekranları (R-HIL-01). Çalıştırma: `streamlit run services/review-ui/app.py`

Sayfalar (sol menü):
1. Çıkarım kontrolü: PDF sayfası ile çıkarılan metni karşılaştır (S04).
2. Kör etiketleme: pilot paragraflarını modelin etiketini görmeden etiketle (S05).
3. Etiket onayı: model önerilerini onayla/düzelt (pilot bittikten sonra).

Ortam değişkenleri: ECOIZGE_DATA_DIR (veri), ECOIZGE_RAPOR_DIR (PDF'ler), ECOIZGE_REPORTS_DIR (QA çıktısı).
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ui import kor, qa  # noqa: E402
from review_ui.ortak import ad_al, deney_dizini, veri_dizini  # noqa: E402

st.title("EcoIzge · Çalışma ekranları")
ad = ad_al(st, "ad_ana")

data = veri_dizini()
yollar = kor.KorYollar(data)
orneklem = kor.orneklem_oku(yollar.orneklem) if yollar.orneklem.exists() else []
birim_dizini = data / "labels" / "pilot" / "birimler"
raporlar = sorted(p.stem for p in birim_dizini.glob("*.jsonl"))
qa_ozet = qa.ozet(deney_dizini() / "extraction-qa-elle.csv")
pdf_dizin = qa.rapor_dizini(data)

st.markdown("Sırayla ilerle. Her adımın ayrıntısı `docs/kullanim/ELLE_KONTROL_VE_PILOT.md` rehberinde.")

c1, c2, c3 = st.columns(3)
c1.metric("1 · Çıkarım kontrolü", f"{qa_ozet['sayfa']} / {len(raporlar) * qa.SAYFA_SAYISI} sayfa")
if ad:
    yapilan = kor.yapilanlar(yollar.cikti(ad))
    c2.metric("2 · Kör etiketleme", f"{len(yapilan)} / {len(orneklem)} paragraf")
else:
    c2.metric("2 · Kör etiketleme", "ad gir")
c3.metric("3 · Etiket onayı", "pilot sonrası")

st.subheader("Hazırlık denetimi")
denetim = [
    ("Pilot örneklemi", yollar.orneklem.exists(), f"{len(orneklem)} paragraf · {yollar.orneklem}"),
    ("Pilot raporlarının birimleri", bool(raporlar), ", ".join(raporlar) or str(birim_dizini)),
    (
        "PDF klasörü",
        all(qa.pdf_yolu(pdf_dizin, r) for r in raporlar) and bool(raporlar),
        f"{pdf_dizin} (değiştirmek için ECOIZGE_RAPOR_DIR)",
    ),
    ("Ad", bool(ad), ad or "sol menüye adını yaz"),
]
for baslik, tamam, ayrinti in denetim:
    st.write(f"{'✅' if tamam else '⚠️'} **{baslik}**: {ayrinti}")
