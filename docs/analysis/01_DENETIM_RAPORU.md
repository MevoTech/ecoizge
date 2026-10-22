# Denetim Raporu: Ajan–Skill Mimarisi v0 → v1

Tarih: 2026-10-22 · Denetlenen: `00_ANALIZ_RAPORU.md` (v0 önerisi) · Ölçüt: kullanıcının 10 zorunlu kuralı (2026-10-22)

Bu rapor, v0 önerisinin yeni kurallarla çelişen ve eksik kalan yönlerini listeler ve her biri için v1'de uygulanan çözümü verir. v0 bir öneriydi; dosya olarak yalnızca katalog, kılavuz, şablon ve analiz raporu vardı. Ajan, skill, hook ve kod yoktu.

## 1. İncelenen dosyalar

| Dosya | Durum (denetim öncesi) |
|---|---|
| `README.md` | 8 satır. Ajan sistemine ve komutlara değinmiyor |
| `.gitignore` | Var. `data/gold/` için kural yok (gold git'e girmeli, bu doğru), `runs/` model dosyaları için kural yok |
| `data/catalog/catalog_v0.csv` | 93 satır. Doğrulayıcı betiği repoda yoktu, oturumda tek seferlik koşulmuştu |
| `data/labels/etiket_sablonu.csv` | Yalnızca başlık. Repoda bunu doğrulayan bir betik yoktu |
| `docs/labeling/etiket_kilavuzu_v0.md` | Kılavuz. 7. bölümdeki süreç repoda hiçbir mekanizmaya bağlı değildi |
| `docs/analysis/00_ANALIZ_RAPORU.md` | v0 önerisi. Aşağıdaki çelişkiler bunun içinde |
| `CLAUDE.md`, `.claude/**`, `tasks/`, kod, testler | **Yok** |

## 2. Çelişkiler (v0 öneri ↔ kurallar ↔ Claude Code'un gerçek davranışı)

| # | Çelişki | Kaynak | v1 çözümü |
|---|---|---|---|
| Ç1 | v0 orkestratörü "dosya değil, CLAUDE.md" olarak tanımlıyordu. Kural 1 tek ana ajan istiyor: `engineering-orchestrator` | v0 3.2, Kural 1 | `.claude/agents/engineering-orchestrator.md` yazıldı. `.claude/settings.json` içinde `"agent": "engineering-orchestrator"` ile ana oturum bu ajan olarak açılıyor (Claude Code: `agent` ayarı, ana oturum ajanı) |
| Ç2 | v0 "alt ajanlar alt ajan çağıramaz" varsayımıyla yazıldı. Gerçekte Claude Code'da alt ajanlar varsayılan olarak 3 katman derinliğe kadar alt ajan başlatabiliyor | Subagents belgesi, "Nesting rules"; Kural 9 | Hiçbir alt ajanın `tools` listesinde `Agent` yok. Ek olarak `settings.json` `env` bloğunda `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` ayarlı. Koordinasyon yalnızca orkestratör üzerinden yürüyor. `tools/check_consistency.py` bunu denetliyor |
| Ç3 | v0 6 yetkinliği (mobil, bilgisayarlı görü, gömülü, ağ, işletim sistemleri, dağıtık sistemler) "gereksiz" diye dışarıda bıraktı. Kural 2 hepsinin kapsanmasını istiyor | v0 3.1, Kural 2 | `docs/COMPETENCY_MATRIX.md`: 18 yetkinliğin her biri bir ajana ve en az bir skill'e bağlı. Projede kullanılmayanlar ajan olarak değil, **etkin değil** işaretli skill olarak tanımlı. Tetiklenme koşulları yazılı |
| Ç4 | v0 "yazma alanları ajan düzeyinde tam kısıtlanamıyor" deyip yalnızca tabloyla bıraktı | v0 3.2, Kural 5 | Hook girdisinde `agent_type` alanı var (Hooks belgesi). `.claude/hooks/guard.py` her Write ve Edit işleminde ajanın yazma alanını `.claude/hooks/write_scopes.json`'dan okuyup alan dışına yazmayı engelliyor. Yazma alanları ajanlar arasında ayrık |
| Ç5 | Paralel çalışmada aynı dosyaya yazma yalnızca bir cümleyle yasaklanmıştı | v0 3.3, Kural 5 | (a) Yazma alanları ayrık, bu yüzden iki *farklı* ajan aynı dosyaya yazamıyor. (b) Aynı ajandan iki örnek paralel çalışacaksa `isolation: worktree` zorunlu (ORCHESTRATION.md §4) |
| Ç6 | v0'da `nlp-rag-engineer` ve sonradan tanımlanacak `forecast-ml-engineer` vardı. İki ayrı ML ajanı aynı yöntem bilgisini tekrar ediyor | v0 3.2, Kural 3 | Tek bir `ml-engineer` var. Modül farkını skill'ler taşıyor (`rag-draft`, `forecast-modeling` vb.) |
| Ç7 | Skill adları v0 içinde tutarsızdı: `contract-check` ile API sözleşmesi, `label-review-export` ile onay arayüzü | v0 4 | Adlar `api-contract` ve `label-review` olarak sabitlendi. Denetleyici, her referansın gerçek bir skill dizinine karşılık geldiğini doğruluyor |
| Ç8 | v0 adım planını `docs/plan/steps/` altına koydu. Kural 4 `tasks/` istiyor | v0 7–8 | `tasks/S01…S24.md` + `tasks/README.md`. Her görev YAML önbilgisinde ajan, skill, gereksinim ve bağımlılık taşıyor; denetleyici bunları çapraz kontrol ediyor |
| Ç9 | v0 B1, B3, B4, B7 ve B13'ü danışman kararına bırakmıştı. Kullanıcı 2026-10-22'de "danışmana gitmeye gerek yok" dedi ve B10'u onayladı | v0 2.4, kullanıcı | Kararlar `docs/DECISIONS.md`'de ADR olarak, karar sahibi Mehmet olarak kaydedildi. ADR-004 kabul edildi; ADR-007…ADR-012 "önerildi" durumunda, Mehmet'in onayını bekliyor (görev S08). Hepsi geri alınabilir |
| Ç10 | v0 H4 kontrolü için pre-commit önerdi; ama ne pre-commit yapılandırması ne betik vardı | v0 5 | Tek komut: `python tools/check_all.py` (ruff, pytest, veri doğrulayıcı, tutarlılık denetleyicisi, gold manifest). Aynı komut CI'da koşuyor (`.github/workflows/ci.yml`). pre-commit isteğe bağlı bırakıldı |
| Ç11 | v0 "insan onayı" diyordu, ama alt ajanların kullanıcıya soru soramadığını mekanizma olarak ele almıyordu | Subagents belgesi (`AskUserQuestion` alt ajanlardan kaldırılır) | Onay gerektiren her şey alt ajan çıktısında "Onay gerektirenler" başlığına yazılıyor. Kullanıcıya yalnızca orkestratör soruyor ya da iş onay arayüzüne gidiyor (ORCHESTRATION.md §6) |
| Ç12 | v0 güvenlik denetçisini "salt-okunur" tanımladı ama Bash izni veriyordu. Bash ile dosya yazılabilir | v0 3.2 | Denetçi ajanlarda Bash yok: `code-reviewer`, `security-auditor` ve `docs-auditor`'ın araçları Read, Grep ve Glob. Testleri ve taramaları orkestratör `check_all.py` ile koşturup çıktıyı denetçiye veriyor. Bash'li ajanlar için kalan risk §4'te |

## 3. Eksikler (v0'da hiç olmayan)

| # | Eksik | v1'de |
|---|---|---|
| E1 | Ajan girdi ve çıktı sözleşmesi | `.claude/rules/orchestration.md` (ortak çıktı biçimi) + her ajan dosyasında girdi ve çıktı bölümü |
| E2 | Kabul kriteri, test komutu, kanıt ve hata prosedürü | `.claude/rules/quality-gates.md` + her `tasks/Sxx.md` dosyasında ayrı bölümler |
| E3 | Gereksinim kimlikleri ve izlenebilirlik | `docs/REQUIREMENTS.md` (R-*), `docs/TRACEABILITY.md`; denetleyici iki yönlü kontrol ediyor |
| E4 | Çalışan doğrulama betikleri | `tools/validate_data.py`, `tools/kappa.py`, `tools/gold_manifest.py`, `tools/check_consistency.py`, `tools/check_all.py` |
| E5 | B10 (yer tutuculu üretim) ve B9 (Türkçe sayı) için kod | `report_service/generation/placeholders.py`, `report_service/verify/numbers.py` + testler |
| E6 | Onay arayüzü | `services/review-ui/` (Streamlit) + mantık testleri + AppTest |
| E7 | Ortak sözleşme | `shared/contracts/forecast_record.schema.json`. S-19'daki örnek kayıtla test ediliyor |
| E8 | Gerçek durum kaydı | `docs/PROGRESS.md`: hangi komut koştu, sonuç ne, neyin test edilemediği |

## 4. Kapatılamayan ya da kısmen kapatılan riskler

1. **Bash ile yazma alanı aşımı.** Bash'li ajanlar (`backend-engineer`, `ml-engineer`, `test-engineer`, `annotation-assistant`, `evaluator`) shell komutuyla alan dışına yazabilir.
   - Guard hook Bash komutlarında korumalı yolları (`data/gold`, `data/labels/reviewed`, `data/raw/pilot`, `.env`, `secrets`) ve yıkıcı kalıpları engelliyor.
   - Ama genel yazma alanı Bash'te tam zorlanamıyor; bir komutun hangi dosyaya yazacağını statik olarak bilmek mümkün değil.
   - Dengeleyici kontroller: altın kümede SHA-256 manifest (CI'da kırmızı), PR incelemesi, `git diff` üzerinden orkestratör kontrolü.
2. **Canlı yönlendirme testi yapılmadı.** Ajan dosyaları biçim olarak doğrulandı ve hook'lar doğrudan JSON girdisiyle test edildi. Ama Claude Code'un bu ajanları gerçekten doğru göreve yönlendirip yönlendirmediği bu ortamda test edilemedi; bu oturum o çalışma zamanı değil. Senaryolar `tasks/S01-ajan-altyapisi.md` dosyasında; kullanıcının makinesinde koşulacak.
3. **`agent_type` alanının ana oturumdaki değeri.** Belgeye göre `--agent` ya da `agent` ayarı varken mevcut. Alan gelmezse guard ana oturumu orkestratör sayıyor. Bu varsayım canlı testte doğrulanacak (S01).
