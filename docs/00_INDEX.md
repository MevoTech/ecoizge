# Belge Haritası ve Okuma Sırası

Bu klasör raporlama modülünü bugünkü durumundan (F1, araştırma) tez teslimine (F8, Mayıs 2027) taşıyan geliştirme rehberidir. Her dosyanın somut bir işlevi vardır; işlevi olmayan belge eklenmez.

## 1. Dosyalar ve sorumlulukları

| Dosya | Amaç | Ne zaman kullanılır | Bağlı olduğu dosyalar |
|---|---|---|---|
| [../AGENTS.md](../AGENTS.md) | Bütün ajanlar için bağlayıcı kurallar | Her oturum (otomatik) | Tümü |
| [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) | S01–S27: görevler, bağımlılıklar, kabul, doğrulama, geri dönüş | `/start-phase`, `/phase-gate` | PROGRESS, REQUIREMENTS |
| [PROGRESS.md](PROGRESS.md) | Tek ilerleme kaynağı: durum, kullanıcı eylemleri, riskler, kanıt günlüğü, ertelenenler, otonom kararlar | Her oturum | DEVELOPMENT_PLAN |
| [DECISIONS.md](DECISIONS.md) | ADR-001…, açık kararlar (D-xx), çelişki kaydı (C-xx) | Her aşamanın başında; yeni karar alındığında | Tümü |
| [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) | Bilinçli olarak tamamlanmamış işler ve çıkış yolları (KL-xx) | Kısıt bulunduğunda; tez "sınırlılıklar" bölümü | DEVELOPMENT_PLAN |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Gereksinimler (R-*); kimliklerin tek tanım yeri | Aşama açılırken, kabul yazılırken | TRACEABILITY |
| [TRACEABILITY.md](TRACEABILITY.md) | Gereksinim → aşama → test → durum | Faz sonu, tez yazımı | REQUIREMENTS, PROGRESS |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Servisler, veri akışı, katmanlar | S06, S09–S10, S25 | DATA_MODEL, API_SPEC |
| [DATA_MODEL.md](DATA_MODEL.md) | Tablolar, ortak çekirdek, sahiplik | S06, S09 | ARCHITECTURE |
| [API_SPEC.md](API_SPEC.md) | Uçlar, sürüm, hata modeli, ortak JSON sözleşmesi | S06, S10, S11, S20 | DATA_MODEL, SECURITY |
| [SECURITY.md](SECURITY.md) | Tehdit modeli, veri sınıfları, yükleme, enjeksiyon, kiracı izolasyonu | S10, S17, S18 ve her güvenlik kritik değişiklik | `.claude/rules/security.md` |
| [TEST_PLAN.md](TEST_PLAN.md) | Test katmanları, kalite kapısı, deneyler | Her aşama | AGENTS §7 |
| [AI_WORKFLOW.md](AI_WORKFLOW.md) | Roller, oturum protokolü, aşama döngüsü, bağımsız denetim, durma noktaları | Her oturum | AGENTS, ORCHESTRATION |
| [ORCHESTRATION.md](ORCHESTRATION.md) | Ajan yönlendirme tablosu, çelişki çözümü | Görev dağıtırken | `.claude/agents/` |
| [COMPETENCY_MATRIX.md](COMPETENCY_MATRIX.md) | Yetkinlik → ajan → skill | Yeni iş türü geldiğinde | ORCHESTRATION |
| [labeling/etiket_kilavuzu_v0.md](labeling/etiket_kilavuzu_v0.md) | 2 / 1 / U / NONE etiket tanımları ve örnekler | S05, S07, S12 | `data/catalog/` |
| [kullanim/ELLE_KONTROL_VE_PILOT.md](kullanim/ELLE_KONTROL_VE_PILOT.md) | Kullanıcı kılavuzu: Windows kurulumu, çıkarım kontrolü, kör etiketleme | U-01…U-04 | S04, S05, S07 |
| [audits/README.md](audits/README.md) | Bağımsız denetim ve inceleme raporları | 🔒 aşama kapanışı | AI_WORKFLOW §6 |
| [analysis/](analysis/) | Geçmiş analiz ve denetim raporları (00–03); salt tarihsel | Karar gerekçesi ararken | DECISIONS |

