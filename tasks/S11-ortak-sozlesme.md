---
id: S11
baslik: Ortak JSON sözleşmesi ve iki serviste sözleşme testleri
faz: F3
durum: devam
sorumlu: architect
skills: []
gereksinimler: [R-API-01, R-INT-01]
bagimlilik: [S06]
insan_onayi: Zemzem'in onayı
---

# S11 · Ortak JSON sözleşmesi ve iki serviste sözleşme testleri

**Amaç.** Tahmin kaydı sözleşmesini iki tarafta da test edilir yapmak.

## Girdi

Sunum S-19.

## Çıktı

`shared/contracts/forecast_record.schema.json` [uygulandı]; forecast-service tarafı testi [bekliyor].

## Kabul kriterleri

- Şema ve örnek testli [karşılandı]
- forecast-service çıktısı aynı testten geçer [bekliyor]
- Zemzem onayı [bekliyor]

## Test komutu

```
python -m pytest tests/contracts -q
```

## Kanıt

PROGRESS 2026-10-22: sözleşme testleri.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
