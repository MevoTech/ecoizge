---
name: debug
description: 'Bir hatayı sistematik ayıklamak için kullan: yeniden üret, daralt, kök nedeni bul, regresyon testiyle düzelt.'
---

# debug

## Adımlar
1. Yeniden üret: tam komut, girdi, beklenen ve gerçek çıktı.
2. Daralt: en küçük girdiye indir; değişkenleri tek tek sabitle (veri, sürüm, tohum, ortam).
3. Hipotez yaz, tek değişkenle test et; sonucu not et.
4. Kök neden bulunca önce başarısız regresyon testini yaz (`test-engineer`'a görev olarak), sonra düzeltmeyi yap.
5. Aynı yaklaşım iki kez başarısızsa dur ve orkestratöre seçenekleri raporla (`.claude/rules/quality-gates.md` §Hata prosedürü).

## Kontrol listesi
- [ ] Yeniden üretme komutu raporda
- [ ] Kök neden (belirti değil) yazılı
- [ ] Regresyon testi kırmızı→yeşil
