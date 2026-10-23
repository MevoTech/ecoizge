---
name: table-eval
description: "Tablo çıkarımını insan altın kümesine karşı ölçmek için kullan: tespit P/R/F1, yapı (GriTS_Con, GriTS_Top) ve olgu düzeyi P/R/F1; altın tablo kümesinin insan tarafından hazırlanması ve PyMuPDF ile Docling motorlarının karşılaştırılması. Tetikleyiciler: tablo çıkarım kodu ya da motoru değişti, 'tablolar doğru mu' sorusu, S28 kapanışı, tez çıkarım tablosu."
---

# table-eval

Tablo çıkarımının doğruluğu üç düzeyde ölçülür; biri iyi diğeri kötü olabilir (R-TAB-05):

| Düzey | Ölçüt | Neyi yakalar |
|---|---|---|
| Tespit | P/R/F1 (aynı sayfa, IoU ≥ 0,5; altında kutu yoksa GriTS_Con ≥ 0,5) | Kaçırılan ya da uydurulan tablo |
| Yapı | GriTS_Con (hücre metni, LCS), GriTS_Top (birleşik hücre topolojisi, IoU) | Kayan sütun, yutulan satır, bölünen/birleşen hücre |
| Olgu | P/R/F1, anahtar (sayfa, değer, birim, dönem, son satır başlığı); ayrıca yalnız değer | Taslak sayısını doğrulamaya yetecek doğrulukta mı |

GriTS: Smock, Pesala, Abraham (2023), ICDAR, arXiv:2203.12555. `tools/tablo_olcum.py` tanımdan bağımsız yazıldı ve Microsoft table-transformer `src/grits.py` (MIT) ile 300 rastgele ızgara çiftinde karşılaştırıldı: en büyük fark 0 (PROGRESS §4). TEDS (Zhong vd. 2020, PubTabNet; arXiv:1911.10683) ağaç düzenleme uzaklığına dayanır, HTML gerektirir ve `apted` bağımlılığı ister; şimdilik kullanılmaz.

## Ne zaman / ne zaman değil

- **Kullan:** motor ya da `pipelines/tables.py` değişince; S28 kapanışında; tezde çıkarım tablosu için.
- **Kullanma:** altın küme yokken "doğruluk" raporlamak için. Altın küme yoksa yalnızca kapsama (başlıklı sayfa / tablolu sayfa) ve uyarı sayıları raporlanır, "doğruluk" kelimesi kullanılmaz.

## Girdi / çıktı

| | Yol | Biçim |
|---|---|---|
| Altın | `data/gold/tables/<rapor_id>.tables.jsonl`, `.facts.jsonl` | `tablo-0.1` / `olgu-0.1`, `motor: insan`; **insan hazırlar** (korumalı yol) |
| Tahmin | `data/processed/<rapor_id>/tables.jsonl`, `facts.jsonl` | `pipelines/structure.py` çıktısı |
| Sonuç | `reports/experiments/tablo-olcum-<run_id>.json` ve `.md` | `run_id`, girdi SHA-256'ları, ölçütler, tablo bazında GriTS |

## Adımlar

1. **Altın küme (insan, U-16).** Rapor başına 5 tablo (4 rapor → 20): en az 2'si kenarlıksız, 1'i iki sayfaya bölünmüş, 1'i birleşik başlıklı. Her tabloyu Excel'de PDF'te göründüğü gibi yaz (`;` ayraçlı CSV, sayı biçimi değiştirilmez; birleşik hücrede soldakiyle `<`, üsttekiyle `^`), sonra:
   ```
   python .claude/skills/table-eval/scripts/altin_donustur.py tablo.csv --rapor-id <id> --sayfa <s> --sira 1 --baslik-satiri <n> --baslik "<Tablo N ...>" --out-dir data/gold/tables
   ```
   Komut her olgunun birim ve dönemini yazar; insan bunları PDF'le karşılaştırır. Taslak, bir motorun çıktısından **kopyalanmaz** (ölçülen motoru kayırır).
2. Doğrula: `python tools/validate_data.py` (altın dosyaları varsayılan listededir) ve `python tools/gold_manifest.py verify`.
3. Her motor için tahmin üret (`table-extract` Adımlar 2) ve ölç:
   ```
   python tools/tablo_olcum.py --gercek data/gold/tables/<id>.tables.jsonl --tahmin data/processed/<id>/tables.jsonl --gercek-olgu data/gold/tables/<id>.facts.jsonl --tahmin-olgu data/processed/<id>/facts.jsonl --run-id tablo-<motor>-<tarih> --out reports/experiments/tablo-olcum-<run_id>.json
   ```
4. Rapor bazında sonuçları birleştir; 4 rapor < 5 olduğundan sonuç "ön sonuç" etiketlidir (evaluator kuralı). Kol başına en az 5 hata örneği yaz (tablo_id, beklenen, bulunan).
5. Motor kararı (PyMuPDF / Docling varsayılanı) ADR olarak yazılır; ölçüm görülmeden karar verilmez.

## Tuzaklar

- **Excel sayıyı dönüştürür:** hücreler "Metin" biçimine alınmadan yazılırsa "12.450" CSV'ye "12450", "1/2" tarih olarak gider; GriTS_Con ve olgu ham metni yanlış düşer. Kullanım kılavuzu §5a adım 1.
- **Taslaktan altın:** Motor çıktısını düzelterek altın hazırlamak o motoru kayırır; elle yazılır ya da üçüncü bir araçtan (Excel "PDF'ten veri al") alınıp hücre hücre kontrol edilir; kaynak `uyarilar`'a yazılır.
- **GriTS_Con yüksek ama olgu düşük** olabilir: metin doğru, başlık rolü yanlış (dönem/birim kayar). Bu yüzden üç düzey birlikte raporlanır.
- **Olgu ölçümü türetme mantığını kendisiyle karşılaştırır:** altın olgular da `pipelines/tables.py` içindeki `olgular` ile türetilir; bu yüzden altın olguların birim ve dönemi insan tarafından kontrol edilmeden ölçüm yapılmaz (Adımlar 1).
- **Eşlenmeyen gerçek tablo:** `grits_*_tum_gercek_ort` onu 0 sayar; `*_eslenen_ort` saymaz. İkisi birlikte yazılır.
- **Sayfa numarası:** altın kümede sayfa PDF sayfasıdır (raporun basılı numarası değil; Akbank'ta bir PDF sayfası iki basılı sayfa).

## Örnek

Sentetik doğrulama (`tests/tools/test_tablo_olcum.py`): 3×3 tabloya boş bir satır eklenirse eşleşen 9 konum için GriTS = 2·9 / (9 + 12) = 0,857; "12.450" → "12 450" tek hücre farkı GriTS_Con'u (8 + LCS) / 9'a indirir, GriTS_Top 1 kalır; iki sütun kaplayan başlığı iki hücre sanan tahminde GriTS_Con = 1 iken GriTS_Top < 1.

## Kontrol listesi

- [ ] Altın küme insan tarafından hazırlandı, `gold_manifest.py verify` geçti
- [ ] Her sonuç dosyasında `run_id` ve girdi SHA-256'ları var
- [ ] Tespit, GriTS (iki çeşit, iki ortalama) ve olgu birlikte raporlandı
- [ ] Kol başına ≥ 5 hata örneği; "ön sonuç" etiketi (rapor < 5)

## Dosyalar

- `tools/tablo_olcum.py`: tespit, GriTS, olgu ölçümü (standart kütüphane)
- `scripts/altin_donustur.py`: insan CSV'si → altın tablo ve olgu kaydı
- `tools/tablo_kurallari.py`: şema ve değişmezler
