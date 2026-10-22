---
id: S14
baslik: TF-IDF + LR taban çizgisi, gruplu CV, eşikler, unsur kapsama
faz: F4
durum: bekliyor
sorumlu: ml-engineer
skills: [gap-baseline, algorithms-ds]
gereksinimler: [R-GAP-01, R-GAP-02, R-GAP-03, R-EVL-01]
bagimlilik: [S05, S02]
insan_onayi: Eşiklerin kabulü
---

# S14 · TF-IDF + LR taban çizgisi, gruplu CV, eşikler, unsur kapsama

**Amaç.** Deney (a)'nın taban kolu ve ilk F1.

## Girdi

Onaylı etiketler, katalog v1.

## Çıktı

Model, eşikler, run.json.

## Kabul kriterleri

- Rapor bazında bölünme testli
- Unsur kapsama toplaması birim testli
- F1 rapor bazında ortalama ± aralık

## Test komutu

```
python -m pytest -q -k gap
python tools/check_all.py
```

## Kanıt

run.json + evaluator raporu.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
