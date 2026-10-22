# İzlenebilirlik

Gereksinim → görev → test → durum. Kimlikler `docs/REQUIREMENTS.md`'den; denetim `tools/check_consistency.py`. Durum metni test sonuçlarına göre orkestratör tarafından güncellenir (`.claude/agents/engineering-orchestrator.md` → Sorumluluk 9).

| Gereksinim | Görev(ler) | Test | Durum |
|---|---|---|---|
| R-KAT-01 | S02 | `tests/tools/test_validate_data.py`, `tests/skills/test_skill_scripts.py` (katalog farkı, v1 üst madde) | kısmi: doğrulayıcı ve fark aracı uygulandı, katalog v1 bekliyor |
| R-KAT-02 | S06 | — | hedef |
| R-PDF-01 | S03, S04 | `tests/pipelines/test_extract.py` | kısmi: çıkarım uygulandı (sentetik PDF), gerçek rapor bekliyor; CI'da PyMuPDF onayına kadar atlanır |
| R-PDF-02 | S04 | `tests/skills/test_skill_scripts.py` (qa_report) | kısmi: otomatik QA uygulandı, elle kontrol bekliyor |
| R-ETK-01 | S05 | `tests/tools/test_validate_data.py`, `tests/tools/test_kappa.py`, `tests/skills/test_skill_scripts.py` (örneklem, öneri dönüştürücü) | kısmi: araçlar uygulandı, etiket yok |
| R-ETK-02 | S12 | `tests/tools/test_gold_manifest.py` | kısmi: araç uygulandı, küme yok |
| R-GAP-01 | S14 | — | hedef |
| R-GAP-02 | S14, S16, S22 | `tests/skills/test_skill_scripts.py` (baseline) | kısmi: taban çizgisi sentetik veride testli; CI'da scikit-learn onayına kadar atlanır |
| R-GAP-03 | S02, S14 | `services/report-service/tests/test_coverage.py` | uygulandı (unsur kapsama); katalog v1 alt maddeleri bekliyor |
| R-GAP-04 | S08, S16 | — | hedef |
| R-RET-01 | S13 | `tests/skills/test_skill_scripts.py` (retrieval_metrics) | kısmi: metrik aracı uygulandı, adaylar ölçülmedi |
| R-RET-02 | S18 | — | hedef |
| R-GEN-01 | S17 | — | hedef |
| R-GEN-02 | S08, S17 | `tests/skills/test_skill_scripts.py` (build_prompt kip kuralları) | kısmi: istem kurucu uygulandı, LLM yok |
| R-GEN-03 | S17 | `services/report-service/tests/test_placeholders.py` | kısmi: yer tutucu modülü uygulandı, LLM entegrasyonu yok |
| R-GEN-04 | S17 | `services/report-service/tests/test_placeholders.py` | kısmi: eksik kayıt hatası uygulandı |
| R-VER-01 | S15 | `services/report-service/tests/test_numbers.py` | uygulandı (normalleştirme ve eşleme); NER yok |
| R-VER-02 | S18 | — | hedef |
| R-VER-03 | S15, S18, S20 | `services/report-service/tests/test_placeholders.py`, `tests/contracts/test_forecast_record.py` | kısmi: şema, tür ve kip uygulandı; DB kısıtı hedef |
| R-EVL-01 | S14, S22 | `tests/skills/test_skill_scripts.py` (gruplu bootstrap) | kısmi: güven aralığı aracı uygulandı |
| R-EVL-02 | S08, S19 | — | hedef |
| R-EVL-03 | S23 | — | hedef |
| R-EVL-04 | S22 | `tests/skills/test_skill_scripts.py` (gruplu bootstrap) | hedef: deney tanımları `experiment-run/references/experiments.md` |
| R-API-01 | S06, S11 | `tests/contracts/test_forecast_record.py` | kısmi: ortak kayıt şeması uygulandı, uçlar hedef |
| R-API-02 | S10 | — | hedef |
| R-SEC-01 | S17 | `tests/skills/test_skill_scripts.py` (enjeksiyon temizleme) | kısmi: istem temizleme uygulandı; PDF enjeksiyon testi S17 |
| R-SEC-02 | S01 | `tests/hooks/test_guard.py` | uygulandı (ajan tarafı); gitleaks CI'da |
| R-SEC-03 | S08, S17 | — | hedef |
| R-SEC-04 | S09, S10 | — | hedef |
| R-REP-01 | S13, S16, S24 | `tests/skills/test_skill_scripts.py` (run_record, Colab şablonu) | kısmi: kayıt aracı ve şablon uygulandı, gerçek koşu yok |
| R-HIL-01 | S07 | `services/review-ui/tests/test_review_logic.py`, `tests/skills/test_skill_scripts.py` (review_status) | kısmi: etiket kuyruğu ve durum aracı uygulandı |
| R-INT-01 | S06, S11, S20 | `tests/contracts/test_forecast_record.py` | kısmi: şema uygulandı |
| R-EXP-01 | S21 | — | hedef |
| R-AGT-01 | S01 | `tests/tools/test_check_consistency.py`, `tests/hooks/test_guard.py` | kısmi: mekanik denetim uygulandı, canlı yönlendirme bekliyor (S01) |
