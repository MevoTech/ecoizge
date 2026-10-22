# Deney tasarımları

Kaynak: Teknik Kapsam 7 (deneyler a, b, c), analiz raporu bulguları B1, B7, B8, B10, ADR-004/007/009.

## (a) Boşluk analizi: taban çizgisi ile BERT

- **Soru:** Türkçe/çok dilli transformer, TF-IDF benzerlik + LR taban çizgisini madde düzeyi F1'de geçiyor mu?
- **Kollar:** `gap-baseline` · BERTurk ince ayar · çok dilli model ince ayar · en iyi model + `s_spec` açık/kapalı (ablasyon, ADR-007).
- **Veri:** onaylı etiketler (geliştirme, gruplu CV) + altın test kümesi (nihai, tek sefer).
- **Birincil metrik:** madde düzeyi makro F1 (0/1/2), rapor bazında hesaplanıp ortalanır. İkincil: F1 (karşılanan = düzey ≥ 1), eksik maddeleri yakalama recall'u.
- **Ek analiz:** kardeş madde karışması sayısı (bkz. `gap-baseline` → Tuzaklar).

## (b) Üretim: sayısal hata oranı

- **Soru:** RAG ve yer tutuculu üretim sayısal hatayı ne kadar azaltıyor?
- **Kollar:** LLM (yalnızca madde metni) · RAG (serbest sayı) · RAG + yer tutucu (ADR-004).
- **Metrik:** sayısal hata oranı = (kaynakla eşleşmeyen ya da ε dışı sayı) / (taslaktaki toplam sayı); `numeric-verify` ile. NC (S-15) = 1 − hata oranı.
- **Yer tutucu kolu için:** "VERİ EKSİK" oranı ve desteksiz iddia oranı birincil sayılır (bkz. SKILL.md → Tuzaklar).

## (c) Doğrulama katmanı: halüsinasyon

- **Soru:** Doğrulama katmanı (yeniden üretim döngüsü) desteksiz ve çelişen iddiaları ne kadar azaltıyor?
- **Kollar:** doğrulama kapalı · doğrulama açık · yer tutucu + doğrulama.
- **Metrik:** iddia düzeyi etiket (R-EVL-03):
  - **desteklenen:** kaynakta var;
  - **desteksiz:** kaynakta yok;
  - **çelişen:** kaynakla çelişiyor.

  İki insan değerlendirici kör etiketler; κ raporlanır (`agreement-kappa`).
- **Örneklem:** kol başına en az 40 taslak; madde türleri (anlatı / sayısal / karma) dengeli.

## (m) Maskeleme ile üretim kalitesi (ADR-009)

- **Kurulum:** düzeyi 2 olan gerçek paragraflar rapordan çıkarılır. Sistem o madde için `yaz` kipinde üretir. Çıktı orijinal paragrafla karşılaştırılır.
- **Metrikler:** ROUGE-L (F); BERTScore (çok dilli model, adı ve katmanı raporda yazılı); uzman Likert 1–5 (doğruluk, bütünlük, üslup).
- **Dikkat:** maskelenen paragraf retrieval kaynaklarından da çıkarılmalı; aksi hâlde model cevabı kopyalar.
