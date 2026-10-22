---
name: release-check
description: 'Bir sürümü veya faz sonunu doğrulamak için kullan: tüm kapı, ortamın ayağa kalkması, migration, sürüm notu.'
allowed-tools: Bash(python tools/check_all.py*) Bash(python tools/gold_manifest.py verify*)
---

# release-check

## Adımlar
1. `python tools/check_all.py` → çıkış 0.
2. (F3 sonrası) `docker compose up -d --build` → `docker compose ps` tüm servisler `healthy`.
3. (F3 sonrası) `docker compose exec report-service alembic upgrade head` → hata yok.
4. `python tools/gold_manifest.py verify` → altın küme değişmemiş (küme varsa).
5. `docs/PROGRESS.md`'ye tarih, commit, komutlar ve sonuçlar; `git tag` önerisi.

## Kontrol listesi
- [ ] Her adımın çıktısı raporda; koşulamayan adım "test edilemedi" diye yazılı
- [ ] CI son commit'te yeşil (`gh run list --limit 1`)
