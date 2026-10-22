---
id: S19
baslik: Maskeleme değerlendirme kümesi
faz: F5
durum: bekliyor
sorumlu: evaluator
skills: [experiment-run]
gereksinimler: [R-EVL-02]
bagimlilik: [S05]
insan_onayi: Küme tanımı
---

# S19 · Maskeleme değerlendirme kümesi

**Amaç.** ROUGE-L ve BERTScore için referanslı küme (ADR-009).

## Girdi

Tam karşılanan paragraflar.

## Çıktı

Küme + ölçüm betiği.

## Kabul kriterleri

- BERTScore model adı yazılı
- Küme rapor bazında bölünmüş

## Test komutu

```
python tools/check_all.py
```

## Kanıt

Deney tanımı.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
