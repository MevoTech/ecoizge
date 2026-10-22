---
name: label-review
description: Onay arayüzünü (Streamlit) çalıştırmak ve insan kararlarını doğrulanmış etiket dosyasına aktarmak için kullan.
---

# label-review

## Akış
`data/labels/proposals/*.csv` → arayüz (insan: onayla / düzelt / reddet + gerekçe) → `data/labels/reviewed/<kaynak_dosya>` + `data/reviews/reviews.jsonl` (yalnızca ekleme).

## Çalıştırma (kullanıcının bilgisayarında)
```
pip install -r services/review-ui/requirements.txt
streamlit run services/review-ui/app.py
```

## Kurallar
- Arayüz yazar, ajanlar yazmaz (korumalı yol). Ajan yalnızca sonucu okur ve doğrular.
- Düzeltilen satır `kaynak = insan`, onaylanan `kaynak = insan_onayli`, reddedilen satır reviewed dosyasına girmez ama reviews.jsonl'de kalır.
- Her karar: `{zaman, inceleyen, dosya, etiket_id, karar, eski, yeni, gerekce}`.

## Kontrol listesi
- [ ] `python tools/validate_data.py` (argümansız: tüm katalog ve etiket dosyaları) → 0. Korumalı yol adını komuta yazma; guard engeller
- [ ] reviews.jsonl satır sayısı = verilen karar sayısı
