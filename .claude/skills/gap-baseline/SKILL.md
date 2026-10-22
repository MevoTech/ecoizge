---
name: gap-baseline
description: "Boşluk analizinin taban çizgisini (TF-IDF benzerlik öznitelikleri + lojistik regresyon) rapor bazında gruplu çapraz doğrulamayla kurmak, tau1/tau2 eşiklerini seçmek ve deney (a)'nın taban kolunu üretmek için kullan. Tetikleyiciler: onaylı etiket kümesi büyüdüğünde, BERT koluyla karşılaştırma yapılacakken, eşik değerleri sorulduğunda."
---

# gap-baseline

Tezin ilk deneyi (a), BERT tabanlı modelin basit bir yöntemden **ne kadar iyi** olduğunu gösterir (Teknik Kapsam 7). Taban çizgisi zayıf kurulursa BERT'in üstünlüğü yapay olarak büyür. Bu yüzden taban çizgisi dürüst kurulmalıdır: aynı veri, aynı bölünme, eşikler yalnızca eğitim katında seçilir.

## Yöntem (`scripts/baseline.py`)

- **Birim:** (paragraf, madde) çifti; hedef düzey 0 (NONE), 1 ya da 2. `U` çiftleri dışarıda bırakılır.
- **Öznitelikler:**
  - kelime 1–2 gram TF-IDF kosinüsü;
  - karakter 3–5 gram TF-IDF kosinüsü (Türkçe çekim eklerine dayanıklı);
  - sayısal yoğunluk;
  - birim varlığı;
  - log uzunluk.
  Hepsi standartlaştırılır.
- **Model:** çok sınıflı lojistik regresyon, `class_weight="balanced"` (NONE çiftleri çoğunluktadır).
- **Bölünme:** rapor bazında `GroupKFold`. Kat sayısı = min(5, rapor sayısı). TF-IDF her katta yalnızca eğitim paragraflarıyla öğrenilir.
- **Eşikler:** beklenen düzey skoru s = (P₁ + 2·P₂) / 2. τ₁ ve τ₂ eğitim katında F1'i en iyileyen değerlerdir; test katında sabit uygulanır. Rapor düzeyi karar, çiftlerden `report_service/nlp/coverage.py` ile toplanır.

## Adımlar

1. Bağımlılık: `pip install -r requirements-train.txt` (scikit-learn).
2. Altın test raporlarının etiket dosyalarını girdiye **katma** (S12'den sonra `data/gold/` ayrıdır; bu skill yalnızca onaylı geliştirme etiketlerini kullanır).
3. Çalıştır:
   ```
   python .claude/skills/gap-baseline/scripts/baseline.py --labels data/labels/reviewed/*.csv \
     --catalog data/catalog/catalog_v0.csv --seed 43 --out metrikler.json
   ```
   Komutu kullanıcı çalıştırır ya da Colab defterinde (`colab-train`) koşulur. Korumalı yol adı ajan komutunda yer alamaz.
4. Sonucu `run_record.py` ile koşu kaydına çevir (`colab-train`); kayıt `onay_bekliyor` durumunda başlar.
5. Katlar arası farkı oku. Bir katta F1 diğerlerinden çok düşükse o katın test raporlarını incele: çıkarım hatası mı, farklı rapor türü (KOBİ / holding) mü?

## Tuzaklar (gerçek)

- **Ölçekleme zorunlu.** Ölçeksiz öznitelikte log uzunluk benzerliği bastırır ve uzun bir paragrafın bütün madde çiftleri "karşılandı" çıkar. Bu hata `tests/skills/test_skill_scripts.py` ile yakalandı (2026-10-22).
- **Kardeş maddeler ayırt edilemez.** `TSRS2-YON-06a` ile `TSRS2-YON-06a-iii` metinleri benzer; benzerlik tabanlı model ikisini birlikte pozitif verir ve F1 düşer. Bu, taban çizgisinin bilinen sınırıdır ve BERT kolunun aşması beklenen noktadır. Tezde ayrıca raporla.
- **Rapor sızıntısı.** Paragraf bazında rastgele bölünme, aynı raporun üslubunu hem eğitime hem teste sokar ve skoru şişirir. Betik her katta sızıntı olmadığını `assert` ile doğrular.
- **Az pozitif.** Pozitif çift sayısı (`pozitif_cift`) 30'un altındaysa sonuçları "ön sonuç" diye etiketle.

## Örnek

Çıktı (`metrikler.json`, kısaltılmış):
```json
{"model": "tfidf-benzerlik+lr", "tohum": 43, "kat_sayisi": 5, "cift_sayisi": 18600, "pozitif_cift": 212,
 "f1_makro": 0.47, "f1_karsilanan": 0.58,
 "katlar": [{"kat": 0, "test_raporlari": ["karel-2025"], "tau1": 0.31, "tau2": 0.62, "f1_makro": 0.44, "f1_karsilanan": 0.55}]}
```
Bu değerler örnektir, gerçek sonuç değildir. Gerçek sonuçlar yalnızca `docs/PROGRESS.md`'ye bir `run_id` ile yazılır.

## Kontrol listesi

- [ ] Altın küme raporları girdide yok
- [ ] `kat_sayisi` ≥ 2; her rapor tam bir kez testte
- [ ] run.json üretildi, onaya gönderildi
- [ ] Kardeş madde karışması ayrıca sayıldı

## Dosyalar

- `scripts/baseline.py`: taban çizgisi
- `services/report-service/report_service/nlp/coverage.py`: madde düzeyi toplama
