---
name: embed-eval
description: Aday embedding modellerini kendi altın/doğrulama kümemizde retrieval başarısıyla karşılaştırmak için kullan (Recall@k, MRR).
---

# embed-eval

## Girdi
Madde metinleri (katalog), etiketli paragraf × madde çiftleri (2 veya 1 olanlar pozitif), aday model listesi.

## Adımlar
1. Her aday için madde ve paragraf vektörlerini üret (aynı ön işleme, aynı kesme uzunluğu).
2. Her madde için paragrafları kosinüsle sırala; Recall@{5,10,20} ve MRR hesapla.
3. Rapor bazında gruplu sonuç ver; ortalama + bootstrap %95 aralık.
4. Süre ve bellek (Colab T4/CPU) yaz; çok büyük model pratik değilse belirt.
5. Sonuç `evaluator`'a; karar ADR (B2).

## Adaylar (başlangıç, doğrulanacak)
multilingual-e5-base/large, TR-MTEB yazarlarının Türkçe modeli, bge-m3 (Türkçe başarısı doğrulanmadı), ham BERTurk (taban).

## Kontrol listesi
- [ ] Altın test kümesi değil doğrulama kümesi kullanıldı (seçim aşaması)
- [ ] Tüm adaylar aynı çiftlerde ölçüldü
