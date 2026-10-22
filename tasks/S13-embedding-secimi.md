---
id: S13
baslik: Embedding modeli seçimi
faz: F4
durum: bekliyor
sorumlu: ml-engineer
skills: [embed-eval, colab-train]
gereksinimler: [R-RET-01, R-REP-01]
bagimlilik: [S05]
insan_onayi: Model seçimi ADR'si
---

# S13 · Embedding modeli seçimi

**Amaç.** Adayları kendi kümemizde ölçüp seçmek (B2).

## Girdi

Doğrulama kümesi.

## Çıktı

Recall@k/MRR tablosu, ADR.

## Kabul kriterleri

- Tüm adaylar aynı çiftlerde
- Altın küme kullanılmadı
- run.json kayıtlı

## Test komutu

```
python -m pytest -q -k embed
python tools/check_all.py
```

## Kanıt

`reports/experiments/embed-*.md`.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
