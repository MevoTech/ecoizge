---
name: label-propose
description: "Rapor paragrafları için katalog maddelerine göre etiket önerisi (2 / 1 / U / NONE) üretmek için kullan. Tetikleyiciler: pilot etiketleme turu, toplu ön etiketleme, yeni bir raporun paragrafları hazır olduğunda. Çıktı yalnızca data/labels/proposals/ altına gider ve insan onayından geçmeden etiket sayılmaz."
---

# label-propose

Etiketleme kılavuzunu (`docs/labeling/etiket_kilavuzu_v0.md`) uygulayarak öneri üretir. Öneriler onay arayüzünde insan tarafından onaylanır, düzeltilir ya da reddedilir (`label-review`). Bu skill'in en önemli kuralı: **öneri, etiket değildir.** Tezdeki bütün P/R/F1 sayıları insan onaylı etiketlere dayanır.

## Ne zaman / ne zaman değil

- **Pilot körleme turu** (S05): önce `scripts/sample_pilot.py` ile örneklem seçilir. İnsan ve model aynı örneklemi **birbirini görmeden** etiketler. Bu turda insanın etiket dosyalarına bakma; görev paketinde verilmezler, guard da `data/labels/reviewed/` okumasını sana kapatır.
- **Toplu ön etiketleme** (S07 sonrası): kılavuz v1 hazır olduktan sonra.
- **Kullanma:** altın test kümesine girecek raporlar için öneri üretme (bu raporlar tamamen insan tarafından etiketlenir, R-ETK-02). Kılavuzu değiştirmek için de kullanma; belirsizlik raporlanır, kural uydurulmaz.

## Girdi / çıktı

| | Yol |
|---|---|
| Paragraflar | `data/processed/<rapor_id>/paragraphs.jsonl` (`pdf-extract` çıktısı) |
| Katalog | `data/catalog/catalog_v<N>.csv` (en yeni sürüm) |
| Kılavuz | `docs/labeling/etiket_kilavuzu_v<N>.md` |
| Model kararları (ara) | `kararlar.jsonl`: `{paragraf_id, madde_id, karsilama, guven, gerekce}` |
| Çıktı | `data/labels/proposals/<tur>-<rapor_id>-<YYYY-AA-GG>.csv` (`etiket_sablonu.csv` sütunları) |

## Adımlar

1. **Örneklem** (yalnızca pilot). Kanonik örneklem `data/labels/pilot/orneklem.jsonl`'dur; kör etiketleme ekranı yalnızca onu okur (C-02). Bu dizine sen yazamazsın: komutu orkestratör koşar ya da sen önerirsin.
   ```
   python .claude/skills/label-propose/scripts/sample_pilot.py data/labels/pilot/birimler/*.jsonl \
     --catalog data/catalog/catalog_v0.csv --aday 30 --rastgele 20 --seed 43 \
     --out data/labels/pilot/orneklem.jsonl --hints data/labels/proposals/pilot_ipuclari.json
   ```
   Örneklem insana gider; ipucu içermez. `data/labels/proposals/pilot_ipuclari.json` yalnızca senin içindir: her paragraf için en olası üç madde. Betik var olan örneklemin üzerine `--force` olmadan yazmaz: etiketleme başladıktan sonra örneklem değişirse etiketler sahipsiz kalır (kör ekran örneklemin SHA-256 özetini denetler ve durur).
2. **Her paragraf için karar ver.** Kılavuz §4'ü sırayla uygula:
   1. Paragrafın konusu hangi maddelerin `baslik` ve `gereklilik_ozeti` alanlarıyla örtüşüyor?
   2. Madde kaç unsurdan oluşuyor; paragraf bunların kaçını karşılıyor?
   3. Bilgi şirkete özgü ve somut mu?
   4. Madde sayısal ise değer, birim ve dönem var mı?

   Kararları `kararlar.jsonl`'a yaz. Hiçbir maddeyle ilgisi olmayan paragraf için de **açıkça** `{"madde_id": "NONE", "karsilama": "NONE", ...}` satırı yaz.
