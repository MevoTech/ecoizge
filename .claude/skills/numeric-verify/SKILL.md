---
name: numeric-verify
description: Taslaktaki sayıları Türkçe biçimiyle ayrıştırıp normalleştirmek, kaynak değerle ε toleransında eşlemek ve gerçekleşmiş/tahmin kipini denetlemek için kullan.
---

# numeric-verify

## Modül
`report_service.verify.numbers` (tek kaynak, `.claude/rules/python.md`).

## Kapsam
- Türkçe ayraç: `12.450,5` → 12450.5; `1.234` (binlik) ve `1,5` (ondalık) ayrımı
- Ölçek sözcükleri: bin, milyon, milyar
- Yüzde: `%12,5` ve `yüzde 12,5`
- Birimler: tCO2e/ktCO2e/MtCO2e, kWh/MWh/GWh, m³ — ortak taban birime çevrilir
- Yıl: 1900–2100 arası tek başına tam sayı değer değil yıl sayılır
- Eşleme: `|n − n*| / |n*| ≤ ε` (varsayılan ε = 0.005), birim tabanı aynı olmalı

## Adımlar
1. `extract_numbers(metin)` → değer, birim, yıl adayları.
2. `match(n, kaynaklar, eps)` → eşleşen kaynak veya None.
3. Kip: tahmin kaynaklı değerin cümlesi gelecek/öngörü işareti taşımalı, geçmiş bildiren kip taşımamalı.

## Kontrol listesi
- [ ] `python -m pytest services/report-service/tests -q -k numbers` yeşil
- [ ] Yeni biçim bulunduysa önce test eklendi
