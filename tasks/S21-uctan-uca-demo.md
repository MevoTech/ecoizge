---
id: S21
baslik: Uçtan uca demo ve DOCX/PDF dışa aktarım
faz: F6
durum: bekliyor
sorumlu: backend-engineer
skills: []
gereksinimler: [R-EXP-01]
bagimlilik: [S20]
insan_onayi: Demo senaryosu
---

# S21 · Uçtan uca demo ve DOCX/PDF dışa aktarım

**Amaç.** Yükle → analiz → taslak → onay → dışa aktar.

## Girdi

Tüm hat.

## Çıktı

Demo betiği, dışa aktarım.

## Kabul kriterleri

- Tek komutla demo
- DOCX/PDF çıktısında tahmin etiketleri korunuyor

## Test komutu

```
python -m pytest -m integration -q
python tools/check_all.py
```

## Kanıt

release-check çıktısı.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
