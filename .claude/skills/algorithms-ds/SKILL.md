---
name: algorithms-ds
description: 'Algoritma ve veri yapısı seçimini ve karmaşıklığını analiz etmek için kullan: eşleme, arama, toplama, indeks, matris işlemleri.'
---

# algorithms-ds

## Adımlar
1. Problemi girdi boyutlarıyla tanımla (ör. P paragraf, M madde, d boyut).
2. Mevcut çözümün zaman/bellek karmaşıklığını yaz (ör. tam eşleme O(P·M·d)).
3. Alternatifleri karşılaştır: ANN indeksi (HNSW/IVF), ön filtreleme, toplu matris çarpımı, önbellek.
4. Doğruluk etkisini belirt (yaklaşık arama recall kaybı) ve ölçüm öner (`embed-eval`).
5. Projeye özgü: unsur kapsama toplaması (ADR-008) madde başına alt unsur kümesi üzerinde OR-toplama; sınır durum: alt unsuru olmayan madde.

## Kontrol listesi
- [ ] Karmaşıklık gerçekçi boyutlarla sayıya döküldü (ör. 2.000 paragraf × 150 madde)
- [ ] Yaklaşık yöntemin doğruluk kaybı ölçüme bağlandı
