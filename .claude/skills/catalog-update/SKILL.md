---
name: catalog-update
description: Gereklilik kataloğuna madde eklemek veya güncellemek için kullan (TSRS, VSME, GRI). Resmî kaynak ve doğrulama tarihi zorunlu; kullanıcı onayı gerekir.
allowed-tools: Bash(python tools/validate_data.py *)
---

# catalog-update

## Girdi
Standart, madde referansı, resmî metin bağlantısı.

## Adımlar
1. Maddeyi resmî metinden doğrula (`researcher` veya doğrudan kaynak). Özet kendi cümlenle, alıntı değil.
2. Yeni sürüm dosyası: `data/catalog/catalog_v<N+1>.csv` (eski sürüm silinmez).
3. Çok unsurlu maddeyi alt maddelere böl (ADR-008): `madde_id` sonuna `-a`, `-b` …
4. `python tools/validate_data.py data/catalog/catalog_v<N+1>.csv` → 0.
5. Değişiklik listesini kullanıcıya onaya sun.

## Kontrol listesi
- [ ] `dogrulama` sütunu `resmi_metin_YYYY-MM-DD` biçiminde
- [ ] Kimlikler benzersiz, enum değerleri izinli
- [ ] Kullanıcı onayı alındı
