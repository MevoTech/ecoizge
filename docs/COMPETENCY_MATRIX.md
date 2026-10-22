# Yetkinlik Matrisi

Kullanıcının 2026-10-22 tarihli listesindeki 18 yetkinliğin her biri bir **sorumlu ajana** bağlıdır. Kural 2 "ajan **veya** skill" ister: her yetkinliği bir ajan kapsar, skill ise yalnızca o yetkinlik için tekrar eden ve projeye özgü bir iş akışı varsa yazılır.

- **Ajan:** uzmanlığı yürüten bağımsız rol. Yöntemleri ve projeye özgü bilgileri ajan dosyasındadır.
- **Skill:** çalışan betikleri, çözümlü örnekleri ve tuzak listesi olan iş akışı.

Denetim: `tools/check_consistency.py`. Kontrol ettikleri:
- her ajan `.claude/agents/` içinde var;
- yazılan her skill `.claude/skills/<ad>/SKILL.md` olarak var ve o ajanın "Kullandığı skill'ler" listesinde;
- 18 yetkinliğin hepsi tabloda.

Durum:
- **etkin:** şu fazda kullanılıyor.
- **hazır:** ilgili fazda kullanılacak.
- **etkin değil:** proje kapsamı dışında; kapsam değişirse ADR ile açılır.

| # | Yetkinlik | Sorumlu ajan | Skill'ler | Durum | Projedeki karşılığı ve ajan dosyasındaki yeri |
|---|---|---|---|---|---|
| 1 | Yazılım mimarisi | `architect` | `adr` | etkin | İki servis + ortak DB + JSON sözleşmesi; "Projeye özgü bilgiler" |
| 2 | Algoritmalar | `code-reviewer` | — | etkin | Eşleme karmaşıklığı, unsur kapsama özyinelemesi; inceleme kontrol listesi |
| 3 | Veri yapıları | `code-reviewer` | — | etkin | Paragraf × madde matrisi, indeks seçimi; inceleme kontrol listesi |
| 4 | İşletim sistemleri | `backend-engineer` | — | hazır | Süreç, bellek, disk, konteyner kaynağı teşhisi; Prosedür adım 5 |
| 5 | Bilgisayar ağları | `backend-engineer` | — | hazır | Compose ağı, port, TLS, servisler arası HTTP; Prosedür adım 5 |
| 6 | Veritabanları | `architect` | — | hazır | Şema, kısıt, `company_id`, pgvector boyutu (F3); uygulama `backend-engineer` |
| 7 | Backend | `backend-engineer` | `label-review` | etkin | FastAPI, Alembic, onay arayüzü |
| 8 | Frontend | `frontend-engineer` | — | etkin değil | React panel (F3 sonrası; kullanıcı şimdilik istemiyor) |
| 9 | Mobil | `frontend-engineer` | — | etkin değil | Kapsam dışı (Teknik Kapsam 6) |
| 10 | Yapay zekâ | `ml-engineer` | `rag-draft`, `colab-train` | etkin | LLM ile kaynaklı taslak, yer tutuculu üretim |
| 11 | Makine öğrenmesi | `ml-engineer` | `gap-baseline`, `colab-train` | etkin | TF-IDF+LR taban çizgisi, BERT ince ayarı; Zemzem'in tahmin modelleri |
| 12 | NLP / RAG | `ml-engineer` | `pdf-extract`, `embed-eval`, `rag-draft`, `numeric-verify` | etkin | Çıkarım, retrieval, üretim, doğrulama |
| 13 | Bilgisayarlı görü | `ml-engineer` | — | etkin değil | Yalnızca taranmış PDF çıkarsa OCR (`pdf-extract` → `ocr_gerekli`) |
| 14 | Gömülü sistemler | `architect` | — | etkin değil | Kapsam dışı; sayaç veya IoT veri girişi eklenirse ADR |
| 15 | Siber güvenlik | `security-auditor` | — | etkin | Tehdit modeli T1–T10, OWASP LLM; denetçi kontrol listesi |
| 16 | DevOps | `backend-engineer` | — | hazır | Docker Compose, GitHub Actions; `tools/check_all.py` |
| 17 | Performans | `code-reviewer` | — | hazır | Boyut tahmini, yaklaşık arama riski; uygulamada `backend-engineer` profil komutları |
| 18 | Test | `test-engineer` | `numeric-verify` | etkin | pytest, kanca, sözleşme, skill betiği ve arayüz testleri |

Destek yetkinlikleri (18'in dışında, sistemin işlemesi için gerekli):

| Yetkinlik | Sorumlu ajan | Skill'ler | Durum | Projedeki karşılığı |
|---|---|---|---|---|
| Teknik araştırma | `researcher` | — | etkin | Birincil kaynak sırası, not şablonu |
| Gereksinim, planlama ve koordinasyon | `engineering-orchestrator` | `adr` | etkin | Görev bölme, yönlendirme, kalite kapısı |
| Katalog yönetimi | `engineering-orchestrator` | `catalog-update` | etkin | Standart maddeleri, sürümleme |
| Dokümantasyon denetimi | `docs-auditor` | — | etkin | Etiket ve tek kaynak denetimi |
| Kod inceleme ve refaktör | `code-reviewer` | — | etkin | Proje kuralları kontrol listesi |
| Veri etiketleme | `annotation-assistant` | `label-propose` | etkin | Etiket önerisi (insan onaylı) |
| İnsan onayı | `engineering-orchestrator` | `label-review` | etkin | Onay arayüzü akışı |
| Deney ve ölçüm | `evaluator` | `agreement-kappa`, `experiment-run`, `embed-eval` | etkin | κ, P/R/F1, Recall@k, deneyler a–m |