## 2. Okuma sırası

**İlk kez gelen ajan ya da geliştirici:** `../AGENTS.md` → bu dosya → `DECISIONS.md` → `PROGRESS.md` → aktif aşamanın `DEVELOPMENT_PLAN.md` bölümü → bölümün "Girdi" satırı.

**Aşamaya göre zorunlu okuma:**

| Aşama | Zorunlu belgeler |
|---|---|
| S01 Ajan altyapısı | AI_WORKFLOW, ORCHESTRATION, COMPETENCY_MATRIX, `.claude/hooks/write_scopes.json` |
| S02 Katalog | etiket kılavuzu, DECISIONS (ADR-008, ADR-010), `.claude/skills/catalog-update/SKILL.md` |
| S03–S04 Derlem, çıkarım | `.claude/rules/turkce-tdk.md`, `.claude/skills/pdf-extract/SKILL.md`, KNOWN_LIMITATIONS (KL-01, KL-02, KL-04) |
| S05, S07 Etiketleme, arayüz | etiket kılavuzu, `.claude/skills/label-propose/SKILL.md`, `.claude/skills/label-review/SKILL.md`, kullanım kılavuzu |
| S06, S11 Şema, sözleşme | REQUIREMENTS, DATA_MODEL, API_SPEC |
| S08 Yöntem kararları | DECISIONS (ADR-007…012), `docs/analysis/00_ANALIZ_RAPORU.md` |
| S09–S10 Altyapı, servis | ARCHITECTURE, DATA_MODEL, SECURITY |
| S12 Altın küme | `.claude/rules/data.md`, `.claude/rules/security.md` |
| S13–S16 Model | `.claude/skills/embed-eval/SKILL.md`, `.claude/skills/gap-baseline/SKILL.md`, `.claude/skills/colab-train/SKILL.md` |
| S17–S18 Taslak, doğrulama | SECURITY, `.claude/skills/rag-draft/SKILL.md`, `.claude/skills/numeric-verify/SKILL.md` |
| S19, S22–S24 Deney, tez | TEST_PLAN, `.claude/skills/experiment-run/SKILL.md` |
| S20–S21, S25–S27 Entegrasyon, web | API_SPEC, ARCHITECTURE |

## 3. Tutarlılık kuralları

- **Tek kaynak ilkesi:** Bir bilgi yalnızca bir dosyada tanımlanır, diğerleri bağlantı verir.
  - Plan ve kabul kriterleri → DEVELOPMENT_PLAN
  - Durum ve kanıt → PROGRESS
  - Karar → DECISIONS
  - Kısıt → KNOWN_LIMITATIONS
  - Gereksinim kimliği → REQUIREMENTS
  - Yazma alanı → `.claude/hooks/write_scopes.json`
- **Kimlikler:**

  | Kimlik | Anlamı |
  |---|---|
  | `Sxx` | aşama |
  | `Sxx.Tm` | görev |
  | `R-AAA-nn` | gereksinim |
  | `ADR-xxx` | karar |
  | `D-xx` | açık karar |
  | `C-xx` | çelişki |
  | `KL-xx` | bilinen kısıt |
  | `U-xx` | kullanıcı eylemi |
  | `R-xx` | risk |

- **Belgeyi kodla birlikte güncelle:** Davranışı değiştiren dal ilgili belgeyi de günceller. `/phase-gate` bunu denetler.
- **Mekanik denetim:** `python tools/check_consistency.py` şunları sınar:
  - plan biçimi;
  - plan ile PROGRESS §1 durum uyumu;
  - gereksinim kapsaması;
  - U, KL, D, C ve ADR atıflarının tanımlı olması;
  - ✅ aşamaların kanıt kaydı;
  - yol ve bağlantıların gerçek dosyalara işaret etmesi.
