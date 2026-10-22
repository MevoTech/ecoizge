# Veri Modeli

**Durum: tamamı `[hedef]`.** Veritabanı F3'te (S09) kurulacak. Bu belge Teknik Kapsam 5.2 ile Sunum S-18/S-19 arasındaki ad farklarını uzlaştırır (bulgu B15). Tablo adları İngilizce `snake_case`; Türkçe adlar yalnızca arayüz etiketidir.

## Ad uzlaştırması

| Sunum (S-18/S-19) | Teknik Kapsam 5.2 | Karar |
|---|---|---|
| `olcum_gerceklesmis` | `emission_record`, `energy_use` … | Konu tabloları korunur (TK kararı); hepsinde `data_type = 'realized'` CHECK |
| `tahmin_ciktisi` | `forecast_run` | `forecast_record` (satır) + `forecast_run` (koşu); `data_type = 'forecast'` |
| Model kayıt defteri | yok | `model_registry` eklendi |
| Asenkron iş (S-21) | yok | `job` eklendi |

## Tablolar

Her ölçüm tablosu ortak alanları taşır: `company_id, period_id, unit, value, source_type, evidence_id, entered_by, entered_at, status`.

| Grup | Tablo | Ana alanlar | Gereksinim |
|---|---|---|---|
| Şirket | `company`, `user_account`, `reporting_period`, `facility` | TK 5.2 | R-SEC-04 |
| Ölçüm | `energy_use`, `emission_record`, `water_use`, `waste_record`, `workforce_record`, `ohs_incident`, `target` | TK 5.2 + `data_type CHECK = 'realized'` | R-VER-03 |
| Tahmin | `forecast_run`, `forecast_record`, `scenario`, `sensitivity_result` | `forecast_record`: kpi, year, value, unit, model_id, scenario_id, ci_low, ci_high, `data_type CHECK = 'forecast'`; yalnızca forecast-service yazar | R-INT-01, R-VER-03 |
| Katalog | `catalog_version`, `standard_requirement` | `catalog_v*.csv` sütunları + parent_id (alt unsur, ADR-008) | R-KAT-01 |
| Rapor | `report_document`, `report_chunk` | chunk: text, page, heading, kind (paragraph/table), source (text/ocr), `embedding vector(d)` | R-PDF-01 |
| Etiket | `annotation` | `etiket_sablonu.csv` sütunları + review_id | R-ETK-01 |
| Çıktı | `gap_result` | chunk_id, requirement_id, level, score, model_version | R-GAP-01 |
| Çıktı | `draft_section`, `draft_claim` | section: requirement_id, mode (yaz/tamamla), text, status, prompt_version_id · claim: placeholder, kpi, year, value, data_type, source, check_result, support (supported/unsupported/contradicted) | R-GEN-*, R-EVL-03 |
| İşletim | `job` | kind, status (queued/running/done/failed), payload, result, error | R-API-02 |
| İşletim | `model_registry`, `prompt_version`, `experiment_run` | run_id, git_sha, metrics, status (proposed/accepted/rejected), approved_by | R-REP-01, R-HIL-01 |
| İzlenebilirlik | `evidence_file`, `audit_log` | TK 5.2 | R-SEC-04 |

`embedding` boyutu `d`, seçilen modele bağlıdır ve ADR ile sabitlenir (S13).
