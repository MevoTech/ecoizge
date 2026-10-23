---
name: pdf-extract
description: "Bir sürdürülebilirlik raporu PDF'ini paragraf ve tablo birimlerine ayırmak ve çıkarım kalitesini ölçmek için kullan. Tetikleyiciler: yeni rapor PDF'i geldiğinde, paragraphs.jsonl üretilecekken, etiketlemeden önce, çıkarım hatası şüphesinde (bozuk tablo, karışık sütun, eksik metin)."
---

# pdf-extract

Etiketlemenin, boşluk analizinin ve RAG'in girdisi olan birimleri (paragraf ve tablo) üretir. Tablo burada **tek bir metin birimidir**; hücre ızgarası, başlık rolü, birim, dönem ve grafik verisi için `table-extract` ve `figure-extract` skill'lerine geç (S28, ADR-014). Buradaki bir hata zincirin geri kalanında **model hatası gibi görünür**. Örneğin bozuk çıkarılmış bir tablo yüzünden madde "eksik" işaretlenir. Bu yüzden çıkarım her rapor için ayrıca ölçülür (R-PDF-02, bulgu B14).

## Ne zaman / ne zaman değil

- **Kullan:** `data/raw/public/` altına yeni bir kamu raporu geldiğinde; çıkarım kodu değiştiğinde (tüm raporlar yeniden çıkarılır ve QA tekrarlanır).
- **Kullanma:** pilot firma verisi için (`data/raw/pilot/` ajanlara kapalı, ADR-011). Taranmış sayfalar için de kullanma; bunlar `ocr_gerekli` listesinde raporlanır ve OCR şimdilik kapsam dışıdır (orkestratöre bildir).

## Girdi / çıktı

| | Yol | Biçim |
|---|---|---|
| Girdi | `data/raw/public/<rapor_id>.pdf` | Kamu sınıfı PDF; `rapor_id` = `sirket-yil`, ör. `karel-2025` |
| Çıktı | `data/processed/<rapor_id>/paragraphs.jsonl` | Satır başına `{paragraf_id, rapor_id, sayfa, bolum_basligi, tur: paragraf\|tablo, metin, kaynak: metin}` |
| QA | `reports/experiments/extraction-qa-<rapor_id>.md` | `scripts/qa_report.py` çıktısı + insanın doldurduğu elle kontrol tablosu |

`paragraf_id` biçimi `<rapor_id>-p<sayfa:3>-<sıra:2>` (ör. `karel-2025-p012-03`). Etiketler bu kimliğe bağlanır. Çıkarım kodu değişirse kimlikler kayabilir; aşağıdaki "Tuzaklar" bölümüne bakın.

## Adımlar

1. Bağımlılık: `pip install -r requirements-train.txt` (PyMuPDF; onay durumu dosyada yazılı).
2. Çıkar:
   ```
   python pipelines/extract.py data/raw/public/karel-2025.pdf --rapor-id karel-2025 --out data/processed/karel-2025/paragraphs.jsonl
   ```
   Özet satırını oku: birim sayısı, tablo sayısı, atılan üst/alt bilgi, `OCR gereken sayfalar`.
3. Otomatik QA ve elle kontrol örneklemi:
   ```
   python .claude/skills/pdf-extract/scripts/qa_report.py data/processed/karel-2025/paragraphs.jsonl --sayfa 20 --seed 43
   ```
   Çıktıyı `reports/experiments/extraction-qa-karel-2025.md` olarak kaydettir (`evaluator` yazar).
4. İnsan, listelenen 20 sayfayı PDF ile yan yana açıp elle kontrol tablosunu doldurur (eksik metin, fazla metin, kırık tablo, sütun karışması, yanlış başlık). Bu bir **onay noktasıdır**.
5. İşaretli birim oranı %5'i geçerse ya da elle kontrolde sistematik bir hata çıkarsa etiketlemeye geçme. Hatayı `tests/pipelines/test_extract.py`'ye önce başarısız bir test olarak ekle, sonra `pipelines/extract.py`'yi düzelt.

## Tuzaklar (bu projede gerçekten yaşananlar)

