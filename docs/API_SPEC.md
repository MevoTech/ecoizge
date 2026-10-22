# API Sözleşmesi

Tek kaynak bu belgedir (bulgu B16). Sunumdaki Türkçe yollar (`/api/rapor/...`, S-18) ile Teknik Kapsam 5.3'teki İngilizce yollar burada uzlaştırıldı: **İngilizce yollar kullanılır**, Türkçe adlar arayüz etiketidir. Her yanıt `schema_version` taşır.

## Ortak kayıt şeması `[uygulandı]`

`shared/contracts/forecast_record.schema.json`:
- KPI ve tahmin kaydı;
- örnek: `shared/contracts/examples/forecast_record.example.json`;
- test: `tests/contracts/test_forecast_record.py`.

Sunum S-19'daki örnek kayıtta `schema_version` alanı yoktu. Örnek, bu alan eklenerek kullanıldı.

## Uçlar `[hedef]`

| Yöntem ve yol | Servis | Girdi | Çıktı | Sunumdaki ad | Gereksinim |
|---|---|---|---|---|---|
| `POST /auth/login` | Ortak | e-posta, parola | JWT | — | R-SEC-04 |
| `POST /reports` | report | PDF, yıl, company_id | `job_id` | `/api/rapor/analiz` (yükleme kısmı) | R-PDF-01, R-API-02 |
| `POST /gap-analysis` | report | report_id, profil | `job_id` | `/api/rapor/analiz` | R-GAP-01, R-KAT-02 |
| `GET /jobs/{id}` | report | — | durum, sonuç veya hata | `/api/rapor/analiz/{id}` | R-API-02 |
| `POST /drafts` | report | requirement_id, period_id, mode (yaz/tamamla) | `job_id` → taslak, iddialar, uyarılar | `/api/rapor/taslak` | R-GEN-01…04 |
| `POST /drafts/{id}/export` | report | biçim (docx/pdf) | dosya | — | R-EXP-01 |
| `POST /forecasts` | forecast | şirket, hedef, ufuk, model | `forecast_record[]` | `/api/emisyon/tahmin` | R-INT-01 |
| `POST /scenarios` | forecast | temel koşu, değişen girdiler | `forecast_record[]` | `/api/emisyon/senaryo` | R-INT-01 |
| `GET /sensitivity/{run}` | forecast | — | tornado, SHAP, Sobol verisi | `/api/emisyon/duyarlilik` | — |
| `POST /exports/forecast-to-report` | report | senaryo_id, hedef madde | bağlanan kayıt sayısı | `/api/rapor/aktar` | R-INT-01 |

Değişiklik prosedürü: `.claude/agents/architect.md` → Prosedür adım 5 (şema, örnek, `schema_version`). Zemzem'i etkileyen her değişiklik onun PR onayını ister.
