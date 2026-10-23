# Araştırma notu: tablo ve grafik çıkarımı, ölçütler ve ajan skill depoları

- **Tarih:** 2026-10-23 · **Hazırlayan:** orkestratör (kullanıcı isteği: "tablolar ve içindeki veriler ayrışıyor mu … skillerin GitHub reposunu bul")
- **Kapsam:** Sürdürülebilirlik raporu PDF'lerinde tablo yapısı, sayısal olgu ve grafik verisi; doğruluk ölçütleri; hazır ajan skill'leri.
- **Karar:** ADR-014. Bu not karar vermez; karar için kanıt sunar.

## 1. Sorun (koşulmuş ölçümle)

2026-10-23 öncesindeki `pipelines/extract.py` tabloyu "a | b" satırlarından oluşan tek bir metin birimi olarak veriyordu. 4 pilot raporda "Tablo N" başlığı geçen sayfalarla tablo bulunan sayfalar karşılaştırıldı (PROGRESS §4 S28):

| Rapor | "Tablo N" başlıklı sayfa | Tablosu bulunmayan (önce) | Tablosu bulunmayan (S28, PyMuPDF + sezgi) |
|---|---|---|---|
| Klimasan 2025 | 34 | 13 | 2 (s. 26, 62) |
| Akbank 2025 | 20 | 3 | 2 (s. 5, 35) |
| Derimod 2025 | 3 | 0 | 0 |
| QUA Granite 2025 | 7 | 0 | 0 |

"Tablo bulundu" doğru yapı anlamına gelmez: Klimasan s. 51'de PyMuPDF iki satırlık başlığı ve ilk veri satırını tek hücre yaptı (Kapsam 1 verisi kayboldu); Docling aynı tabloyu 7×4 olarak doğru ayırdı ve 11 olgunun hepsine birim ve dönem verdi. Doğruluk ancak altın kümeyle ölçülebilir (S28.T6–T7).

## 2. Araçlar (birincil kaynak, erişim 2026-10-23)

