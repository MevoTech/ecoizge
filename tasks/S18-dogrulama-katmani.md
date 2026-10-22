---
id: S18
baslik: Doğrulama katmanı entegrasyonu, kaynaksız cümle, kiracı izolasyonu
faz: F5
durum: bekliyor
sorumlu: ml-engineer
skills: [numeric-verify, rag-draft]
gereksinimler: [R-VER-02, R-VER-03, R-RET-02]
bagimlilik: [S17, S10]
insan_onayi: —
---

# S18 · Doğrulama katmanı entegrasyonu, kaynaksız cümle, kiracı izolasyonu

**Amaç.** Taslak hattına doğrulamayı bağlamak.

## Girdi

S15, S17.

## Çıktı

Hat entegrasyonu + testler.

## Kabul kriterleri

- İki şirketli sızıntı testi geçer
- Kaynaksız cümle uyarısı testli

## Test komutu

```
python -m pytest -q -k verify
python tools/check_all.py
```

## Kanıt

Test çıktısı + security-auditor raporu.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
