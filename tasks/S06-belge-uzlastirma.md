---
id: S06
baslik: REQUIREMENTS, DATA_MODEL ve API_SPEC v1 uzlaştırması (Zemzem ile)
faz: F2
durum: bekliyor
sorumlu: architect
skills: [adr]
gereksinimler: [R-KAT-02, R-API-01, R-INT-01]
bagimlilik: [S01]
insan_onayi: Zemzem'in onayı
---

# S06 · REQUIREMENTS, DATA_MODEL ve API_SPEC v1 uzlaştırması (Zemzem ile)

**Amaç.** Ortak şema ve sözleşmeyi iki öğrencinin onayıyla v1 yapmak.

## Girdi

`docs/DATA_MODEL.md`, `docs/API_SPEC.md`.

## Çıktı

v1 belgeler, güncellenmiş şemalar.

## Kabul kriterleri

- `docs-auditor` çelişki bulmuyor
- Zemzem PR'ı onayladı

## Test komutu

```
python -m pytest tests/contracts -q
python tools/check_all.py
```

## Kanıt

PR bağlantısı.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
