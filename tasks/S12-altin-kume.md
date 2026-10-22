---
id: S12
baslik: Altın test kümesini dondur
faz: F4
durum: bekliyor
sorumlu: engineering-orchestrator
skills: [label-review]
gereksinimler: [R-ETK-02]
bagimlilik: [S05]
insan_onayi: Dondurmayı yalnızca Mehmet yapar
---

# S12 · Altın test kümesini dondur

**Amaç.** Test raporlarının onaylı etiketlerini dondurmak.

## Girdi

Onaylı etiketler (test raporları).

## Çıktı

`data/gold/` + `MANIFEST.json`.

## Kabul kriterleri

- Mehmet `python tools/gold_manifest.py freeze --by ...` komutunu kendisi çalıştırdı
- CI'da verify yeşil
- Test raporları eğitimde yok

## Test komutu

```
python tools/gold_manifest.py verify
```

## Kanıt

MANIFEST.json + CI.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
