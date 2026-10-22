---
name: agreement-kappa
description: "İki etiketleyici arasındaki uyumu ağırlıklı Cohen's kappa ile ölçmek ve anlaşmazlıkları kılavuz iyileştirmesine çevirmek için kullan. Tetikleyiciler: pilot körleme turu bittiğinde, ikinci insan etiketleyici alt kümeyi bitirdiğinde, kılavuz yeni sürüme geçmeden önce."
---

# agreement-kappa

Kappa (κ) iki şeyi gösterir: kılavuzun ne kadar net olduğunu ve etiketlerin tezde ne kadar güvenilir sayılabileceğini. Bu projede iki ayrı κ raporlanır (ADR-012):
1. **İnsan–model:** Mehmet ile `annotation-assistant`. Bu bir *etiketleyici uyumu* değildir; modelin kılavuzu ne kadar izlediğini gösterir.
2. **İnsan–insan:** Mehmet ile Zemzem, 30–50 paragraflık alt kümede. Tezde etiket güvenilirliği olarak yalnızca bu raporlanır.

## Adımlar

1. İki dosyanın da **bağımsız** üretildiğini doğrula: körleme, aynı örneklem, aynı katalog ve kılavuz sürümü.
2. Hesapla:
   ```
   python tools/kappa.py A.csv B.csv --weights quadratic --out reports/experiments/kappa-<tur>-<tarih>.md
   ```
3. Raporu oku:
   - ortak paragraf sayısı;
   - κ'ya giren çift sayısı;
   - U içeren çift sayısı;
   - κ değeri;
   - anlaşmazlık listesi.
4. Anlaşmazlıkları türe ayır (`references/interpretation.md`): ölçek kayması (2↔1), madde seçimi (biri madde buldu, diğeri NONE dedi), sınır durum (§5), çıkarım hatası.
5. Her tür için kılavuz önerisi yaz: yeni örnek, kural netleştirmesi ya da yeni sınır durum satırı. Kılavuzu değiştirmek kullanıcı onayı gerektirir; öneriyi orkestratöre ver.

## Hesap tanımı (`tools/kappa.py`)

- Anahtar `(paragraf_id, madde_id)`. Yalnızca **iki dosyada da incelenmiş** paragraflar karşılaştırılır. Bir tarafın yazmadığı çift NONE sayılır.
- Sıralı ölçek: NONE = 0, 1 = 1, 2 = 2. Kareli ağırlıkta 2↔NONE anlaşmazlığı, 2↔1'in dört katı cezalandırılır.
- `U` sıralı ölçeğe girmez. U içeren çiftler ayrıca sayılır; anlaşmazlıklarda listelenir.
- Doğruluk kontrolü: referans değerler scikit-learn `cohen_kappa_score` ile bağımsız olarak hesaplanıp `tests/tools/test_kappa.py`'de sabitlendi.

## Tuzaklar

- **50 paragrafta κ'nın güven aralığı geniştir.** Pilotun amacı κ değeri değil, kılavuz belirsizliğini bulmaktır. Tezde değeri örneklem büyüklüğüyle birlikte yaz.
- **NONE baskınlığı κ'yı düşürür ya da şişirir.** Çiftlerin çoğu NONE–NONE ise gözlenen uyum yüksek görünür, beklenen uyum da yükselir. Raporda düzey dağılımını da ver.
- **Model önerisini görüp onaylamak bağımsız etiket değildir.** Onay arayüzündeki onaylar κ hesabında *ikinci etiketleyici* olarak kullanılamaz.
- Landis–Koch eşikleri ("0,61–0,80 önemli uyum") yaygın ama keyfidir. Tezde değeri yorumlarken anlaşmazlık türlerini öne koy.

## Örnek

```
# Uyum raporu
- Ortak paragraf: 50 · çift: 71 · κ'ya giren: 68 · U içeren çift: 3
- Ağırlıklı κ (quadratic): **0.712**
## Anlaşmazlıklar
| paragraf_id | madde_id | A | B |
| karel-2025-p014-02 | TSRS2-YON-06a-iii | 2 | 1 |
| karel-2025-p031-01 | TSRS2-MET-29a-i | 1 | NONE |
```
Bu rapordan çıkan kılavuz önerisi: "p014-02'de sıklık 'düzenli olarak' diye geçiyor. §4.3'e 'belirsiz sıklık ifadesi = 1' örneği eklenmeli."

## Kontrol listesi

- [ ] Dosyalar bağımsız, aynı örneklem ve sürümler
- [ ] Rapor `reports/experiments/` altında
- [ ] Anlaşmazlıklar türe ayrıldı, kılavuz önerisi yazıldı
- [ ] İnsan–model ve insan–insan κ ayrı raporlandı

## Dosyalar

- `tools/kappa.py`: hesap (testli)
- `references/interpretation.md`: anlaşmazlık türleri ve kılavuza dönüştürme
