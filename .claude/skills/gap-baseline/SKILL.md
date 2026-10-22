---
name: gap-baseline
description: Boşluk analizi taban çizgisini (TF-IDF + lojistik regresyon) kurmak, gruplu çapraz doğrulama yapmak ve τ1/τ2 eşiklerini seçmek için kullan.
---

# gap-baseline

## Adımlar
1. Girdi: onaylı etiketler (`data/labels/reviewed/`), katalog; birim paragraf × madde.
2. Bölünme: rapor bazında `GroupKFold` (k=5 veya rapor sayısı azsa leave-one-report-out).
3. Model: TF-IDF (kelime + karakter n-gram, Türkçe küçük harf `İ→i`, `I→ı`) + LR; sınıf dengesizliği için `class_weight`.
4. Eşikler: doğrulama katlarında F1'i en iyileyen τ1 (eksik/kısmi) ve τ2 (kısmi/tam); test katında sabit.
5. Rapor düzeyi karar: unsur kapsama toplaması (ADR-008).
6. Çıktı: `runs/<run_id>/run.json` (metrikler, eşikler, tohum, veri sürümü).

## Kontrol listesi
- [ ] Aynı rapor hem eğitimde hem testte yok
- [ ] Altın küme kullanılmadı
- [ ] Deney (a)'nın taban kolu olarak kaydedildi
