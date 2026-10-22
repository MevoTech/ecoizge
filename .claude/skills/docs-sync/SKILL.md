---
name: docs-sync
description: 'Belgeleri gerçek kod ve test sonuçlarıyla eşitlemek ve denetlemek için kullan: PROGRESS güncelleme, durum etiketleri, izlenebilirlik, faz sonu denetimi.'
---

# docs-sync

## Güncelleme (orkestratör)
1. `python tools/check_all.py` koş; çıktıyı ve tarihi `docs/PROGRESS.md`'ye ekle (özet + çıkış kodu).
2. Biten görevin `durum` alanını güncelle; `tasks/README.md` tablosu ile aynı olmalı.
3. Uygulanan öğelerin etiketini `[hedef]` → `[uygulandı]` yap; dosya yolunu ekle.
4. Yeni test eklendiyse `docs/TRACEABILITY.md`'ye satır ekle.

## Denetim (docs-auditor)
- `[uygulandı]` öğeler gerçek dosyaya ve geçen teste işaret ediyor mu?
- README, ARCHITECTURE, API_SPEC aynı uç ve tablo adlarını mı kullanıyor?
- PROGRESS'teki son sonuç son commit'e mi ait?
- Mekanik kontrol: `python tools/check_consistency.py`

## Kontrol listesi
- [ ] Hiçbir belge PROGRESS'te olmayan bir sonucu iddia etmiyor
