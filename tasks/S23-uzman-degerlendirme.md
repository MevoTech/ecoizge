---
id: S23
baslik: Uzman değerlendirmesi (Likert) ve iddia etiketlemesi
faz: F7
durum: bekliyor
sorumlu: evaluator
skills: [experiment-run, agreement-kappa]
gereksinimler: [R-EVL-03]
bagimlilik: [S22]
insan_onayi: Uzman katılımı
---

# S23 · Uzman değerlendirmesi (Likert) ve iddia etiketlemesi

**Amaç.** Halüsinasyonun iddia düzeyinde ölçülmesi.

## Girdi

Taslak örneklemi.

## Çıktı

Etiketler, κ, oranlar.

## Kabul kriterleri

- Örneklem büyüklüğü ve uzman sayısı yazılı
- Desteksiz ve çelişen oranları ayrı

## Test komutu

```
python tools/check_all.py
```

## Kanıt

Değerlendirme raporu.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
