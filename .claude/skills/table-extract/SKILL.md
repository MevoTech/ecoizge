---
name: table-extract
description: "Rapor PDF'indeki tabloları hücre ızgarası olarak çıkarmak (satır/sütun, birleşik hücre, başlık rolü, sayfa, koordinat), sayfalar arası bölünen tabloları birleştirmek ve sayısal hücrelerden olgu (değer, birim, satır/sütun yolu, dönem) üretmek için kullan. Tetikleyiciler: yeni rapor çıkarıldığında, taslakta tablo kaynaklı sayı doğrulanacakken, 'tablo okunmuyor / kenarlıksız tablo / bölünen tablo / birim yanlış' şüphesinde, Docling ile PyMuPDF karşılaştırılırken."
---

# table-extract

Bir sürdürülebilirlik raporunun en yoğun bilgisi tablolardadır: emisyon, enerji, hedef, finansal etki. `pdf-extract` tabloyu tek bir metin birimi olarak verir ("a | b" satırları); bu metin etiketleme için yeterli, **sayı doğrulama için yetersizdir**: "12.450" sayısının hangi kapsam, hangi yıl ve hangi birim olduğu satır ve sütun başlıklarından gelir. Bu skill tabloyu ızgara olarak verir ve her sayısal hücreden bir **olgu** üretir (R-TAB-01…03, ADR-014).

Üç düzey (ve bu projedeki karşılığı):

| Düzey | Soru | Çıktı |
|---|---|---|
| Görmek | Sayfada tablo var mı, nerede? | `tables.jsonl` → `parcalar` (sayfa, kutu) |
| Veriyi çıkarmak | Hangi hücre hangi satır/sütunda, hangisi başlık, hangisi birleşik? | `tables.jsonl` → `hucreler` |
| Anlamak | "12.450" = Kapsam 1, 2024, tCO2e mi? | `facts.jsonl` (olgular) |

## Ne zaman / ne zaman değil

- **Kullan:** `pdf-extract`'tan sonra her kamu raporunda; taslak sayılarını tablodan doğrularken (S15, S18); çıkarım kodu değiştiğinde.
- **Kullanma:** pilot firma verisinde harici bir servisle (ADR-011). Docling yereldir, kullanılabilir; Azure Document Intelligence gibi bulut servisleri insan onayı ister (security.md, onay 7).

## Girdi / çıktı

| | Yol | Biçim |
|---|---|---|
| Girdi | `data/raw/public/<...>.pdf`, isteğe bağlı `data/processed/<rapor_id>/paragraphs.jsonl` | PDF; paragraf birimleri |
| Çıktı | `data/processed/<rapor_id>/tables.jsonl` | `tablo-0.1`: `tablo_id`, `sayfalar`, `parcalar`, `baslik`, `dipnotlar`, `birim`, `satir_sayisi`, `sutun_sayisi`, `hucreler[]`, `motor`, `paragraf_id`, `uyarilar` |
| Çıktı | `data/processed/<rapor_id>/facts.jsonl` | `olgu-0.1`: `deger`, `birim`, `carpan`, `birim_kaynagi`, `ham`, `eksik`, `dipnot`, `yil`, `satir_yolu`, `sutun_yolu`, `donem`, kaynak hücre (`tablo_id`, `satir`, `sutun`, `sayfa`, `bbox`) |

Şemanın tek uygulaması `tools/tablo_kurallari.py`'dir. Hücre alanları docling-core `TableCell` ile aynı anlamdadır; motor değişse de kayıt biçimi değişmez. Değişmez: her (satır, sütun) konumu **tam olarak bir** hücre tarafından kaplanır (`tablo_hatalari`).

## Adımlar

