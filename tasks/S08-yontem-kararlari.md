---
id: S08
baslik: Yöntem kararları (ADR-007…ADR-012)
faz: F2
durum: devam
sorumlu: engineering-orchestrator
skills: [adr]
gereksinimler: [R-GAP-04, R-GEN-02, R-EVL-02, R-SEC-03]
bagimlilik: []
insan_onayi: Mehmet her ADR'yi kabul eder veya değiştirir
---

# S08 · Yöntem kararları (ADR-007…ADR-012)

**Amaç.** B1, B3, B4, B6, B7, B12, B13, B18 kararlarını kesinleştirmek (danışmana götürülmeyecek, 2026-10-22).

## Girdi

`docs/DECISIONS.md`.

## Çıktı

ADR durumları `kabul` veya değiştirilmiş.

## Kabul kriterleri

- ADR-004 kabul [karşılandı]
- ADR-007…012 Mehmet'in kararıyla `kabul` veya revize [bekliyor]

## Test komutu

```
python tools/check_all.py
```

## Kanıt

DECISIONS.md durum alanları.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
