---
id: S22
baslik: Deneyler (a), (b), (c) ve ablasyonlar
faz: F7
durum: bekliyor
sorumlu: evaluator
skills: [experiment-run, agreement-kappa]
gereksinimler: [R-EVL-01, R-EVL-04, R-GAP-02]
bagimlilik: [S12, S16, S18]
insan_onayi: Deney tanımları
---

# S22 · Deneyler (a), (b), (c) ve ablasyonlar

**Amaç.** Tezin ana sonuçları.

## Girdi

Altın küme (manifest doğrulanmış).

## Çıktı

Sonuç tabloları.

## Kabul kriterleri

- Her sayı bir run_id'ye bağlı
- Güven aralıkları var

## Test komutu

```
python tools/gold_manifest.py verify
python tools/check_all.py
```

## Kanıt

`reports/experiments/`.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
