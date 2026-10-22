---
id: S17
baslik: LLM seçimi, RAG yaz/tamamla, yer tutuculu üretim, injection testi
faz: F5
durum: devam
sorumlu: ml-engineer
skills: [rag-draft, numeric-verify]
gereksinimler: [R-GEN-01, R-GEN-02, R-GEN-03, R-GEN-04, R-SEC-01, R-SEC-03]
bagimlilik: [S08, S13]
insan_onayi: LLM seçimi ve prompt sürümü
---

# S17 · LLM seçimi, RAG yaz/tamamla, yer tutuculu üretim, injection testi

**Amaç.** Kaynaklı taslak üretimi.

## Girdi

ADR-004, ADR-008, ADR-011.

## Çıktı

`services/report-service/report_service/generation/placeholders.py` [uygulandı]; LLM istemcisi ve prompt [bekliyor].

## Kabul kriterleri

- Yer tutucu doğrulama/doldurma testleri [karşılandı]
- Injection içeren sentetik PDF testi [bekliyor]
- Prompt sürümü kayıtlı ve onaylı [bekliyor]

## Test komutu

```
python -m pytest services/report-service/tests/test_placeholders.py -q
```

## Kanıt

PROGRESS 2026-10-22.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
