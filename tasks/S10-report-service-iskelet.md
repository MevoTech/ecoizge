---
id: S10
baslik: report-service iskeleti, POST /reports, iş tablosu, yükleme güvenliği
faz: F3
durum: bekliyor
sorumlu: backend-engineer
skills: [api-contract, security-audit]
gereksinimler: [R-API-02, R-SEC-04]
bagimlilik: [S09, S04]
insan_onayi: —
---

# S10 · report-service iskeleti, POST /reports, iş tablosu, yükleme güvenliği

**Amaç.** Yükle → chunk → DB akışı, asenkron iş ve güvenli yükleme.

## Girdi

API_SPEC v1.

## Çıktı

`report_service/api/`, `report_service/db/`.

## Kabul kriterleri

- Boyut/sayfa/MIME sınırı testli (T8)
- JWT ve şirket yetkisi testli (T9)
- `GET /jobs/{id}` durum akışı testli

## Test komutu

```
python -m pytest services/report-service/tests -q
python tools/check_all.py
```

## Kanıt

Test çıktısı + security-auditor raporu.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
