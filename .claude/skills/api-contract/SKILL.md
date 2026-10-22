---
name: api-contract
description: API uçlarını ve servisler arası JSON sözleşmesini tanımlamak, sürümlemek ve sözleşme testleriyle doğrulamak için kullan.
---

# api-contract

## Kaynaklar
- Uçlar: `docs/API_SPEC.md` (tek kaynak)
- Ortak şemalar: `shared/contracts/*.schema.json` (JSON Schema 2020-12), her yanıt `schema_version` taşır
- Test: `tests/contracts/`

## Adımlar
1. Değişikliği API_SPEC'e yaz; geriye uyumsuzsa `schema_version` ana sürümünü artır.
2. Şemayı güncelle; örnek kayıt `shared/contracts/examples/` altına.
3. Sözleşme testi: örnek kayıt şemadan geçer, bozuk örnek geçmez.
4. Zemzem'i etkiliyorsa PR'da onayını iste.

## Kontrol listesi
- [ ] `python -m pytest tests/contracts -q` yeşil
- [ ] Uç ve şema adları API_SPEC ile birebir