3. **Güven puanı:** 0,9 ve üstü yalnızca kılavuzdaki bir örnekle birebir örtüşen durumlar için. Kılavuz §5'teki sınır durumlar en fazla 0,6. Kılavuzun kapsamadığı durumlarda `gerekce` alanı `kılavuz-belirsiz:` ile başlar ve güven en fazla 0,5 olur.
4. **Gerekçe:** en fazla iki cümle. Hangi unsurun var ya da eksik olduğunu ve kılavuzun hangi bölümüne dayandığını yaz (ör. "Organ adı var, sıklık yok (§4.2).").
5. **Dönüştür ve doğrula:**
   ```
   python .claude/skills/label-propose/scripts/to_proposals.py --paragraphs data/labels/pilot/orneklem.jsonl \
     --judgments kararlar.jsonl --out data/labels/proposals/pilot_v0.csv --tarih 2026-10-23
   ```
   Kararı olmayan bir paragraf, bilinmeyen bir madde ya da geçersiz bir değer varsa betik dosyayı **yazmaz** ve 1 ile çıkar.
6. Orkestratöre raporla: dosya yolu, paragraf sayısı, düzey dağılımı ve `kılavuz-belirsiz` satırlarının listesi.

## Tuzaklar

- **Aday yanlılığı.** Yalnızca ipucundaki maddelere bakma. İpucu, kelime örtüşmesidir. "Yönetim Kurulu yılda iki kez bilgilendirilir" cümlesi "gözetim" kelimesini içermez, ama `TSRS2-YON-06a-iii` maddesini karşılar.
- **Genel cümle 2 alamaz.** "Şirketimiz iklim konularında yönetim kurulunu düzenli olarak bilgilendirmektedir" en fazla 1'dir: yöntem ve sıklık yok, herhangi bir şirket yazabilir. Bu ayrım `s_spec` skorunun eğitim verisidir (ADR-007); gevşek olursa model de gevşek öğrenir.
- **Tek paragraf, çok madde.** Bir emisyon tablosu `TSRS2-MET-29a-i` maddesine ve VSME B3 maddesine aynı anda karşılık gelebilir. Her ilişki ayrı satırdır.
- **Çapraz atıf.** "Ayrıntılar için bkz. s. 40" paragrafı, atıf yaptığı madde için NONE'dur; atıf yapılan sayfa ayrıca etiketlenir (kılavuz §5.3).
- **Dönemsiz sayı en fazla 1'dir** (kılavuz §5.5). Bağlamda yıl başlıkta geçiyorsa (ör. "2024 Performans Göstergeleri") dönem var sayılır; gerekçeye yaz.
- **Muafiyet beyanı** ("Kapsam 3 geçiş hükmü nedeniyle açıklanmamıştır") ilgili alt unsur için 2'dir. Kural kılavuz §5.1'de açık soru olarak duruyor; güven en fazla 0,6.

## Örnek

Ayrıntılı çözümlü örnekler: `references/worked_examples.md`. Kısa örnek:

| Paragraf | Madde | Öneri | Güven | Gerekçe |
|---|---|---|---|---|
| "Sürdürülebilirlik Komitesi iklim konularında yönetimden üç ayda bir yazılı rapor alır ve yılda iki kez Yönetim Kurulu'na sunum yapar." | `TSRS2-YON-06a-iii` | 2 | 0,90 | Bilgilendirme yöntemi (yazılı rapor, sunum) ve sıklığı (üç ayda bir, yılda iki kez) var (§4). |
| "2024'te Kapsam 1 emisyonumuz 12.450 tCO2e, Kapsam 2 (lokasyon bazlı) emisyonumuz 31.200 tCO2e'dir." | `TSRS2-MET-29a-i` | 1 | 0,80 | Kapsam 1 ve 2 değer, birim ve dönemle var; Kapsam 3 yok (§4.2). |
| "Şirketimiz 1985 yılında kurulmuştur." | `NONE` | NONE | 0,95 | Tarihsel bilgi; hiçbir madde içeriği yok (§5.7). |

## Kontrol listesi

- [ ] Pilot turda insan etiketleri görülmedi
- [ ] Her paragraf için en az bir karar satırı var (NONE dahil)
- [ ] `to_proposals.py` 0 ile çıktı (doğrulayıcı dahil)
- [ ] `kılavuz-belirsiz` satırları orkestratöre listelendi

## Dosyalar

- `scripts/sample_pilot.py`: aday + rastgele, raporlar arası dengeli, tekrarlanabilir örneklem
- `scripts/to_proposals.py`: karar JSONL → doğrulanmış öneri CSV'si
- `references/worked_examples.md`: kılavuzdaki sınır durumlar için çözümlü örnekler
