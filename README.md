# EcoIzge · Sürdürülebilirlik Yönetim ve Güvence Sistemi

GİBTÜ Bilgisayar Mühendisliği bitirme projesi (2026–2027). Danışman: Dr. Öğr. Üyesi Mehmet Sait Vural.

- **Raporlama modülü (Mehmet Güneş):**
  - şirket raporunu (PDF) TSRS ve VSME maddelerine göre analiz eder;
  - eksik ve kısmi maddeler için kaynaklı Türkçe taslak üretir;
  - taslaktaki her sayıyı kaynağıyla doğrular.
- **Tahminleme modülü (Zemzem Boyluğ):** emisyon tahmini, senaryo ve duyarlılık analizi.

Durum: **F1 (araştırma).** Ne çalışıyor, ne çalışmıyor: [`docs/PROGRESS.md`](docs/PROGRESS.md) · Görevler: [`tasks/README.md`](tasks/README.md)

## Hızlı başlangıç

```bash
pip install -r requirements-dev.txt
python tools/check_all.py                  # lint + testler + veri + sistem bütünlüğü
pip install -r requirements-train.txt      # Colab ve eğitim bağımlılıkları
streamlit run services/review-ui/app.py    # etiket onay arayüzü
```

## Şu an çalışan parçalar

| Parça | Yol | Test |
|---|---|---|
| Gereklilik kataloğu (TSRS 2 + VSME, 93 madde) | `data/catalog/catalog_v0.csv` | `tools/validate_data.py` |
| Türkçe sayı ve birim normalleştirme | `services/report-service/report_service/verify/numbers.py` | `services/report-service/tests/test_numbers.py` |
| Yer tutuculu sayı üretimi ve kip denetimi (ADR-004) | `services/report-service/report_service/generation/placeholders.py` | `services/report-service/tests/test_placeholders.py` |
| Tahmin kaydı sözleşmesi | `shared/contracts/forecast_record.schema.json` | `tests/contracts/` |
| Etiket onay arayüzü | `services/review-ui/` | `services/review-ui/tests/` |
| κ, altın küme manifesti, veri doğrulayıcı | `tools/` | `tests/tools/` |
| PDF çıkarımı (paragraf, tablo, başlık, üst/alt bilgi) | `pipelines/extract.py` | `tests/pipelines/` |
| Unsur kapsama ile madde kararı (ADR-008) | `services/report-service/report_service/nlp/coverage.py` | `services/report-service/tests/test_coverage.py` |
| Claude ajan sistemi: 1 ana + 11 alt ajan, 12 skill (betikli), kancalar | `.claude/` | `tests/hooks/`, `tests/skills/`, `tests/tools/test_check_consistency.py` |

## Yapı

```
.claude/        ajanlar, skill'ler, kurallar, kancalar, ayarlar
docs/           gereksinim, mimari, API, güvenlik, test planı, kararlar, ilerleme
tasks/          S01–S24 görev dosyaları
services/       report-service (Mehmet), review-ui; forecast-service (Zemzem, F3)
shared/         ortak JSON sözleşmeleri
tools/          doğrulayıcılar ve kalite kapısı
data/           katalog, etiketler (öneri → onaylı → altın)
```

Claude Code ile çalışma: [`CLAUDE.md`](CLAUDE.md).
