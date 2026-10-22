---
id: S15
baslik: Türkçe sayı normalleştirici ve kip denetimi
faz: F4
durum: tamam
sorumlu: ml-engineer
skills: [numeric-verify]
gereksinimler: [R-VER-01, R-VER-03]
bagimlilik: []
insan_onayi: —
---

# S15 · Türkçe sayı normalleştirici ve kip denetimi

**Amaç.** Sayısal tutarlılık algoritmasının (S-15 adım 5) normalleştirme ve kip parçası.

## Girdi

B9 biçim listesi.

## Çıktı

`services/report-service/report_service/verify/numbers.py`, `services/report-service/report_service/verify/tense.py`.

## Kabul kriterleri

- Türkçe ayraç, ölçek, yüzde, birim, yıl testleri geçer [karşılandı]
- Mutasyon denemesinde testler kırmızıya döner [karşılandı]
- Bilinen sınırlar modül belgesinde [karşılandı]

## Test komutu

```
python -m pytest services/report-service/tests/test_numbers.py -q
```

## Kanıt

PROGRESS 2026-10-22.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
