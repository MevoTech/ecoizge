# Mimari

Durum etiketleri: `[uygulandı]` (kod + test var) · `[kısmi]` · `[hedef]` (tasarım). Gerçek test sonuçları: `docs/PROGRESS.md`.

## 1. Bileşenler

| Bileşen | Teknoloji | Sahip | Durum |
|---|---|---|---|
| Web arayüzü | React + TypeScript | Mehmet (`frontend-engineer`) | `[hedef]` F3+ |
| `report-service` | Python, FastAPI | Mehmet | `[kısmi]`: `verify/numbers.py`, `verify/tense.py`, `generation/placeholders.py`, `nlp/coverage.py` uygulandı; API ve DB katmanları hedef |
| `forecast-service` | Python, FastAPI | Zemzem | `[hedef]` |
| Onay arayüzü | Streamlit (yerel) | Mehmet (`backend-engineer`) | `[kısmi]`: etiket kuyruğu |
| Veri katmanı | PostgreSQL + pgvector | Ortak | `[hedef]` F3 |
| Ortak sözleşme | JSON Schema 2020-12 | Ortak | `[kısmi]`: `shared/contracts/forecast_record.schema.json` |
| Çevrimdışı hatlar | Python betikleri, Colab | Her biri kendi modülünde | `[kısmi]`: `pipelines/extract.py` (PDF çıkarımı), skill betikleri (örneklem, taban çizgisi, metrikler, run.json); gerçek veri bekliyor |
| Ajan sistemi | Claude Code ajanları, skill'ler, kancalar | Mehmet | `[uygulandı]` (canlı yönlendirme testi bekliyor, S01) |

Servisler birbirini doğrudan çağırmaz; ortak veritabanı ve JSON sözleşmesi üzerinden konuşur (Teknik Kapsam 5).

## 2. Raporlama hattı

```
PDF ──▶ [1] çıkarım ──▶ report_chunk ──▶ [2] eşleme (embedding + sınıflandırıcı) ──▶ gap_result
           (pdf-extract)                    C(r) = unsur kapsama (ADR-008), s_spec Türkçe (ADR-007)
                                                     │ eksik → yaz · kısmi → tamamla
                                                     ▼
 KPI kayıtları + tahmin kayıtları ──▶ [3] retrieval (company_id zorunlu) ──▶ [4] LLM: metin + {{KPI:..}} yer tutucu
                                                                                  │
                         [5] doğrulama: serbest sayı yok · kayıt var · tür eşleşir · kip doğru
                                       (placeholders.validate_draft)   [uygulandı]
                                                     │ hata → yeniden üret
                                                     ▼
                         [6] doldurma (placeholders.render) [uygulandı] ──▶ draft_section + draft_claim
                                                     ▼
                                     onay arayüzü (insan) ──▶ DOCX/PDF dışa aktarım [hedef]
```

| Adım | Durum | Gereksinim |
|---|---|---|
| 1 Çıkarım | `[kısmi]` S04: `pipelines/extract.py` + otomatik QA, sentetik PDF testli | R-PDF-01, R-PDF-02 |
| 2 Eşleme | `[kısmi]` S14: TF-IDF+LR taban çizgisi (skill betiği) ve unsur kapsama (`nlp/coverage.py`) · `[hedef]` S13, S16 | R-GAP-01…04, R-RET-01 |
| 3 Retrieval | `[hedef]` S18 | R-RET-02 |
| 4 Üretim | `[kısmi]` istem kurucu (`rag-draft/scripts/build_prompt.py`, enjeksiyon temizleme) · `[hedef]` LLM çağrısı S17 | R-GEN-01, R-GEN-02, R-SEC-01 |
| 5 Doğrulama | `[uygulandı]` yer tutucu, serbest sayı, kip · `[hedef]` kaynaksız cümle (R-VER-02) | R-GEN-03, R-VER-01, R-VER-03 |
| 6 Doldurma | `[uygulandı]` | R-GEN-03, R-GEN-04 |

## 3. Gerçekleşmiş ≠ tahmin (Sunum S-19)

1. **Şema:** `veri_turu` zorunlu; tahminde `model_id`, `senaryo_id`, `guven_araligi` zorunlu. `[uygulandı]`, sözleşme testiyle.
2. **Veritabanı:** ayrı tablolar + CHECK kısıtı. `[hedef]` (`docs/DATA_MODEL.md`).
3. **Üretim:** yer tutucu türü kayıt türüyle aynı olmalı. `[uygulandı]`
4. **Doğrulama:** tahmin cümlesi öngörü kipinde. `[uygulandı]` (`verify/tense.py`, kural tabanlı; sınırları modül belgesinde).
5. **Arayüz:** düz ve kesikli çizgi, "(tahmin)" etiketi. Metinde `[uygulandı]`, grafikte `[hedef]`.

## 4. Ajan sistemi

Ayrıntı:
- `docs/ORCHESTRATION.md`;
- `docs/COMPETENCY_MATRIX.md`;
- `.claude/agents/`, `.claude/skills/`, `.claude/rules/`.

Zorlama mekanizmaları:
- `.claude/hooks/guard.py`;
- `.claude/hooks/write_scopes.json`;
- `.claude/settings.json`.

Bütünlük denetimi: `tools/check_consistency.py`.
