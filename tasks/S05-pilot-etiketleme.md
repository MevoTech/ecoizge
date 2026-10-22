---
id: S05
baslik: Pilot etiketleme, κ ve kılavuz v1
faz: F1
durum: bekliyor
sorumlu: annotation-assistant
skills: [label-propose, agreement-kappa, label-review]
gereksinimler: [R-ETK-01]
bagimlilik: [S04, S07]
insan_onayi: Mehmet'in körleme etiketleri ve kılavuz v1
---

# S05 · Pilot etiketleme, κ ve kılavuz v1

**Amaç.** ~50 paragrafta (30 aday + 20 rastgele) körleme etiketleme; κ; kılavuz v1.

## Girdi

`paragraphs.jsonl`, katalog, kılavuz v0.

## Çıktı

Öneri ve onaylı etiket dosyaları, κ raporu, `etiket_kilavuzu_v1.md`.

## Kabul kriterleri

- Doğrulayıcı geçer
- κ raporu insan–model ve (varsa) insan–insan ayrı
- Anlaşmazlıklar kılavuz §5'e işlendi

## Test komutu

```
python tools/validate_data.py
python -m pytest tests/tools/test_kappa.py -q
```

## Kanıt

`reports/experiments/kappa-*.md`.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
