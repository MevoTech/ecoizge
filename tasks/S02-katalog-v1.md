---
id: S02
baslik: 'Katalog v1: TSRS 1 çekirdek ve alt maddelere bölme'
faz: F1
durum: bekliyor
sorumlu: engineering-orchestrator
skills: [catalog-update]
gereksinimler: [R-KAT-01, R-GAP-03]
bagimlilik: [S01]
insan_onayi: Katalog değişikliği ve kapsam (ADR-010)
---

# S02 · Katalog v1: TSRS 1 çekirdek ve alt maddelere bölme

**Amaç.** Kataloğu MVP kapsamına (ADR-010) genişletmek ve çok unsurlu maddeleri bölmek (ADR-008).

## Girdi

`data/catalog/catalog_v0.csv`; KGK TSRS 1 resmî metni.

## Çıktı

`data/catalog/catalog_v1.csv` + değişiklik listesi.

## Kabul kriterleri

- Doğrulayıcı geçer
- Her yeni satırda `dogrulama` resmî kaynak ve tarih taşır
- Bölünen maddeler `-a/-b` ile, üst madde `not` sütununda
- Mehmet onayı

## Test komutu

```
python tools/validate_data.py
python tools/check_all.py
```

## Kanıt

Doğrulayıcı çıktısı + onay kaydı.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
