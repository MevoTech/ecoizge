# Yetkinlik Matrisi

Bilgisayar mühendisliğinin 18 yetkinliğinin (kullanıcının 2026-10-22 tarihli listesi) her biri bir **sorumlu ajana** ve en az bir **skill'e** bağlıdır. Ajan, uzmanlığı yürüten bağımsız roldür; skill, o uzmanlığın tekrar kullanılabilir iş akışıdır. Bu tablo `tools/check_consistency.py` tarafından denetlenir:
- her ajan `.claude/agents/` içinde var olmalı;
- her skill `.claude/skills/<ad>/SKILL.md` olarak var olmalı;
- skill, sorumlu ajanın "Kullandığı skill'ler" listesinde bulunmalı.

Durum:
- **etkin**: şu fazda kullanılıyor.
- **hazır**: tanımlı, ilgili fazda kullanılacak.
- **etkin değil**: proje kapsamı dışında; kapsam değişirse kullanılır.

| # | Yetkinlik | Sorumlu ajan | Skill'ler | Durum | Projedeki karşılığı |
|---|---|---|---|---|---|
| 1 | Yazılım mimarisi | `architect` | `adr`, `api-contract` | etkin | İki servis + ortak DB, sözleşme (Teknik Kapsam 5) |
| 2 | Algoritmalar | `code-reviewer` | `algorithms-ds` | etkin | Eşleme, top-k, unsur kapsama toplama (ADR-008) |
| 3 | Veri yapıları | `code-reviewer` | `algorithms-ds` | etkin | İndeksler, paragraf × madde matrisi |
| 4 | İşletim sistemleri | `backend-engineer` | `systems-diagnostics` | hazır | Süreç, bellek, dosya sistemi, konteyner kaynakları |
| 5 | Bilgisayar ağları | `backend-engineer` | `systems-diagnostics` | hazır | Compose ağı, port, TLS, servisler arası HTTP |
| 6 | Veritabanları | `architect` | `db-migration` | hazır | PostgreSQL + pgvector şeması (F3) |
| 7 | Backend | `backend-engineer` | `api-contract`, `db-migration`, `release-check` | hazır | FastAPI `report-service` (F3) |
| 8 | Frontend | `frontend-engineer` | `frontend-dev` | etkin değil | React panel (F3'ten sonra; kullanıcı şimdilik istemiyor) |
| 9 | Mobil | `frontend-engineer` | `mobile-dev` | etkin değil | Kapsam dışı (Teknik Kapsam 6) |
| 10 | Yapay zekâ | `ml-engineer` | `rag-draft`, `colab-train` | etkin | LLM ile kaynaklı taslak |
| 11 | Makine öğrenmesi | `ml-engineer` | `gap-baseline`, `colab-train`, `forecast-modeling` | etkin | TF-IDF+LR, BERT fine-tune; Zemzem'in tahmin modelleri |
| 12 | NLP / RAG | `ml-engineer` | `pdf-extract`, `embed-eval`, `rag-draft`, `numeric-verify` | etkin | Boşluk analizi, retrieval, üretim, doğrulama |
| 13 | Bilgisayarlı görü | `ml-engineer` | `computer-vision` | etkin değil | Yalnızca taranmış PDF / görsel tablo çıkarsa (OCR) |
| 14 | Gömülü sistemler | `architect` | `embedded-realtime` | etkin değil | Kapsam dışı; sayaç veya IoT veri girişi eklenirse |
| 15 | Siber güvenlik | `security-auditor` | `security-audit` | etkin | Injection, kiracı izolasyonu, gizli veri (SECURITY.md) |
| 16 | DevOps | `backend-engineer` | `release-check` | hazır | Docker Compose, GitHub Actions |
| 17 | Performans | `code-reviewer` | `perf-profile` | hazır | Embedding toplu üretim, pgvector sorgu süresi |
| 18 | Test | `test-engineer` | `test-engineering` | etkin | pytest, sözleşme, hook ve arayüz testleri |

Destek yetkinlikleri (18'in dışında, sistemin işlemesi için gerekli):

| Yetkinlik | Sorumlu ajan | Skill'ler | Durum | Projedeki karşılığı |
|---|---|---|---|---|
| Teknik araştırma | `researcher` | `tech-research` | etkin | Model, kütüphane ve standart doğrulama |
| Gereksinim ve planlama | `engineering-orchestrator` | `plan-task` | etkin | Görev bölme, kabul kriterleri |
| Dokümantasyon denetimi | `docs-auditor` | `docs-sync` | etkin | Belge–kod–test uyumu |
| Kod inceleme ve refaktör | `code-reviewer` | `code-review` | etkin | Birleştirme öncesi bağımsız inceleme |
| Veri etiketleme | `annotation-assistant` | `label-propose` | etkin | Etiket önerisi (insan onaylı) |
| Deney ve ölçüm | `evaluator` | `agreement-kappa`, `experiment-run` | etkin | κ, P/R/F1, deney (a)–(c) |
| Hata ayıklama | `test-engineer` | `debug` | etkin | Yeniden üret, daralt, regresyon testi |
