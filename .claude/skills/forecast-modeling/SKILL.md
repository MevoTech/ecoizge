---
name: forecast-modeling
description: 'Zemzem''in tahmin modülü için zaman serisi ve regresyon modelleme akışı: kronolojik bölme, taban çizgisi, model karşılaştırma, senaryo ve duyarlılık çıktısının sözleşmeye uygun üretimi.'
---

# forecast-modeling

## Durum
Zemzem'in modülü; Zemzem görev tanımlarını kendi `tasks/` dosyalarında belirler. Bu skill ortak kuralları taşır.

## Adımlar
1. Hangi verinin hangi soruyu yanıtladığını yaz (15 dk UCI ≠ yıllık şirket verisi; Teknik Kapsam 8).
2. Kronolojik bölme; kayan pencere CV; rastgele bölme yok.
3. Taban çizgisi (son değer/ortalama) → MLR → Ridge/Lasso → RF/XGBoost → ARIMA/Prophet → (gerekçeliyse) LSTM; MAE, RMSE, MAPE, R².
4. Hedeften türetilen sütunları girdiden çıkar (sızıntı).
5. Senaryo ve duyarlılık çıktısı `shared/contracts/forecast_record.schema.json`'a uyar; `veri_turu = "tahmin"`, `model_id`, `senaryo_id`, `guven_araligi` zorunlu.

## Kontrol listesi
- [ ] `python -m pytest tests/contracts -q` yeşil
- [ ] Sonuçlar run.json ile kayıtlı
