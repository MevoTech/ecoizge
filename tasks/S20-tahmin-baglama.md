---
id: S20
baslik: Tahmin JSON'unun taslağa bağlanması
faz: F6
durum: bekliyor
sorumlu: backend-engineer
skills: [api-contract]
gereksinimler: [R-INT-01, R-VER-03]
bagimlilik: [S11, S17]
insan_onayi: —
---

# S20 · Tahmin JSON'unun taslağa bağlanması

**Amaç.** Zemzem'in kayıtlarının `veri_turu` korunarak taslağa girmesi.

## Girdi

Sözleşme v1.

## Çıktı

`POST /exports/forecast-to-report`.

## Kabul kriterleri

- Tahmin kaydı taslakta '(tahmin)' ve öngörü kipiyle
- Uçtan uca test

## Test komutu

```
python -m pytest -m integration -q
```

## Kanıt

Test çıktısı.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
