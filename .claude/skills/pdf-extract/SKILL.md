---
name: pdf-extract
description: Rapor PDF'inden paragraf ve tabloları sayfa ve başlık bağlamıyla çıkarmak ve çıkarım kalitesini ölçmek için kullan.
---

# pdf-extract

## Girdi
`data/raw/public/<rapor>.pdf` (kamu sınıfı); rapor kimliği.

## Çıktı
`data/processed/<rapor_id>/paragraphs.jsonl`: her satır `{paragraf_id, rapor_id, sayfa, bolum_basligi, tur: paragraf|tablo, metin, kaynak: metin|ocr}`.

## Adımlar
1. Metin katmanını kontrol et; yoksa `computer-vision`.
2. Blokları sayfa sırasıyla çıkar; üst bilgi/alt bilgi tekrarlarını at; başlık hiyerarşisini yazı boyutundan çıkar.
3. Tablo + başlığını tek birim yap (kılavuz §2).
4. Türkçe karakter ve tirelemeyi onar (satır sonu `-` birleştirme).
5. Kalite: QA kümesinde (S04) elle kontrol edilen sayfalarla karşılaştır; hata türlerini say (kırık tablo, karışık sütun, eksik metin).

## Kontrol listesi
- [ ] Her paragrafın sayfa numarası doğru (QA örneklemi)
- [ ] Çıkarım hatası listesi `reports/experiments/extraction-qa-<tarih>.md` (evaluator)
- [ ] Kütüphane seçimi ölçümle (ADR)
