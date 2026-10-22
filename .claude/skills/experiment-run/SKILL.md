---
name: experiment-run
description: "Tez deneylerini tanımlamak, koşmak ve raporlamak için kullan: (a) taban çizgisi ile BERT karşılaştırması, (b) RAG'li, RAG'siz ve yer tutuculu üretimde sayı hatası, (c) doğrulama katmanı açık ve kapalıyken halüsinasyon, (m) maskeleme ile üretim kalitesi ve ablasyonlar. Tetikleyiciler: deney tanımı yazılacakken, bir kol eklenecekken, güven aralığı hesaplanacakken, tez tablosu üretilecekken."
---

# experiment-run

Deneyler tezin bilimsel katkısıdır; mühendislik tamam olsa bile deney tasarımı zayıfsa tez savunulamaz. Bu skill üç şeyi güvenceye alır:
- deneyin **önceden** tanımlanması (sonuç görülünce kol değiştirilmez);
- aynı veri ve tohumla karşılaştırma;
- her sayının bir `run_id`'ye bağlanması.

Deneylerin ayrıntılı tasarımı (kollar, metrik formülleri, örneklem): `references/experiments.md`.

## Adımlar

1. **Tanım:** `reports/experiments/<kod>-tanim.md`. İçinde şunlar bulunur:
   - araştırma sorusu ve hipotez;
   - kollar;
   - veri (sürüm; doğrulama mı altın mı);
   - birincil metrik ve ikincil metrikler;
   - tohum ve tekrar sayısı;
   - başarı ölçütü (ör. "BERT, taban çizgisinden F1'de en az 0,05 yüksek ve %95 aralıkları çakışmıyor").

   Tanımı kullanıcıya **onaylat**; onaydan sonra değişiklik yeni bir tanım sürümüdür.
2. **Altın küme kullanılıyorsa:** `python tools/gold_manifest.py verify` → 0. Değilse dur.
3. **Koş:** Her kol ayrı bir koşudur ve ayrı `run_id` alır (`colab-train`).
4. **Güven aralığı:** Kalem bazında sonuçları (`rapor_id`, `deger`) CSV'ye yaz ve gruplu bootstrap uygula:
   ```
   python .claude/skills/experiment-run/scripts/bootstrap_ci.py sonuclar-kolA.csv --grup rapor_id --deger dogru --seed 43
   ```
5. **Rapor:** `reports/experiments/<kod>-sonuc.md`. İçinde şunlar bulunur:
   - kollar tablosu (metrik, %95 aralık, n, run_id);
   - hata örnekleri (kol başına en az 5);
   - tanımdan sapmalar (varsa gerekçesiyle).

## Tuzaklar

- **Gruplu bootstrap.** Paragraflar rapor içinde bağımlıdır. Paragraf bazında bootstrap aralığı yapay olarak daraltır. 5'ten az rapor varsa betik uyarı verir; tezde yaz.
- **Kol eklemek.** Sonuçlar görüldükten sonra kol eklemek "çatallı yol" sorunudur. Gerekirse yeni bir tanım sürümü olarak eklenir ve tezde açıkça belirtilir.
- **Yer tutucu kolu (ADR-004) farklı bir şeyi ölçer.** Yer tutuculu üretimde serbest metinde sayı yapısal olarak yoktur; sayısal hata oranı tanım gereği sıfıra yakındır. Bu kol için birincil metrik **desteksiz iddia oranı** ve "VERİ EKSİK" oranıdır. Aksi hâlde karşılaştırma haksız olur.
- **İnsan değerlendirmesi** (Likert, iddia etiketi) için değerlendiriciler kolları **kör** görür; çıktıların sırası karıştırılır ve kol adı gizlenir.

## Örnek

Deney (b) sonuç tablosu biçimi (değerler örnektir):

| Kol | Sayısal hata oranı | %95 GA | Desteksiz iddia | n (taslak) | run_id |
|---|---|---|---|---|---|
| LLM, RAG yok | 0,31 | [0,24, 0,39] | 0,42 | 60 | 20270312-101500-s22 |
| RAG | 0,12 | [0,07, 0,18] | 0,15 | 60 | 20270312-111500-s22 |
| RAG + yer tutucu | 0,00 | — | 0,09 | 60 | 20270312-121500-s22 |

## Kontrol listesi

- [ ] Tanım koşudan önce yazıldı ve onaylandı
- [ ] Kollar aynı veri, aynı tohum
- [ ] Altın küme manifesti doğrulandı (kullanıldıysa)
- [ ] Her hücre bir run_id'ye bağlı; güven aralıkları gruplu bootstrap ile

## Dosyalar

- `scripts/bootstrap_ci.py`: rapor bazında gruplu bootstrap
- `references/experiments.md`: deney a, b, c ve m tasarımı