1. Önce `pdf-extract` ile `paragraphs.jsonl` üret (tablo birimleri etiketlemede kullanılır, değiştirilmez).
2. Yapısal çıkarım:
   ```
   python pipelines/structure.py data/raw/public/sirket/<pdf> --rapor-id <id> --out-dir data/processed/<id> --paragraflar data/processed/<id>/paragraphs.jsonl
   ```
   Varsayılan motor `pymupdf` (hafif, CI'da koşar). Docling kuruluysa (`pip install -r requirements-extract.txt`): `--motor docling` (TableFormer; kenarlıksız ve karmaşık tablolarda daha iyi, sayfa başına ~1–5 sn CPU).
3. Doğrula: `python tools/validate_data.py data/processed/<id>/tables.jsonl data/processed/<id>/facts.jsonl` → hata yok. Olgu doğrulayıcısı her olgunun değerini kaynak hücreden yeniden üretir.
4. Otomatik QA ve elle kontrol örneklemi:
   ```
   python .claude/skills/table-extract/scripts/tablo_ozeti.py data/processed/<id> --pdf data/raw/public/sirket/<pdf> --ornek 10 --seed 43
   ```
   Bak: "tablosu bulunmayan" sayfalar (kaçırılan tablo), `uyarilar` sayımı, birimli ve dönemli olgu oranı.
5. Örneklemdeki 10 tabloyu PDF ile yan yana kontrol ettir (insan). Sistematik hata çıkarsa önce `tests/pipelines/test_tables.py`'ye kırmızı test, sonra `pipelines/tables.py`'de düzeltme.
6. Ölçüm altın kümeyle `table-eval` skill'indedir (`evaluator`); bu skill kendi işini notlamaz.

## Tuzaklar (bu projede gerçekten yaşananlar, 2026-10-23)

- **Kenarlıksız tablo.** `find_tables` Klimasan 2025'te "Tablo N" başlıklı 34 sayfanın 13'ünde tablo bulamadı (s. 37 "Tablo 4"). Sezgisel `pymupdf-bosluk` motoru başlık çapasının altındaki bölgede sütunları başlık bandının yatay izdüşümünden, satırları dikey boşluklardan bulur; kalan 2 sayfa. Sezgi sıkı aralıklı satırları **tek satıra** birleştirebilir; uyarı `kenarliksiz_sezgisel`.
- **Başlık satırı veriyi yuttu.** Klimasan 2025 s. 51'de PyMuPDF iki satırlık başlığı ve ilk veri satırını ("Kapsam 1 1.514,11 1.075,62") tek hücre yaptı: Kapsam 1 verisi kayboldu. Uyarı `baslikta_sayisal_veri`; bu hücreden birim alınmaz, birden çok yıl içerdiği için dönem boş kalır. Docling bu tabloyu doğru ayırdı.
- **Çerçeve kutusu hücreleri yutuyordu.** `find_tables` bütün tabloyu saran kutuyu da hücre olarak verebiliyor; önce o yerleşince gerçek hücreler atılıyordu (4 raporda 180 hücre, Klimasan s. 44 finansal etki değerleri dahil). Çerçeve kutusu (≥ 2 kutuyu içine alan) ızgaraya girmez; uyarı `cizgi_hucre_atildi` sıfır olmalı.
- **Windows'ta "-" yumuşak tire (U+00AD) gelir** (Arial); hücre metni `hucre_metni_temizle` ile düzeltilir. CI windows-latest bunu yakaladı.
- **Dönem önekli hücre:** "2025: -42,78 milyon TL" → değer −42.780.000 TL, dönem 2025. Aralık ("-271,8 milyon TL ile -407,7 milyon TL") olgu değildir.
- **İçindekiler tablosu.** Akbank, Derimod ve QUA Granite s. 2–3'teki içindekiler tablo olarak bulunur; sayfa numaraları olgu sanılırdı. Uyarı `icindekiler_olasi`; olgu üretilmez.
- **Yıl hücresi nicelik değildir.** QUA Granite s. 42 "Hedef Yılı = 2035" satırdaki tCO2e birimini alıyordu; yıl hücresine birim verilmez (`yil: true`).
- **`ton CO₂` birimi çöküyordu.** "e" eki olmayan CO₂ birimi `normalize_unit`'te ValueError veriyordu (Klimasan); düzeltildi, regresyon testi `test_r_ver_01_co2_e_eksiz_birim_cokmez`.
- **Bölünen tablo** (KL-02, Derimod s. 22→23, 25→26; Klimasan Tablo 1–4 zincirleri, ör. s. 37→41): ardışık sayfalar, alt/üst konum, aynı sütun sayısı ve sol kenarlar, devamın başlığı yok ya da aynı → birleşir; tekrarlanan başlık satırı atılır. Farklı başlıklı yeni tablo birleşmez.
- **Birim önceliği:** hücre > sütun başlığı (en derin) > satır başlığı > tablo başlığı. "(Bin TL)" çarpan verir (`carpan: 1000`). İki farklı birim anan başlıktan birim alınmaz.
- **Muhasebe gösterimi:** "(1.234)" eksi; "+19.202.635" artı işaretli; "-", "—", "n/a" **eksik** (sıfır değil).
- **Kimlik kayması yok:** `paragraphs.jsonl` değişmez; pilot örneklemi ve kör etiketler ona bağlıdır.

## Örnek

Girdi: "Tablo 1. Sera gazı emisyonları"; başlıkta "Kapsam" iki satır, "Emisyon (tCO2e)" iki sütun kaplar; altında 2024, 2025; satırlar "Kapsam 1 | 12.450 | 13.100*", "Kapsam 2 | 31.200 | -" (`tests/pipelines/test_tables.py`).

Çıktı (özet):
```
tables.jsonl: 4×3 ızgara; "Kapsam" (satir_kapsam 2), "Emisyon (tCO2e)" (sutun_kapsam 2); dipnot "* Bağımsız güvence kapsamında değildir."
facts.jsonl : Kapsam 1 · Emisyon (tCO2e) > 2024 → 12450 tCO2e, dönem 2024, birim_kaynagi sutun_basligi
              Kapsam 1 · … > 2025 → 13100 tCO2e, dipnot ["*"]
              Kapsam 2 · … > 2025 → eksik (deger null)
```

## Kontrol listesi

- [ ] `python -m pytest -q tests/pipelines services/report-service/tests` geçti
- [ ] `validate_data.py` tables/facts için hata vermedi
- [ ] `tablo_ozeti.py` çıktısında "tablosu bulunmayan" sayfalar incelendi; kalanlar KL-13'te ya da düzeltildi
- [ ] 10 tabloluk elle kontrol yapıldı (insan); sonuç PROGRESS §4'te
- [ ] Docling kullanıldıysa sürümü (`pip show docling`) ve motor çıktı özeti kayıtta

## Dosyalar

- `pipelines/tables.py`: ızgara, başlık rolü, kenarlıksız sezgi, birleştirme, olgular, Docling uyarlayıcısı (sahibi `ml-engineer`)
- `pipelines/structure.py`: komut satırı; tablo + olgu + şekil dosyaları
- `tools/tablo_kurallari.py`: şema ve değişmezler (tek kaynak)
- `scripts/tablo_ozeti.py`: otomatik QA özeti ve elle kontrol örneklemi
- Dış kaynak: Docling (MIT, <https://github.com/docling-project/docling>); kurulunca resmî ajan skill'i `uvx library-skills --claude` ile bağlanabilir (`docs/research/tablo-grafik-cikarimi.md`).
