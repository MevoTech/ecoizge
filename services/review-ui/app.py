"""EcoIzge çalışma ekranları (R-HIL-01). Çalıştırma: `streamlit run services/review-ui/app.py`

Ekranlar (sol menü), sırayla:
0. Başlangıç: hazırlık denetimi ve ilerleme.
1. Çıkarım kontrolü: PDF sayfası ile çıkarılan metni karşılaştır (S04).
2. Kör etiketleme: pilot paragraflarını modelin etiketini görmeden etiketle (S05).
3. Etiket onayı: model önerilerini onayla/düzelt (yalnızca pilot bittikten sonra).

Ortam değişkenleri: ECOIZGE_DATA_DIR (veri), ECOIZGE_RAPOR_DIR (PDF'ler), ECOIZGE_REPORTS_DIR (QA çıktısı).
"""

from pathlib import Path

import streamlit as st

EKRAN = Path(__file__).resolve().parent / "ekranlar"

st.set_page_config(page_title="EcoIzge", layout="wide")
st.navigation(
    [
        st.Page(EKRAN / "baslangic.py", title="Başlangıç", default=True),
        st.Page(EKRAN / "cikarim_kontrolu.py", title="1 · Çıkarım kontrolü", url_path="cikarim"),
        st.Page(EKRAN / "kor_etiketleme.py", title="2 · Kör etiketleme", url_path="kor"),
        st.Page(EKRAN / "etiket_onayi.py", title="3 · Etiket onayı", url_path="onay"),
    ]
).run()
