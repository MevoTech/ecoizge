---
id: S16
baslik: BERTurk / çok dilli ince ayar ve Türkçe spesifiklik başlığı (Colab)
faz: F5
durum: bekliyor
sorumlu: ml-engineer
skills: [colab-train, gap-baseline]
gereksinimler: [R-GAP-02, R-GAP-04, R-REP-01]
bagimlilik: [S14, S08]
insan_onayi: Koşu kabulü (onay arayüzü)
---

# S16 · BERTurk / çok dilli ince ayar ve Türkçe spesifiklik başlığı (Colab)

**Amaç.** Deney (a)'nın BERT kolu ve `s_spec` ablasyonu (ADR-007).

## Girdi

Onaylı etiketler.

## Çıktı

Colab defteri, run.json, model (Drive).

## Kabul kriterleri

- Defter temiz çekirdekte çalıştı
- Tohum ve sürümler kayıtlı
- Ablasyon sonucu var

## Test komutu

```
python tools/check_all.py
```

## Kanıt

run.json + evaluator raporu.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