| Araç | Lisans | Tablo | Grafik | Not |
|---|---|---|---|---|
| PyMuPDF `find_tables` | AGPL-3.0 | Çizgili ve düzenli hizalı tablolar; hücre kutuları | — | Zaten bağımlılık (requirements-train). `table.extract()` Türkçe binlik ayracını bozar; hücre metni kutudan okunur |
| [Docling](https://github.com/docling-project/docling) 2.142.1, docling-core 2.104.0 | MIT (kod); modeller CDLA-Permissive-2.0 / Apache-2.0 ([docling-models](https://huggingface.co/docling-project/docling-models), [layout-heron](https://huggingface.co/docling-project/docling-layout-heron), [DocumentFigureClassifier](https://huggingface.co/docling-project/DocumentFigureClassifier-v2.0)) | TableFormer (`TableFormerMode.ACCURATE`); hücre: `start/end_row/col_offset_idx`, `row/col_span`, `column_header`, `row_header`, `row_section`, `bbox` (docling-core `TableCell`) | Resim sınıflandırma (bar_chart, pie_chart, line_chart, flow_chart …); `do_chart_extraction` granite-vision ile bar/pie/line → tablo (yaklaşık, VLM); PowerPoint/Excel grafikleri `meta.tabular_chart` | Yerel. CPU 2 çekirdekte 4 raporun tamamı: Klimasan 65 sf 228 sn, Akbank 45 sf 174 sn. Kutu alt-sol orijinli olabilir (`to_top_left_origin`) |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) PP-StructureV3 | Apache-2.0 | Tablo hücre koordinatları, Markdown/JSON | PP-Chart2Table (grafik → tablo) | Paddle çerçevesi ek bağımlılık; denenmedi |
| [Microsoft table-transformer](https://github.com/microsoft/table-transformer) | MIT | DETR tabanlı tablo tespiti ve yapısı; PubTables-1M | — | GriTS ölçütünün başvuru uygulaması (`src/grits.py`) |
| Azure Document Intelligence | Ticari bulut | Var | — | Yeni harici servis ve hesap; pilot verisi gönderilemez (ADR-011). Değerlendirilmedi |

## 3. Ölçütler

- **GriTS** — Smock, Pesala, Abraham, "GriTS: Grid table similarity metric for table structure recognition", ICDAR 2023, [arXiv:2203.12555](https://arxiv.org/abs/2203.12555). Tabloyu ızgara olarak karşılaştırır; 2D en benzer alt yapı problemi NP-zor olduğundan satır ve sütun hizalaması ayrı ayrı (factored) yapılır. Üç çeşit: içerik (Con), topoloji (Top), konum (Loc). `tools/tablo_olcum.py` tanımdan bağımsız yazıldı; başvuru uygulamasıyla 300 rastgele ızgara çiftinde en büyük fark 0 (PROGRESS §4).
- **TEDS** — Zhong, ShafieiBavani, Jimeno Yepes, "Image-based table recognition: data, model, and evaluation", ECCV 2020, [arXiv:1911.10683](https://arxiv.org/abs/1911.10683); PubTabNet açıklamaları CDLA-Permissive-1.0. HTML ağacı üzerinde ağaç düzenleme uzaklığı; `apted` bağımlılığı ister. Kullanılmadı: GriTS ızgara modelimizle doğrudan uyumlu ve birleşik hücre topolojisini ayrı ölçüyor.
- **Olgu P/R/F1** (projeye özgü): taslak sayısının doğrulanması için gereken düzey. Yapı doğru ama başlık rolü yanlışsa dönem ya da birim kayar; GriTS bunu göstermez.

## 4. Ajan skill depoları (GitHub)

| Depo | İçerik | Lisans | Kullanım |
|---|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) (commit dbd4588) | `pdf`, `docx`, `pptx`, `xlsx` skill'leri | **Proprietary** ("Use … is governed by your agreement with Anthropic") | Depoya kopyalanmadı; yalnızca başvuru |
| aynı depo, `skill-creator` | Skill yazım rehberi ve değerlendirme döngüsü | Apache-2.0 | Biçim için başvuru (önbilgi, tetikleyici açıklama, kısa gövde) |
| [docling-project/docling](https://github.com/docling-project/docling) `docling/.agents/skills/docling/` | Resmî Docling kullanım skill'i (CLI, Python SDK, RAG parçalama, docling-serve) | MIT | Docling kurulunca `uvx library-skills --claude` ile `.claude/skills/docling` bağlantısı kurulabilir (sembolik bağ; Windows'ta yönetici izni gerekebilir). Depoya kopyalanmadı: sürümle birlikte güncellenmeli |
| [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) `skills/paddleocr-doc-parsing` | Belge ayrıştırma skill'i | Apache-2.0 | `PADDLEOCR_ACCESS_TOKEN` ile bulut API'si kullanır → yeni harici servis, insan onayı gerekir; kullanılmadı |

Projede yazılan skill'ler: `table-extract`, `figure-extract` (`ml-engineer`), `table-eval` (`evaluator`). Biçim proje kuralına uyar (Adımlar, Tuzaklar, Örnek, Kontrol listesi; her betiğin testi `tests/skills`).

## 5. Açık sorular

- Varsayılan motor (D-09): altın kümede ölçülmeden karar verilmez.
- Görüntü grafikler (KL-14): Docling `do_chart_extraction` (granite-vision 4B) CPU'da yavaş ve yaklaşık; denenecekse çıktı `yaklasik` işaretli ve ayrı ölçülerek.
- Docling'in kenarlıksız tabloları sayfa başına ayrı tablo olarak vermesi: başlık aynı olduğunda `sayfalari_birlestir` birleştiriyor (Klimasan Tablo 1–4).
