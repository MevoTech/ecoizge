---
name: adr
description: Mimari veya yöntem kararını docs/DECISIONS.md'ye karar kaydı (ADR) olarak eklemek için kullan. Model, kütüphane, şema, sözleşme, eşik veya kapsam kararı verildiğinde.
---

# adr

## Girdi
Karar sorusu, seçenekler, kanıt (araştırma notu, deney `run_id`), karar sahibi.

## Çıktı
`docs/DECISIONS.md` sonuna yeni ADR (sıradaki numara).

## Şablon
```
## ADR-NNN · <başlık>
Tarih: YYYY-MM-DD · Durum: önerildi | kabul | yerini aldı: ADR-xxx · Karar sahibi: <kişi>
Bağlam: <neden karar gerekiyor; bağlı bulgu/R-*>
Seçenekler: <A / B / C — artı/eksi>
Karar: <seçilen>
Sonuçlar: <etkilenen dosyalar, görevler, geri alma yolu>
Kanıt: <bağlantı veya run_id>
```

## Kontrol listesi
- [ ] En az iki seçenek (yoksa nedeni)
- [ ] Geri alma yolu yazılı
- [ ] Etkilenen `tasks/` dosyaları güncellendi veya listelendi
- [ ] Eski ADR silinmedi, gerekiyorsa "yerini aldı" diye işaretlendi
