---
id: S07
baslik: Onay arayüzü v1 ve toplu ön etiketleme
faz: F2
durum: devam
sorumlu: backend-engineer
skills: [label-review, test-engineering]
gereksinimler: [R-HIL-01]
bagimlilik: [S01]
insan_onayi: Arayüzün kullanılabilirliğini Mehmet onaylar
---

# S07 · Onay arayüzü v1 ve toplu ön etiketleme

**Amaç.** Etiket, koşu ve taslak onay kuyruklarını tek arayüzde toplamak.

## Girdi

`services/review-ui/`.

## Çıktı

Etiket kuyruğu [uygulandı]; koşu kuyruğu (`runs/*/run.json`) ve taslak kuyruğu [bekliyor].

## Kabul kriterleri

- Etiket kuyruğu: onayla/düzelt/reddet, günlük, doğrulayıcı uyumu, AppTest [karşılandı]
- Koşu kuyruğu ve `model_registry` durumu [bekliyor]
- Mehmet kendi makinesinde `streamlit run` ile denedi [bekliyor]

## Test komutu

```
python -m pytest services/review-ui/tests -q
```

## Kanıt

PROGRESS 2026-10-22: review-ui testleri.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
