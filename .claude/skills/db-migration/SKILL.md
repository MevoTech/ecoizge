---
name: db-migration
description: 'Veritabanı şeması tasarımı ve Alembic migration''ı yazmak için kullan: tablo, indeks, kısıt, pgvector kolonu, veri taşıma.'
---

# db-migration

## Durum
F3'te (S09) etkinleşir; o zamana kadar yalnızca `docs/DATA_MODEL.md` tasarımı.

## Adımlar
1. `docs/DATA_MODEL.md`'deki hedef tabloyu oku; yoksa `architect`'e dön.
2. `alembic revision -m "<ne>"`; `upgrade` ve `downgrade` ikisini de yaz.
3. Kısıtlar: `veri_turu` CHECK (gerceklesmis|tahmin), `company_id` NOT NULL + FK, benzersizlik (şirket, dönem, kalem).
4. pgvector: `vector(d)` kolonu; d embedding modeline bağlı (ADR ile sabit).
5. Boş DB'de `upgrade head` → `downgrade base` → `upgrade head` döngüsünü koş.

## İnsan onayı
Veri silen veya kolon düşüren migration; paylaşılan şema (Zemzem'le).

## Kontrol listesi
- [ ] upgrade/downgrade döngüsü çalıştı (çıktı raporda)
- [ ] DATA_MODEL.md'de ilgili tablo `[uygulandı]` oldu
