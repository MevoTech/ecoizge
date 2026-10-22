---
paths:
  - "data/**"
  - "docs/labeling/**"
---

# Veri ve etiket kuralları

- Katalog: `data/catalog/catalog_v<N>.csv`. Her satırda `dogrulama` (kaynak + tarih) zorunludur. Değişiklik `catalog-update` skill'iyle ve kullanıcı onayıyla yapılır.
- Etiket akışı tek yönlüdür:
  1. `data/labels/proposals/` (model önerisi);
  2. onay arayüzü (insan);
  3. `data/labels/reviewed/` + `data/reviews/reviews.jsonl`;
  4. `data/gold/` (yalnızca insan dondurur).
- Altın küme `tools/gold_manifest.py freeze` ile üretilir. SHA-256 özetleri `data/gold/MANIFEST.json`'dadır. CI her koşuda `verify` yapar.
- Veri bölünmesi rapor veya şirket bazındadır. Aynı raporun paragrafları hem eğitimde hem testte bulunmaz.
- Her CSV `python tools/validate_data.py <dosya>` ile doğrulanır. Doğrulayıcının izin verdiği değerler kılavuzla aynıdır (§3).
- Pilot firma verisi (`data/raw/pilot/`) git'e girmez ve ajanlar tarafından okunmaz.
