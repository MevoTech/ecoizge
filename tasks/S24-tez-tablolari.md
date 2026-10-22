---
id: S24
baslik: Tez tabloları ve figürleri koşu kayıtlarından
faz: F8
durum: bekliyor
sorumlu: evaluator
skills: [experiment-run]
gereksinimler: [R-REP-01]
bagimlilik: [S22, S23]
insan_onayi: Tez metni
---

# S24 · Tez tabloları ve figürleri koşu kayıtlarından

**Amaç.** Tezdeki her sayının bir koşuya bağlanması.

## Girdi

`runs/`, `reports/experiments/`.

## Çıktı

Tablo ve figür dosyaları.

## Kabul kriterleri

- Elle yazılmış sayı yok
- Her tablo bir betikle yeniden üretilebilir

## Test komutu

```
python tools/check_all.py
```

## Kanıt

Üretim betiği çıktısı.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
