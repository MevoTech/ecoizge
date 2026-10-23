---
name: figure-extract
description: "Rapor PDF'indeki grafik ve şekilleri bulmak, vektör grafiklerde yazılı veri etiketlerinden (kategori, seri, değer) veri okumak ve verisi okunamayan grafikleri (görüntü, yazısı çizime çevrilmiş) açıkça işaretlemek için kullan. Tetikleyiciler: 'grafikteki değerler', 'şekil verisi', grafik kaynaklı bir sayının doğrulanması, Docling resim sınıflandırması, chart-to-table denemesi."
---

# figure-extract

Grafikteki veri üç biçimde bulunur ve doğruluk düzeyi farklıdır (R-TAB-04, ADR-014):

| Durum (`veri_durumu`) | Ne var | Ne yapılır | Doğruluk |
|---|---|---|---|
| `vektor_etiket` | Çubuklar PDF çizimi, değerler yazı (Akbank 2025 Şekil 6) | Etiket → çubuk → kategori (eksen yazısı) ve seri (lejant rengi) eşlenir | **Kesin** (değer yazıdan okunur) |
| `yalniz_etiket` | Sayısal etiketler var ama eşleme kurulamadı (pasta, çizgi) | Veri okunmaz, metin saklanır | — |
| `goruntu_veri_yok` | Görüntü ya da yazısı çizime çevrilmiş grafik (Akbank 2025 Şekil 5) | Veri okunmaz; uyarı `goruntu_veri_cikarilmadi` | — |
| `veri_yok` | Başlıklı diyagram, akış şeması | Veri beklenmez | — |

**Kural:** Çubuğun boyundan ölçek tahmini yapılmaz; etiketi olmayan çubuğa değer verilmez (uydurma sonuç yasağı). Görüntüden veri (chart-to-table) yalnızca yaklaşık olabilir; yapılırsa `yaklasik` diye işaretlenmeli ve ayrı ölçülmelidir (KL-14).

## Ne zaman / ne zaman değil

- **Kullan:** `table-extract` ile aynı komutta (`pipelines/structure.py` şekilleri de yazar); grafik kaynaklı bir sayı taslağa girecekse.
- **Kullanma:** Görüntü grafikleri bulut görüntü modeline göndermek için (pilot verisi harici API'ye gitmez, ADR-011; kamu raporu için de yeni servis insan onayı ister).

## Girdi / çıktı

| | Yol | Biçim |
|---|---|---|
| Girdi | PDF; tablo alanları (`tables.jsonl`'dan, tablolar şekil sayılmaz) | |
| Çıktı | `data/processed/<rapor_id>/figures.jsonl` | `sekil-0.1`: `sekil_id`, `sayfa`, `bbox`, `tur` (grafik/sekil), `baslik`, `metin`, `veri[]` ({kategori, seri, deger, ham, bbox}), `veri_durumu`, `eslesmeyen_etiket`, `motor`, `sinif` (Docling resim sınıfı), `uyarilar` |

## Adımlar

1. `pipelines/structure.py` koşulduysa `figures.jsonl` hazırdır (`table-extract` Adımlar 2). `--motor docling` ile Docling'in resim sınıflandırıcısı (DocumentFigureClassifier) her resme `sinif` ekler; PyMuPDF'in bulmadığı grafik resimleri yeni kayıt olur.
2. Özet ve kontrol listesi:
   ```
   python .claude/skills/figure-extract/scripts/sekil_ozeti.py data/processed/<id>/figures.jsonl --pdf data/raw/public/sirket/<pdf>
   ```
3. "Verisi okunan grafikler" tablosunu insan PDF ile karşılaştırır: kategori, seri ve değer doğru mu? `eslesmeyen_etiket` > 0 ise o grafikte okunmayan etiket vardır (ör. çubuğu olmayan "0").
4. "Şekil kaydı olmayan" başlıklı sayfalara PDF'te bak: grafik görüntü mü, yazı çizime mi çevrilmiş? Bu durumlar KL-14 kapsamındadır.
5. Hata → `tests/pipelines/test_figures.py`'ye kırmızı test, sonra `pipelines/figures.py`.

## Tuzaklar (2026-10-23 denemeleri)

- **Tablo başlık dolgusu çubuk sanıldı.** Akbank 2025 s. 6'da kırmızı dolgulu "2024 / 2025" başlık hücreleri çubuk, yıllar değer sanıldı. Eşit boylu gruplar çubuk grafik sayılmaz; yıl etiketi değer değildir; tablo alanları (`tables.jsonl`) şekil aramasından çıkarılır.
- **Yazısı çizime çevrilmiş grafik.** Akbank 2025 Şekil 5'te rakamlar metin değil çizim (glif yolu): metin katmanı yok, değer okunamaz. OCR ya da görüntü modeli gerekir (KL-14).
- **Bir yolda birden çok çubuk.** Bazı PDF üreticileri bütün çubukları tek çizim yolunda toplar; yol içindeki her `re` ayrı çubuk sayılır.
- **Eksen işaretleri değer değildir:** dikey grafikte çubukların solundaki, yatayda altındaki sayılar.
- **Lejant:** küçük kare (≤ 12 pt) + hemen sağındaki yazı; çubuk rengi lejant rengiyle eşleşirse seri adı verilir, lejant yoksa `seri: null`.
- **Başlık uzaklığı:** grafik ile "Şekil N" başlığı arasında lejant olabilir; başlık 80 pt içinde aranır.

## Örnek

Girdi: Akbank 2025 s. 27 sağ grafik, "Şekil 6: 2025 Yılında Sektör Bazlı Çevresel ve Sosyal Etki Kapsamında Değerlendirilen Kredi Sayısı" (yatay çubuk, değerler çubuğun sağında).

Çıktı (`veri_durumu: vektor_etiket`, 2026-10-23 koşusu):
```
Toplam=27; Lojistik=1; Enerji=5; Turizm=1; İmalat=8; Gayrimenkul=2; Hizmet=1; Madencilik=1; Altyapı=8 (eşleşmeyen 0)
```
Aynı sayfadaki sol grafik (Şekil 5) yazısı çizime çevrilmiş olduğundan okunmadı.

## Kontrol listesi

- [ ] `python -m pytest -q tests/pipelines/test_figures.py` geçti
- [ ] `validate_data.py <...>/figures.jsonl` hata vermedi
- [ ] Verisi okunan her grafik insan tarafından PDF ile karşılaştırıldı
- [ ] Okunamayan grafik kaynaklı sayı taslağa **girmedi** (ADR-004: sayı yalnızca kaynak kayıttan)

## Dosyalar

- `pipelines/figures.py`: grafik bölgesi, çubuk grupları, etiket–çubuk–kategori–seri eşlemesi (sahibi `ml-engineer`)
- `pipelines/structure.py`: Docling resim sınıflarının eklenmesi (`resimleri_ekle`)
- `scripts/sekil_ozeti.py`: özet ve elle kontrol listesi
