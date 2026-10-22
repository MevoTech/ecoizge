---
name: computer-vision
description: 'Görsel içerikten metin ve tablo çıkarmak için kullan: taranmış PDF sayfası, görsel tablo, grafik. Yalnızca pdf-extract metin katmanı bulamadığında.'
---

# computer-vision

## Durum
**Etkin değil**, koşullu: `pdf-extract` bir sayfada metin katmanı bulamazsa tetiklenir.

## Adımlar
1. Sayfayı görüntüye çevir (300 dpi).
2. OCR: Tesseract (`tur` dil paketi) veya eşdeğeri; güven skoru düşük satırları işaretle.
3. Tablo: hücre tespiti; sonucu `pdf-extract` çıktı biçimine dönüştür, `kaynak = ocr`.
4. Kalite: çıkarım QA kümesindeki OCR sayfalarında karakter hata oranı raporlanır.

## Kontrol listesi
- [ ] OCR'dan gelen paragraflar etiketlemede ayrı işaretli
- [ ] Sayılar `numeric-verify` normalleştiricisinden geçti
