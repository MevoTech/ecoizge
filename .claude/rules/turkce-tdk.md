# Türkçe dil ve TDK yazım kuralları

Projenin girdisi Türkçe raporlardır, çıktısı Türkçe taslaktır. Belgeler, arayüz metinleri, istemler ve üretilen taslaklar Türkçe yazılır ve TDK Yazım Kılavuzu'na uyar. Kod içi tanımlayıcılar ASCII kalır (ör. `dil_tahmini`, `rapor_id`).

## Yazım (TDK)

- Sayılar: binlik ayracı nokta, ondalık ayracı virgül: `12.450,5`. Dört basamaklı sayılarda nokta isteğe bağlıdır, projede kullanılır: `1.250`.
- Yüzde işareti sayıdan önce, bitişik: `%12`, `%12,5`. Ek alırken kesme işareti kullanılır: `%12'si`.
- Birimler sayıdan bir boşlukla ayrılır: `12.450 ton CO₂e`, `3,2 GWh`.
- Tarih: `31 Aralık 2025` ya da `31.12.2025`. Belirli bir tarih bildiren ay adı büyük harfle başlar; tarih bildirmiyorsa küçük yazılır ("aralık ayında").
- Özel adlara gelen ekler kesme işaretiyle ayrılır: `TSRS 2'ye`, `KAP'ta`, `Borsa İstanbul'un`. Kısaltmaya gelen ek, kısaltmanın okunuşuna uyar: `KGK'nin`, `TSRS'nin`.
- "de/da" bağlacı ayrı, ek bitişik yazılır; "ki" bağlacı ayrı yazılır. "-mı/-mi" soru eki ayrı yazılır.
- Yabancı terimlerin Türkçe karşılığı varsa o kullanılır: "kapsam 1 emisyonları", "gözetim", "geçiş planı". Karşılığı yerleşmemiş terim ilk geçişte ayraç içinde verilir: "sera gazı (GHG)".

## Kodda Türkçe metin

- Büyük/küçük harf dönüşümü Türkçe kurallıdır: `I → ı`, `İ → i`. Python'un `str.lower()` bunu yapmaz; `tools/rapor_derlemi.py` içindeki `tr_kucuk` ya da eşdeğeri kullanılır.
- Sayı ve birim ayrıştırma yalnızca `report_service.verify.numbers` üzerinden yapılır (`.claude/rules/python.md`). Biçimlendirme `format_tr` ile yapılır; `f"{x:,}"` kullanılmaz (İngilizce ayraç üretir).
- Dosyalar UTF-8'dir. Dosya adı ve kimlik üretilirken Türkçe harfler ASCII'ye çevrilir (`slug`): `Batıcım` → `baticim`.
- PDF çıkarımında Türkçe harf kaybı (`ş → ·`, `ı → ·`) bir çıkarım hatasıdır; `pdf-extract` QA raporunda izlenir.

## Derlem

- Derlemdeki her raporun dili `tools/rapor_derlemi.py` ile tahmin edilir (`tr`, `en`, `karisik`, `belirsiz`). Etiketleme ve eğitim yalnızca `tr` raporlarla yapılır; `karisik` raporlar paragraf düzeyinde süzülür.
- `belirsiz` çoğunlukla taranmış PDF'tir; OCR gerekir (`ocr_gerekli`).
