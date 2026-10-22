---
name: experiment-run
description: 'Tez deneylerini tanımlamak ve koşmak için kullan: (a) TF-IDF vs BERT, (b) RAG''li vs RAG''siz sayı hatası, (c) doğrulama açık/kapalı halüsinasyon, yer tutucu kolu ve ablasyonlar.'
allowed-tools: Bash(python tools/gold_manifest.py verify*)
---

# experiment-run

## Deney tanımı (`reports/experiments/<deney>-tanim.md`)
Soru · hipotez · kollar · veri (doğrulama/altın, sürüm) · metrik · tohum · tekrar sayısı · başarı ölçütü.

## Deneyler
| Kod | Kollar | Metrik |
|---|---|---|
| a | TF-IDF+LR / BERTurk / çok dilli; `s_spec` açık-kapalı ablasyonu (ADR-007) | P/R/F1 (madde düzeyi), rapor bazında |
| b | LLM serbest / RAG / RAG + yer tutucu (ADR-004) | sayısal hata oranı, NC |
| c | doğrulama kapalı / açık / yer tutucu + doğrulama | iddia düzeyi desteksiz ve çelişen oranı (R-EVL-03) |
| m | maskeleme değerlendirmesi (ADR-009) | ROUGE-L, BERTScore (çok dilli model adı yazılı) |

## Adımlar
1. Tanımı yaz ve kullanıcı onayı al (deneyin ortasında kol eklenmez).
2. Altın küme kullanılıyorsa `python tools/gold_manifest.py verify`.
3. Koş; her kolun `run_id`'si.
4. Sonuç: tablo + %95 güven aralığı + hata örnekleri.

## Kontrol listesi
- [ ] Kollar aynı veride, aynı tohumla
- [ ] Sonuç tablosundaki her sayı bir run_id'ye bağlı