- **Tablo hücrelerinde Türkçe binlik ayracı bozulur.** PyMuPDF'in `table.extract()` metodu "12.450" sayısını "12 450 ." olarak verir. Bu yüzden `extract.py` hücre metnini hücre alanından okur (`page.get_text(clip=...)`). Başka bir kütüphane denenecekse önce bu testi koş.
- **Tireleme.** Yalnızca tire küçük harfle devam ediyorsa birleştirilir ("sürdürüle-" + "bilirlik"). "Kapsam 1-" + "Kapsam 2" birleştirilmez. Büyük harfle başlayan özel adlarda hatalı birleşme olabilir; QA'da `tire_kalintisi` işaretine bak.
- **Üst ve alt bilgi.** Rakamlar normalleştirilip ("Sayfa 3" → "sayfa #") sayfaların en az yarısında tekrarlanan bant metni atılır. İki sayfalık bir PDF'te her iki sayfada da geçen gerçek bir başlık atılabilir. Kısa raporlarda `atilan_ust_alt` sayısını kontrol et.
- **Başlık tespiti yazı boyutuna dayanır** (gövdenin ≥ 1,15 katı, kısa, noktasız). Başlıkları kalın ama aynı boyutta yazan raporlarda `bolum_basligi` boş kalır (QA'da `basliksiz` işareti). Bu durum etiketlemeyi engellemez, ama bağlam zayıflar.
- **İki sütunlu sayfalar.** Bloklar dikey konuma göre sıralanır; iki sütunlu düzende sol ve sağ sütun karışabilir. Elle kontrolde "sütun karışması" sütununu doldur.
- **Sayfa sonunda bölünen tablo** (Derimod 2025, s. 22→23 ve 25→26). `paragraphs.jsonl`'da tablonun devamı ayrı bir birimdir ve başlık satırı olmadığı için ilk sütunları boş gelir (`| | | …`). Etiketlemede iki birimi birlikte oku. Yapısal çıktıda (`table-extract`, `tables.jsonl`) birleştirme yapılır; `paragraphs.jsonl` etiket kimlikleri yüzünden değiştirilmez (KL-02).
- **Kenarlıksız tablo** (Klimasan 2025 s. 37): `find_tables` bulamaz, metin paragraf birimlerine dağılır. Yapısal çıktıda sezgisel motor ya da Docling bulur (`table-extract`, KL-13).
- **Kapak ve arka kapak görsel olabilir.** Derimod 2025'te s. 2 ve 60 metinsiz çıktı (`ocr_gerekli`). Bu sayfalar çoğu zaman yalnızca görseldir; OCR ihtiyacına karar vermeden önce PDF'te bak.
- **Kimlik kayması.** Çıkarım kodu değişince aynı paragrafın sırası değişebilir. Etiketlenmiş bir raporu **yeniden çıkarmadan önce** orkestratöre sor; etiketlerin eşlenmesi gerekir.

## Örnek

Girdi: iki sayfalık bir rapor. 1. sayfada "Yönetişim" başlığı ve iki paragraf; 2. sayfada "Tablo 1. Sera gazı emisyonları" başlıklı 3×2 bir tablo ve bir paragraf var; her sayfada üst ve alt bilgi var.

Çıktı (`tests/pipelines/test_extract.py` ile doğrulanan davranış):
```
{"paragraf_id": "karel-2025-p001-01", "sayfa": 1, "bolum_basligi": "Yönetişim", "tur": "paragraf", "metin": "Sürdürülebilirlik Komitesi … üç ayda bir yazılı rapor alır …"}
{"paragraf_id": "karel-2025-p001-02", "sayfa": 1, "bolum_basligi": "Yönetişim", "tur": "paragraf", "metin": "Şirketimiz … sürdürülebilirlik stratejisinin merkezine almıştır."}
{"paragraf_id": "karel-2025-p002-01", "sayfa": 2, "bolum_basligi": "Metrikler", "tur": "tablo", "metin": "Tablo 1. Sera gazı emisyonları\nKapsam | 2024 (tCO2e)\nKapsam 1 | 12.450\nKapsam 2 | 31.200"}
{"paragraf_id": "karel-2025-p002-02", "sayfa": 2, "bolum_basligi": "Metrikler", "tur": "paragraf", "metin": "Kapsam 3 emisyonları geçiş hükmü kapsamında …"}
```
Üst ve alt bilgi ("Karel Sürdürülebilirlik Raporu 2025", "Sayfa 1") çıktıda yer almaz.

## Kontrol listesi

- [ ] `python -m pytest tests/pipelines -q` geçti (PyMuPDF kuruluyken)
- [ ] Özet satırında `OCR gereken sayfalar: yok`; varsa orkestratöre bildirildi
- [ ] QA raporu kaydedildi, elle kontrol tablosu insan tarafından dolduruldu
- [ ] İşaretli birim oranı < %5 ya da her işaret açıklandı

## Dosyalar

- `pipelines/extract.py`: çıkarım (sahibi `ml-engineer`)
- `scripts/qa_report.py`: otomatik işaretler ve elle kontrol örneklemi
- `tests/pipelines/test_extract.py`: sentetik Türkçe PDF ile davranış testleri
