---
name: code-review
description: 'Bir değişikliği bağımsız incelemek için kullan: doğruluk, regresyon, sınır durumları, test kapsamı, okunabilirlik, güvenlik ve performans riskleri.'
---

# code-review

## Girdi
Değişen dosyalar, ilgili görev ve R-*, `python tools/check_all.py` çıktısı.

## Adımlar
1. Görevin kabul kriterlerini oku; değişiklik bunları karşılıyor mu?
2. Her değişen fonksiyon için: boş girdi, sınır değer, hata yolu, eşzamanlılık.
3. Testler davranışı mı, uygulama ayrıntısını mı test ediyor? Eksik test var mı?
4. Proje kuralları: sayı ayrıştırma yalnız `report_service.verify.numbers`; retrieval `company_id` zorunlu; gizli değer kodda yok; sayı LLM'e serbest yazdırılmıyor.
5. Karmaşıklık ve performans: `algorithms-ds`, `perf-profile`.

## Çıktı (bulgu başına)
`dosya:satır · kritik|önemli|öneri · başarısızlık senaryosu · önerilen düzeltme`. Tahmin "olası" diye işaretlenir.

## Kontrol listesi
- [ ] Her kritik bulgunun yeniden üretilebilir senaryosu var
- [ ] İncelenen ama sorunsuz bulunan alanlar listelendi
