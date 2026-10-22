# Test Planı

Tek komut: `python tools/check_all.py`. Yerelde ve CI'da (`.github/workflows/ci.yml`) aynı adımlar koşar. Son sonuçlar: `docs/PROGRESS.md`.

## Seviyeler

| Seviye | Ne | Nerede | Durum |
|---|---|---|---|
| Birim | Sayı ve birim normalleştirme, kip, yer tutucu | `services/report-service/tests/` | `[uygulandı]` |
| Birim | Doğrulayıcı, κ, manifest | `tests/tools/` | `[uygulandı]` |
| Kanca | guard: izinli ve engelli yazma, okuma, Bash; bozuk girdi | `tests/hooks/test_guard.py` | `[uygulandı]` |
| Sözleşme | `forecast_record` şeması | `tests/contracts/` | `[uygulandı]` |
| Çıkarım | Sentetik Türkçe PDF: üst/alt bilgi, başlık, tireleme, tablo, OCR gereken sayfa | `tests/pipelines/` | `[uygulandı]` (PyMuPDF gerekir; CI'da onaya kadar atlanır) |
| Skill betikleri | Her `scripts/*.py` en az bir test; denetleyici zorunlu tutar | `tests/skills/` | `[uygulandı]` (taban çizgisi testi scikit-learn gerektirir) |
| Arayüz | Onay mantığı + Streamlit AppTest | `services/review-ui/tests/` | `[uygulandı]` |
| Sistem bütünlüğü | Ajan, skill, kural, belge ve görev tutarlılığı; bozulan kopyanın yakalanması | `tests/tools/test_check_consistency.py` + `tools/check_consistency.py` | `[uygulandı]` |
| Lint ve biçim | ruff | `pyproject.toml` | `[uygulandı]` |
| Entegrasyon | Compose üzerinde yükle → analiz → taslak | `tests/integration/` (`-m integration`) | `[hedef]` S21 |
| Model | P/R/F1, Recall@k, ROUGE-L, BERTScore, NC | `reports/experiments/` (`evaluator`) | `[hedef]` S13–S23 |
| Canlı ajan | Yönlendirme senaryoları (S01) | Kullanıcının Claude Code oturumu | `[hedef]` |

## Testin gerçekten hata yakaladığının kanıtı

Kod, testlerden önce yazıldığı için testlerin kırmızıya dönebildiği **mutasyon denemesiyle** gösterildi. Yöntem: kodda kasıtlı bir hata yapılır, test koşulur, kod geri alınır. Sonuçlar `docs/PROGRESS.md`'dedir. Yeni kodda sıra: önce kırmızı test, sonra kod (`.claude/rules/quality-gates.md`).
