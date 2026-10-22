---
name: adr
description: "Mimari veya yöntem kararını docs/DECISIONS.md'ye karar kaydı (ADR) olarak eklemek ya da mevcut bir ADR'nin durumunu güncellemek için kullan. Tetikleyiciler: model, kütüphane, şema, sözleşme, eşik, kapsam veya veri sınıfı kararı; bir kontrolün gevşetilmesi; önerilen bir ADR'nin kullanıcı tarafından kabul edilmesi ya da reddedilmesi."
---

# adr

Karar kaydı, tez savunmasında "neden böyle yaptınız?" sorusunun yazılı cevabıdır. Ayrıca ajanlar arası çelişkide başvurulan kaynaktır: bir ajan ADR'ye aykırı bir şey önerirse orkestratör ADR'yi gösterir.

## ADR mi, görev notu mu?

| ADR yaz | Görev dosyasının "Kararlar" bölümüne yaz |
|---|---|
| Birden çok görevi ya da Zemzem'in modülünü etkiler | Yalnızca o görevin uygulama ayrıntısı |
| Geri alınması maliyetlidir (şema, vektör boyutu, kapsam) | Kolayca değiştirilir (değişken adı, dosya düzeni) |
| Tezde gerekçelendirilecek (yöntem, metrik, deney kolu) | Teze girmez |
| Bir kontrolü, eşiği ya da testi gevşetir (`.claude/rules/quality-gates.md` §Hata prosedürü 4) | — |

## Adımlar

1. `docs/DECISIONS.md`'deki son numarayı bul; yeni ADR bir sonraki numaradır.
2. Şablonu doldur:
   ```
   ## ADR-NNN · <başlık>
   Tarih: YYYY-AA-GG · Durum: önerildi | kabul | yerini aldı: ADR-xxx · Karar sahibi: <kişi>
   Bağlam: <neden gerekiyor; bağlı bulgu (B…) ve gereksinim (R-…)>
   Seçenekler: (A) … · (B) … · (C) … — her birinin artısı ve eksisi
   Karar: <seçilen>
   Sonuçlar: <etkilenen dosyalar ve görevler; geri alma yolu>
   Kanıt: <araştırma notu, run_id ya da belge bölümü>
   ```
3. Ajanlar ADR'yi en fazla `önerildi` durumunda yazar. `kabul` durumuna yalnızca kullanıcının açık onayıyla geçer; onay tarihi `Karar sahibi` alanının yanına yazılır.
4. Etkilenen `tasks/Sxx` dosyalarının "Kararlar" bölümüne ADR numarasını ekle.
5. `python tools/check_consistency.py`: belgelerde atıf yapılan her ADR numarasının tanımlı olduğunu denetler.

## Tuzaklar

- **Tek seçenekli ADR karar değil, beyandır.** Gerçekten tek seçenek varsa nedenini yaz (ör. "kullanıcı kararı", "formda zorunlu").
- **Eski ADR silinmez ve düzeltilmez.** Karar değişince yeni ADR yazılır, eskisinin durumu `yerini aldı: ADR-xxx` olur.
- **Kanıt alanı boş kalmaz.** Yöntem kararları bir araştırma notuna ya da deney koşusuna, kapsam kararları bir kaynağa (form, Teknik Kapsam bölümü) bağlanır.

## Örnek

Repodaki gerçek örnek: `docs/DECISIONS.md` → ADR-004 (yer tutuculu üretim). Kullanıcı onayı tarihli, iki seçenekli, sonuçları kod dosyasına bağlı ve geri alma yolu (A kolu deneylerde tutulur) açık.

## Kontrol listesi

- [ ] Sıradaki numara; en az iki seçenek ya da gerekçe
- [ ] Durum `önerildi` (kabul yalnızca kullanıcı onayıyla)
- [ ] Görev dosyaları güncellendi; denetleyici geçti
