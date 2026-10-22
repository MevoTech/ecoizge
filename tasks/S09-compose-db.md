---
id: S09
baslik: Docker Compose, PostgreSQL + pgvector, Alembic
faz: F3
durum: bekliyor
sorumlu: backend-engineer
skills: [db-migration, release-check, systems-diagnostics]
gereksinimler: [R-SEC-04]
bagimlilik: [S06]
insan_onayi: Ortak şema migration'ı
---

# S09 · Docker Compose, PostgreSQL + pgvector, Alembic

**Amaç.** Tek komutla ayağa kalkan geliştirme ortamı.

## Girdi

DATA_MODEL v1.

## Çıktı

`docker-compose.yml`, `db/migrations/`.

## Kabul kriterleri

- `docker compose up` → servisler healthy
- upgrade → downgrade → upgrade döngüsü geçer
- `audit_log` tetikleyicisi testli

## Test komutu

```
docker compose up -d --build
python -m pytest -m integration -q
```

## Kanıt

release-check çıktısı.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
