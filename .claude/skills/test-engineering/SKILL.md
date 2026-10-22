---
name: test-engineering
description: 'Test yazmak ve test stratejisi kurmak için kullan: pytest birim, sözleşme, entegrasyon, hook ve arayüz testleri; regresyon testi.'
---

# test-engineering

## Girdi
Davranış tanımı, R-*, kabul kriterleri.

## Kurallar
- Test yeri: servisin `tests/` dizini veya kökteki `tests/`. Ad veya docstring R-* içerir (`test_r_ver_01_turkce_ondalik`).
- Önce kırmızı: test düzeltmeden önce başarısız koşmalı; çıktı rapora.
- Sınır durumlarını `pytest.mark.parametrize` ile tabloya dök.
- Dış servis (LLM, DB) birim testinde taklit edilir; entegrasyon testi `-m integration` ile ayrılır.
- Rastgelelik varsa sabit tohum.

## Komutlar
- Hepsi: `python -m pytest -q`
- Tek dosya: `python -m pytest <yol> -q`
- Tüm kapı: `python tools/check_all.py`

## Kontrol listesi
- [ ] Her yeni R-* için en az bir test
- [ ] Kırmızı ve yeşil çıktılar raporda
- [ ] Beklenti gevşetilmedi
- [ ] TRACEABILITY güncelleme önerisi raporda
