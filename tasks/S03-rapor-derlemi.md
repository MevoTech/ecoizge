---
id: S03
baslik: Rapor derlemi ve tarama tablosu
faz: F1
durum: bekliyor
sorumlu: researcher
skills: [tech-research]
gereksinimler: [R-PDF-01]
bagimlilik: []
insan_onayi: Hangi raporların kullanılacağı
---

# S03 · Rapor derlemi ve tarama tablosu

**Amaç.** En az 10 rapor (hedef 5 KOBİ) toplamak ve Geliştirme 2 §4 tarama tablosunu doldurmak.

## Girdi

KAP, şirket siteleri; Karel 2025, Sabancı 2024.

## Çıktı

`docs/research/` altında tarama notu; PDF'ler `data/raw/public/`.

## Kabul kriterleri

- ≥10 rapor, her biri için kaynak URL ve erişim tarihi
- KOBİ raporu bulunamazsa durum açıkça yazılı (G2 §4)

## Test komutu

```
python tools/check_all.py
```

## Kanıt

Tarama notu.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
