---
name: embed-eval
description: "Aday embedding modellerini kendi etiketli verimizde retrieval başarısıyla (Recall@k, MRR) karşılaştırıp seçmek için kullan. Tetikleyiciler: retrieval modeli seçilecekken (S13), yeni bir Türkçe/çok dilli model çıktığında, pgvector boyutu sabitlenmeden önce."
---

# embed-eval

Retrieval iki yerde kullanılır: boşluk analizinde madde → aday paragraflar, RAG'de madde → kaynaklar. Model seçimi **genel benchmark'a göre değil, kendi verimize göre** yapılır. TR-MTEB genel alanı ölçer; sürdürülebilirlik raporu dili farklıdır (bulgu B2). Seçilen modelin vektör boyutu veritabanı şemasını belirler (`docs/DATA_MODEL.md`, `report_chunk.embedding`). Bu yüzden karar ADR ile sabitlenir.

## Adımlar

1. **Sorgu kümesi:** onaylı etiketlerden her (rapor, madde) için ilgili paragraflar (düzey 1 veya 2). Altın küme raporları kullanılmaz.
2. **Vektör üretimi (Colab, `colab-train`):** Her aday için madde metni (`baslik` + `gereklilik_ozeti`) ve o rapordaki tüm paragraflar kodlanır. Modelin istediği önekler uygulanır (e5 ailesinde `query:` ve `passage:`). Kesme uzunluğu tüm adaylarda aynıdır.
3. Her sorgu için paragraflar kosinüse göre sıralanır ve `siralama.json` yazılır (biçim: `scripts/retrieval_metrics.py` belgesi).
4. Metrikleri hesapla:
   ```
   python .claude/skills/embed-eval/scripts/retrieval_metrics.py siralama-e5-base.json --k 5 10 20
   ```
5. Karşılaştırma tablosunu `evaluator`'a ver: model, Recall@5/10/20, MRR, süre, bellek, vektör boyutu. Karar ADR olur (`adr`).

## Adaylar ve başlangıç kanıtı

`references/candidates.md`'de. Özet: TR-MTEB'de `multilingual-e5-large` ortalamada en iyi (66,82). Ham BERTurk retrieval'da zayıf (34,82). `bge-m3` TR-MTEB'de yok, ölçülmesi gerekiyor.

## Tuzaklar

- **Önek unutmak.** e5 ailesi `query:` ve `passage:` önekleri olmadan belirgin şekilde kötüleşir. Bu bir model hatası değil, kullanım hatasıdır.
- **Rapor içi arama.** Sıralama yalnızca **aynı rapordaki** paragraflar arasında yapılır; üretimde de retrieval şirket ve rapor kimliğiyle filtrelenir (R-RET-02). Tüm derlem üzerinde sıralamak sonuçları değiştirir.
- **İlgilisiz sorgular** (raporda o madde yok) Recall'a girmez; sayısı ayrıca raporlanır. Bunlar boşluk analizinin "eksik" doğru tespitleri için önemlidir, ama retrieval metriğinde tanımsızdır.
- **Colab bellek sınırı.** Büyük modeller (large) T4'te toplu kodlamada yavaştır. Süre tabloya yazılır; pratik değilse bu bir karar gerekçesidir.

## Örnek

```json
{"metrikler": {"recall@5": 0.71, "recall@10": 0.83, "recall@20": 0.92, "mrr": 0.58}, "rapor_sayisi": 8, "ilgilisiz_sorgu": 37, "model": "multilingual-e5-base"}
```
(örnek değerler; gerçek sonuçlar PROGRESS'e `run_id` ile yazılır)

## Kontrol listesi

- [ ] Tüm adaylar aynı sorgularda, aynı kesme uzunluğuyla
- [ ] Önekler modele uygun
- [ ] Altın küme kullanılmadı
- [ ] Süre, bellek ve boyut tabloda; karar ADR

## Dosyalar

- `scripts/retrieval_metrics.py`: Recall@k, MRR (rapor bazında ortalama)
- `references/candidates.md`: aday listesi ve kaynakları
