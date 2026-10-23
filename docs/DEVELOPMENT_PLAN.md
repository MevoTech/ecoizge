# Geliştirme Planı: Raporlama Modülü (Mehmet Güneş)

Bu dosya raporlama modülünün **tek planıdır**: aşamalar, görevler, kabul kriterleri, doğrulama komutları ve geri dönüş yolları burada yazılır. Durum ve kanıtlar yalnızca [PROGRESS.md](PROGRESS.md)'dedir. Takvim: Geliştirme 2 (F1–F8, Ekim 2026 – Mayıs 2027). Tahminleme modülü (Zemzem Boyluğ) bu planda yalnızca ortak noktalarıyla (S06, S11, S20) yer alır.

## 0. Nasıl kullanılır

- **Başlatma:** `/start-phase Sxx` ([.claude/skills/start-phase/SKILL.md](../.claude/skills/start-phase/SKILL.md)). Ön koşullar → girdi belgeleri → plan PROGRESS §4'e → dal `asama/Sxx-kisa-ad` → uygulama.
- **Kapatma:** `/phase-gate` ([.claude/skills/phase-gate/SKILL.md](../.claude/skills/phase-gate/SKILL.md)). Test → çalıştır → kabul maddeleri tek tek → öz-denetim → kanıt → PROGRESS → birleştir → etiket `sxx-done`.
- **Görev kimliği:** `Sxx.Tm`. Commit gövdesinde `Refs: Sxx.Tm`.
- **Bağımlılık:** Bir aşama, bağımlılık satırındaki aşama veya görevler ✅ (ya da "✅ (✋ hariç)") olunca başlar. Aşamalar sıralı değil, bir bağımlılık ağıdır (§ Bağımlılıklar).
- **Ortak kabul kriterleri** (her aşamaya eklenir, tekrar yazılmaz):
  - **AK-G1:** `python tools/check_all.py` 6/6 GEÇTİ; çıktı özeti PROGRESS'te.
  - **AK-G2:** Davranışı değişen her şeyin belgesi aynı dalda güncel.
  - **AK-G3:** [AGENTS.md](../AGENTS.md) §7 öz-denetim soruları cevaplandı ve PROGRESS'e yazıldı.
  - **AK-G4:** Kod değiştiyse `code-reviewer` incelemesi yapıldı. Güvenlik kritikse ayrıca `security-auditor` incelemesi yapıldı. Kritik bulgu açık değil.
  - **AK-G5:** Kodda yeni TODO yok; yapılamayanlar [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)'de (KL-xx).
- **Simgeler:**
  - Görev: ✅ kanıtlı · 🟨 sürüyor · ⬜ başlamadı · ✋ kullanıcı eylemi (U-xx) · ⛔ engelli.
  - 🔒 Geri dönüşü zor karar içeren aşama. Kapanıştan önce bağımsız denetim zorunlu ([AI_WORKFLOW.md](AI_WORKFLOW.md) §6). Rapor: `docs/audits/Sxx.md`.
  - ✋ işaretli görevleri ajan yapmaz. Yalnızca ✋ görevleri eksik kalan aşama "✅ (✋ hariç)" kapanır.
- **Boyut:** S (≤ 2 oturum) · M (3–6) · L (7+). Tahmindir.
- **Ortak geri dönüş:** Aşama dalı birleşmeden önce terk edilebilir. Birleştikten sonra `git revert` ya da önceki `sxx-done` etiketinden yeni dal. Veri dosyalarında (katalog, etiket, altın küme) geri dönüş yalnızca yeni sürümle yapılır, eski sürüm silinmez.

## Bağımlılıklar

```text
F1  S01 ─┬─ S02 (🔒) ─────────────────────────┐
         ├─ S06 (🔒) ─ S09 ─ S10 ─────────────┤
         ├─ S07 ─┐                            │
S03 ─ S04 ───────┴─ S05 ─┬─ S12 (🔒) ─────────┤
                         ├─ S13 ─ S17 (🔒) ─ S18 (🔒)
                         ├─ S14 ─ S16         │
                         └─ S19               │
S06 ─ S11 (🔒) ─ S20 ─ S21                    │
S08 (🔒) ─ S16, S17                           │
S09 ─ S25 ─ S26 ─ S27                         │
S12, S16, S18 ─ S22 (🔒) ─ S23 ─ S24 ─────────┘
S15 bağımsız (tamamlandı)
```

Teknik gerekçe: S05 etiket üretmeden S12–S14, S19 ölçülemez. S08'deki kararlar (D-01…D-06) S16 ve S17'nin yöntemini belirler. S22, altın küme (S12), BERT kolu (S16) ve doğrulama katmanı (S18) olmadan koşulamaz.

---

## F1 · Araştırma ve alan (12 Eki – 15 Kas)

## S01: Ajan, skill, kural ve kanca altyapısı · M · F1
- **Durum:** ✅ (✋ hariç)
- **Sorumlu:** `engineering-orchestrator` · **Skill'ler:** `adr` · **Gereksinimler:** R-AGT-01, R-SEC-02 · **Bağımlılık:** —
- **Amaç:** Ajan sistemini çalışır, denetlenebilir ve testli hâle getirmek; aşama protokolünü kurmak.
- **Girdi:** Kullanıcı kuralları 1–10; [analysis/01_DENETIM_RAPORU.md](analysis/01_DENETIM_RAPORU.md); noor deposundaki belge yapısı (2026-10-23).
- **Görevler:**
  - T1 ✅ 1 ana + 11 alt ajan; `settings.json` `"agent"`, alt ajan derinliği 1 (ADR-001, ADR-002).
  - T2 ✅ `guard.py` + `write_scopes.json`; yazma, okuma ve Bash denetimi (ADR-003).
  - T3 ✅ 12 betikli skill; betiklerin testleri (2026-10-22).
  - T4 ✅ `tools/check_consistency.py`, `tools/check_all.py`, CI (kalite kapısı + gitleaks).
  - T5 ✅ noor yapısı: bu plan, PROGRESS (6 bölüm), [00_INDEX.md](00_INDEX.md), [AGENTS.md](../AGENTS.md), [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md), [AI_WORKFLOW.md](AI_WORKFLOW.md), `/start-phase` ve `/phase-gate`; denetleyici plan ile PROGRESS'i karşılaştırır.
  - T6 ✋ U-08: Claude Code ya da Antigravity oturumunda 6 canlı yönlendirme senaryosu ([analysis/00_ANALIZ_RAPORU.md](analysis/00_ANALIZ_RAPORU.md) §9).
- **Çıktılar:** `.claude/`, `.agents/`, `tools/`, belgeler, testler.
- **Kabul:** `check_all` 0. Guard ve denetleyici testleri, kasıtlı bozmada kırmızıya dönüyor. Plan ve PROGRESS durumları denetleyiciyle eşleşiyor. 6 canlı senaryonun sonucu PROGRESS'te.
- **Doğrulama:** `python tools/check_all.py`; `python -m pytest -q tests/hooks tests/tools`.
- **Geri dönüş:** `git revert`. Ana ajanı kapatmak için `settings.json`'dan `agent` anahtarı kaldırılır.

## S02: Katalog v1: TSRS 1 çekirdek ve alt maddelere bölme 🔒 · M · F1
- **Durum:** ⬜
- **Sorumlu:** `engineering-orchestrator` · **Skill'ler:** `catalog-update` · **Gereksinimler:** R-KAT-01, R-GAP-03 · **Bağımlılık:** S01, S08.T2
- **Amaç:** Kataloğu MVP kapsamına (D-04) genişletmek ve çok unsurlu maddeleri bölmek (D-02).
- **Girdi:** `data/catalog/catalog_v0.csv`; KGK TSRS 1 ve TSRS 2 resmî metni; [labeling/etiket_kilavuzu_v0.md](labeling/etiket_kilavuzu_v0.md).
- **Görevler:**
  - T1 ⬜ TSRS 1 çekirdek maddeleri resmî metinden çıkarılır; her satırda `dogrulama` kaynak ve tarih taşır.
  - T2 ⬜ Çok unsurlu maddeler `-a/-b` ile bölünür; üst madde `ust_madde` sütununda.
  - T3 ⬜ Fark raporu: `diff_catalog.py v0 v1`.
  - T4 ✋ U-09: Mehmet katalog v1'i onaylar.
- **Çıktılar:** `data/catalog/catalog_v1.csv`, fark listesi.
- **Kabul:** Doğrulayıcı geçer. Her yeni satırda resmî kaynak ve tarih var. Bölünen her alt madde bir üst maddeye bağlı. Onay kaydı PROGRESS'te.
- **Doğrulama:** `python tools/validate_data.py data/catalog/catalog_v1.csv`; `python .claude/skills/catalog-update/scripts/diff_catalog.py data/catalog/catalog_v0.csv data/catalog/catalog_v1.csv`.
- **Geri dönüş:** v0 silinmez; v1 hatalıysa v2 yazılır. Etiketler katalog sürümüyle birlikte saklanır.

## S03: Rapor derlemi ve tarama tablosu · M · F1
- **Durum:** 🟨
- **Sorumlu:** `researcher` · **Skill'ler:** — · **Gereksinimler:** R-PDF-01 · **Bağımlılık:** —
- **Amaç:** Türkçe TSRS raporlarından oluşan, kaynağı ve özeti doğrulanmış bir derlem kurmak ve Geliştirme 2 §4 tarama tablosunu doldurmak.
- **Girdi:** KGK "Yayımlanan Raporlar", KAP ekleri, Borsa İstanbul, YÖKAK KİDR; [.claude/rules/turkce-tdk.md](../.claude/rules/turkce-tdk.md).
- **Görevler:**
  - T1 ✅ Kaynak listesi: 424 satır (KGK 198, KAP 11, BIST 10, KİDR 205) → `data/raw/public/KAYNAKLAR.csv`.
  - T2 ✅ `tools/rapor_derlemi.py`: indir, yerleştir, doğrula (`%PDF`, SHA-256, boyut, sayfa, dil), denetle; testli.
  - T3 ✅ İndirme: bulutta 418/424 doğrulandı; kullanıcının makinesinde 387, TSRS 161/161.
  - T4 ⬜ Tarama notu `docs/research/rapor_derlemi.md`: sektör, ölçek, standart, sayfa, dil; Geliştirme 2 §4 tablosu.
  - T5 ⬜ KOBİ sınıflandırması: ölçek bilgisi kaynakla (KAP şirket bilgisi, faaliyet raporu); ölçeği bulunamayan rapor açıkça "bilinmiyor".
  - T6 ⬜ Kavram sözlüğü `docs/research/kavram_sozlugu.md` (F1 çıktısı).
- **Çıktılar:** `KAYNAKLAR.csv`, tarama notu, kavram sözlüğü; PDF'ler git dışında (`Documents/ecoizge-raporlar`).
- **Kabul:** ≥ 10 rapor, her biri kaynak URL, erişim tarihi ve SHA-256 ile ✅. KOBİ sayısı ve sınıflandırma yöntemi yazılı (G2 §4). Tarama notu PROGRESS'ten bağlantılı.
- **Doğrulama:** `python tools/rapor_derlemi.py denetle --manifest data/raw/public/KAYNAKLAR.csv`; `python tools/rapor_derlemi.py ozet --manifest data/raw/public/KAYNAKLAR.csv`.
- **Geri dönüş:** Manifest satırları silinmez; geçersiz kaynak `durum=atlandi` ve not ile işaretlenir.

## S04: PDF çıkarım hattı v0 ve çıkarım kalite kümesi · M · F1
- **Durum:** 🟨
- **Sorumlu:** `ml-engineer` · **Skill'ler:** `pdf-extract` · **Gereksinimler:** R-PDF-01, R-PDF-02 · **Bağımlılık:** S03.T3
- **Amaç:** PDF → paragraf/tablo çıkarımı ve elle ölçülmüş kalite.
- **Girdi:** Pilot raporları (Derimod, Akbank, Klimasan, QUA Granite 2025); [.claude/skills/pdf-extract/SKILL.md](../.claude/skills/pdf-extract/SKILL.md).
- **Görevler:**
  - T1 ✅ `pipelines/extract.py`: üst/alt bilgi, başlık, tireleme, tablo hücresi, OCR gereken sayfa; sentetik PDF testli.
  - T2 ✅ 4 gerçek rapor çıkarıldı ve otomatik QA koşuldu; birimler `data/labels/pilot/birimler/`.
  - T3 ✅ Çıkarım kontrol ekranı (`services/review-ui`, "1 · Çıkarım kontrolü"): PDF sayfası ve birimler yan yana, 8 hata türü.
  - T4 ✋ U-03: Mehmet 20 sayfayı (rapor başına 5) ekranda kontrol eder.
  - T5 ⬜ QA raporu `reports/experiments/extraction-qa.md`: hata türü sayıları, hatasız sayfa oranı (`evaluator`).
  - T6 ⬜ PyMuPDF ile pdfplumber aynı 20 sayfada ölçülür; ADR (D-07).
  - T7 ⬜ Bulunan hatalar için önce kırmızı test, sonra düzeltme (KL-02, KL-04 adayları).
- **Çıktılar:** Birim dosyaları, `extraction-qa-elle.csv`, QA raporu, ADR.
- **Kabul:** 20 sayfada hata türleri sayılmış. Kütüphane seçimi ölçümle ADR'ye yazılmış. Çıktı şeması testli.
- **Doğrulama:** `python -m pytest -q tests/pipelines services/review-ui/tests`; `python pipelines/extract.py <pdf> --rapor-id <id> --out <jsonl>`; `streamlit run services/review-ui/app.py`.
- **Geri dönüş:** Çıkarım kodu değişirse etiketli raporlar yeniden çıkarılmadan önce kimlik eşlemesi yapılır (pdf-extract Tuzaklar: "Kimlik kayması").

## S05: Pilot etiketleme, κ ve kılavuz v1 · M · F1
- **Durum:** 🟨
- **Sorumlu:** `annotation-assistant` · **Skill'ler:** `label-propose`, `agreement-kappa`, `label-review` · **Gereksinimler:** R-ETK-01 · **Bağımlılık:** S04.T2, S07.T2
- **Amaç:** Yaklaşık 50 paragrafta kör etiketleme; insan–model κ; kılavuzun belirsizliklerini bulup v1'e geçmek.
- **Girdi:** `data/labels/pilot/orneklem.jsonl`; `data/catalog/catalog_v0.csv`; [labeling/etiket_kilavuzu_v0.md](labeling/etiket_kilavuzu_v0.md).
- **Görevler:**
  - T1 ✅ Örneklem: 4 rapor, 30 aday + 20 rastgele, 100–1.500 karakter, yinelenen metin yok, girdi sırasından bağımsız (`sample_pilot.py`, seed 43; SHA-256 `c180ccc1…`).
  - T2 ✅ Kör etiketleme ekranı ("2 · Kör etiketleme"). Ekran öneri dosyalarını okumaz; `annotation-assistant` `data/labels/blind/**` okuyamaz (guard).
  - T3 ✋ U-04: Mehmet 50 paragrafı kör etiketler. Çıktı: `data/labels/blind/<ad>/pilot_v0.csv`.
  - T4 ⬜ `annotation-assistant` aynı 50 paragrafa, insan etiketini görmeden öneri üretir → `data/labels/proposals/pilot_v0.csv`.
  - T5 ⬜ κ (insan–model) ve anlaşmazlık listesi → `reports/experiments/kappa-pilot.md` (`evaluator`).
  - T6 ⬜ Kılavuz v1: ayrışan durumlar §5'e işlenir; ✋ Mehmet onaylar.
  - T7 ⬜ D-06 kabul edilirse Zemzem 30–50 paragraflık alt kümeyi etiketler (U-15); insan–insan κ ayrı raporlanır.
- **Çıktılar:** Kör etiketler, öneriler, κ raporu, `docs/labeling/etiket_kilavuzu_v1.md`.
- **Kabul:** İki etiket dosyası doğrulayıcıdan geçer. κ raporu insan–model ve (varsa) insan–insan için ayrı. Anlaşmazlıklar kılavuz §5'e işlenmiş.
- **Doğrulama:** `python tools/validate_data.py data/labels/blind/<ad>/pilot_v0.csv`; `python tools/kappa.py <insan.csv> <model.csv>`.
- **Geri dönüş:** Etiket dosyaları sürümlüdür (`pilot_v0`); kılavuz değişirse yeni tur `pilot_v1` olarak etiketlenir.

## F2 · Gereksinim ve veri modeli (16 Kas – 6 Ara)

## S06: REQUIREMENTS, DATA_MODEL ve API_SPEC v1 uzlaştırması 🔒 · M · F2
- **Durum:** ⬜
- **Sorumlu:** `architect` · **Skill'ler:** `adr` · **Gereksinimler:** R-KAT-02, R-API-01, R-INT-01 · **Bağımlılık:** S01
- **Amaç:** Ortak şema ve sözleşmeyi iki öğrencinin onayıyla v1 yapmak.
- **Girdi:** [DATA_MODEL.md](DATA_MODEL.md), [API_SPEC.md](API_SPEC.md), [REQUIREMENTS.md](REQUIREMENTS.md); Teknik Kapsam §9–10.
- **Görevler:**
  - T1 ⬜ Ortak çekirdek (kullanıcı, şirket, dönem, KPI kaydı) tabloları ve sahipliği.
  - T2 ⬜ API v1: uçlar, `schema_version`, hata modeli, asenkron iş.
  - T3 ⬜ Rapor profili seçimi (R-KAT-02) veri modeline.
  - T4 ✋ U-06: ZemCeng GitHub'da ortak çalışan olarak eklenir.
  - T5 ✋ U-07: Zemzem PR'ı onaylar.
- **Çıktılar:** v1 belgeler, şemalar.
- **Kabul:** `docs-auditor` çelişki bulmuyor. Zemzem'in onayı PR'da.
- **Doğrulama:** `python tools/check_consistency.py`; `docs-auditor` raporu.
- **Geri dönüş:** v1 yayımlandıktan sonra değişiklik yeni sürümle (v1.1) ve iki onayla.

## S07: Onay arayüzü v1 ve toplu ön etiketleme · M · F2
- **Durum:** 🟨
- **Sorumlu:** `backend-engineer` · **Skill'ler:** `label-review` · **Gereksinimler:** R-HIL-01 · **Bağımlılık:** S01
- **Amaç:** Etiket, koşu ve taslak onaylarını tek arayüzde toplamak.
- **Girdi:** `services/review-ui/`; ADR-006.
- **Görevler:**
  - T1 ✅ Etiket onay kuyruğu: onayla, düzelt, reddet; günlük; doğrulayıcı uyumu; AppTest.
  - T2 ✅ Türkçe menü (`st.navigation`), Başlangıç, Çıkarım kontrolü ve Kör etiketleme ekranları; ekranlar AppTest ve tarayıcıda çalıştırıldı.
  - T3 ✅ Windows'ta kurulum ve açılış (`tools/windows/kurulum.bat`, `tools/windows/arayuz.bat`): kalite kapısı 6/6, ekranlar kullanıcının makinesinde açıldı, PDF sayfası çizildi (2026-10-23).
  - T4 ⬜ Koşu kuyruğu (`runs/*/run.json`) ve model kaydı durumu.
  - T5 ⬜ Toplu ön etiketleme: S05 sonrası kalan paragraflar için öneri → onay akışı.
  - T6 ⬜ Taslak kuyruğu (S17 ile).
- **Çıktılar:** `services/review-ui/`.
- **Kabul:** Her kuyruk AppTest ile testli. Arayüz kullanıcının Windows makinesinde açıldı ve kalite kapısı orada geçti.
- **Doğrulama:** `python -m pytest -q services/review-ui/tests`; `streamlit run services/review-ui/app.py`.
- **Geri dönüş:** Arayüz yalnızca dosya okur ve yazar; veriler etkilenmeden önceki sürüme dönülür.

## S08: Yöntem kararları (ADR-007…ADR-012) 🔒 · S · F2
- **Durum:** 🟨
- **Sorumlu:** `engineering-orchestrator` · **Skill'ler:** `adr` · **Gereksinimler:** R-GAP-04, R-GEN-02, R-EVL-02, R-SEC-03 · **Bağımlılık:** —
- **Amaç:** Analiz bulgularından (B1, B3, B4, B6, B7, B12, B13, B18) çıkan yöntem kararlarını kesinleştirmek.
- **Girdi:** [DECISIONS.md](DECISIONS.md) (ADR-007…012, D-01…D-06).
- **Görevler:**
  - T1 ✅ ADR-004 (yer tutuculu üretim) kabul edildi (2026-10-22).
  - T2 ✋ U-05: Mehmet D-01…D-06'yı (ADR-007…012) kabul eder ya da değiştirir.
- **Çıktılar:** ADR durumları `kabul` ya da revize.
- **Kabul:** "Önerildi" durumunda ADR kalmadı ya da kalanların gerekçesi PROGRESS'te.
- **Doğrulama:** `grep -c "önerildi" docs/DECISIONS.md`.
- **Geri dönüş:** Yeni ADR ile, eskisi "yerini aldı" olarak.

## F3 · Mimari, veritabanı, ortak sözleşme (7 Ara – 3 Oca)

## S09: Docker Compose, PostgreSQL + pgvector, Alembic · M · F3
- **Durum:** ⬜
- **Sorumlu:** `backend-engineer` · **Skill'ler:** — · **Gereksinimler:** R-SEC-04 · **Bağımlılık:** S06
- **Amaç:** Tek komutla ayağa kalkan geliştirme ortamı.
- **Girdi:** DATA_MODEL v1; [SECURITY.md](SECURITY.md).
- **Görevler:**
  - T1 ✋ U-14: Docker Desktop kurulur (WSL 2).
  - T2 ⬜ `docker-compose.yml`: PostgreSQL + pgvector, report-service, review-ui; sağlık denetimleri.
  - T3 ⬜ Alembic: ilk migration; upgrade → downgrade → upgrade döngüsü.
  - T4 ⬜ `audit_log` tetikleyicisi ve testi (R-SEC-04).
- **Çıktılar:** `docker-compose.yml`, `db/migrations/`.
- **Kabul:** `docker compose up` → servisler healthy. Migration döngüsü geçer. Denetim kaydı testli.
- **Doğrulama:** `docker compose up -d && docker compose ps`; `alembic upgrade head && alembic downgrade base && alembic upgrade head`.
- **Geri dönüş:** `docker compose down -v` ile geliştirme veritabanı sıfırdan kurulur.

## S10: report-service iskeleti, POST /reports, iş tablosu, yükleme güvenliği · L · F3
- **Durum:** ⬜
- **Sorumlu:** `backend-engineer` · **Skill'ler:** — · **Gereksinimler:** R-API-02, R-SEC-04 · **Bağımlılık:** S09, S04
- **Amaç:** Yükle → çıkar → veritabanı akışı, asenkron iş ve güvenli yükleme.
- **Girdi:** API_SPEC v1; [SECURITY.md](SECURITY.md).
- **Görevler:**
  - T1 ⬜ FastAPI iskeleti, `POST /reports`, `GET /jobs/{id}`.
  - T2 ⬜ Yükleme sınırları: boyut, sayfa, MIME (T8 tehdidi).
  - T3 ⬜ JWT ve şirket yetkisi (T9 tehdidi).
  - T4 ⬜ Çıkarım hattının işe bağlanması.
- **Çıktılar:** `report_service/api/`, `report_service/db/`.
- **Kabul:** Sınırlar, yetki ve iş durumu akışı testli.
- **Doğrulama:** `python -m pytest -q services/report-service/tests`.
- **Geri dönüş:** Migration ile; veri silen migration insan onayı ister ([.claude/rules/security.md](../.claude/rules/security.md)).

## S11: Ortak JSON sözleşmesi ve iki serviste sözleşme testleri 🔒 · S · F3
- **Durum:** 🟨
- **Sorumlu:** `architect` · **Skill'ler:** — · **Gereksinimler:** R-API-01, R-INT-01 · **Bağımlılık:** S06
- **Amaç:** Tahmin kaydı sözleşmesini iki tarafta da test edilir yapmak.
- **Girdi:** Sunum S-19; `shared/contracts/`.
- **Görevler:**
  - T1 ✅ `shared/contracts/forecast_record.schema.json` + örnek + test.
  - T2 ⬜ forecast-service çıktısı aynı testten geçer.
  - T3 ✋ U-07: Zemzem onaylar.
- **Çıktılar:** Şema, iki taraflı test.
- **Kabul:** Şema ve örnek testli. Tahmin servisinin çıktısı aynı testten geçer. Zemzem onayı.
- **Doğrulama:** `python -m pytest -q tests/contracts`.
- **Geri dönüş:** `schema_version` artırılır; eski sürüm bir dönem desteklenir.

## S25: Web arayüzü iskeleti, kimlik ve veri giriş formları · L · F3
- **Durum:** ⬜
- **Sorumlu:** `frontend-engineer` · **Skill'ler:** — · **Gereksinimler:** R-KAT-02, R-SEC-04 · **Bağımlılık:** S09, S06
- **Amaç:** Geliştirme 2'deki React arayüzü: giriş, şirket ve dönem seçimi, katalogdan üretilen KPI veri giriş formları.
- **Girdi:** API_SPEC v1; [ARCHITECTURE.md](ARCHITECTURE.md); Teknik Kapsam §4 (madde kataloglu yapı, kanıt belgesi).
- **Görevler:**
  - T1 ⬜ React + TypeScript iskeleti, kimlik akışı.
  - T2 ⬜ Rapor profili seçimi (R-KAT-02).
  - T3 ⬜ Katalogdan üretilen formlar: değer, birim, dönem, kaynak türü, kanıt belgesi; her değişiklik denetim kaydına.
- **Çıktılar:** `web/`.
- **Kabul:** Formlar katalogdan üretiliyor (elle yazılmış alan yok). Kayıtlar denetim kaydına düşüyor. Bileşen testleri geçer.
- **Doğrulama:** `web/` test komutu (iskeletle birlikte tanımlanır).
- **Geri dönüş:** Arayüz yalnızca API'yi kullanır; geri alma API'yi etkilemez.

## F4 · Çekirdek geliştirme (4 Oca – 28 Şub)

## S12: Altın test kümesini dondur 🔒 · S · F4
- **Durum:** ⬜
- **Sorumlu:** `engineering-orchestrator` · **Skill'ler:** `label-review` · **Gereksinimler:** R-ETK-02 · **Bağımlılık:** S05
- **Amaç:** Test raporlarının onaylı etiketlerini dondurmak.
- **Girdi:** Onaylı etiketler (test raporları); [.claude/rules/data.md](../.claude/rules/data.md).
- **Görevler:**
  - T1 ⬜ Test raporları rapor bazında seçilir; eğitim raporlarıyla kesişmez.
  - T2 ⬜ Test raporlarının tüm paragrafları insan onaylı.
  - T3 ✋ U-10: Mehmet `python tools/gold_manifest.py freeze --by "Mehmet Güneş"` komutunu kendisi çalıştırır.
  - T4 ⬜ CI'da `verify` yeşil.
- **Çıktılar:** `data/gold/`, `MANIFEST.json`.
- **Kabul:** Manifest var ve CI'da doğrulanıyor. Test raporları eğitimde yok.
- **Doğrulama:** `python tools/gold_manifest.py verify`.
- **Geri dönüş:** Altın küme değişmez; hata bulunursa yeni sürüm dondurulur ve eski sonuçlar sürüm notuyla raporlanır.

## S13: Embedding modeli seçimi · M · F4
- **Durum:** ⬜
- **Sorumlu:** `ml-engineer` · **Skill'ler:** `embed-eval`, `colab-train` · **Gereksinimler:** R-RET-01, R-REP-01 · **Bağımlılık:** S05
- **Amaç:** Aday embedding modellerini kendi kümemizde ölçüp seçmek (B2).
- **Girdi:** Doğrulama kümesi (altın küme değil); [.claude/skills/embed-eval/references/candidates.md](../.claude/skills/embed-eval/references/candidates.md).
- **Görevler:**
  - T1 ⬜ Sorgu–paragraf çiftleri onaylı etiketlerden.
  - T2 ✋ U-11: Colab defterini Mehmet çalıştırır.
  - T3 ⬜ Recall@k ve MRR tablosu; ADR.
- **Kabul:** Tüm adaylar aynı çiftlerde. Altın küme kullanılmadı. `run.json` kayıtlı.
- **Doğrulama:** `python .claude/skills/colab-train/scripts/run_record.py validate runs/<run_id>/run.json`.
- **Geri dönüş:** Seçim ADR ile; model değişirse vektörler yeniden üretilir.

## S14: TF-IDF + LR taban çizgisi, gruplu CV, eşikler, unsur kapsama · M · F4
- **Durum:** 🟨
- **Sorumlu:** `ml-engineer` · **Skill'ler:** `gap-baseline`, `colab-train` · **Gereksinimler:** R-GAP-01, R-GAP-02, R-GAP-03, R-EVL-01 · **Bağımlılık:** S05, S02
- **Amaç:** Deney (a)'nın taban kolu ve ilk F1.
- **Girdi:** Onaylı etiketler; katalog v1.
- **Görevler:**
  - T1 ✅ `baseline.py`: TF-IDF öznitelikleri + StandardScaler + LR, GroupKFold (sentetik veriyle testli).
  - T2 ✅ Unsur kapsama toplaması (`report_service/nlp/coverage.py`), birim testli.
  - T3 ⬜ Onaylı etiketlerle ilk F1, rapor bazında ortalama ± aralık.
  - T4 ⬜ τ₁/τ₂ eşikleri doğrulama kümesinde seçilir; ✋ kabul.
- **Kabul:** Rapor bazında bölünme testli. F1 rapor bazında ortalama ± aralıkla raporlanmış. Eşikler kabul edilmiş.
- **Doğrulama:** `python -m pytest -q tests/skills -k baseline`; `python .claude/skills/gap-baseline/scripts/baseline.py --help`.
- **Geri dönüş:** Model ve eşikler `run_id`'ye bağlı; önceki koşuya dönülür.

## S15: Türkçe sayı normalleştirici ve kip denetimi · S · F4
- **Durum:** ✅
- **Sorumlu:** `ml-engineer` · **Skill'ler:** `numeric-verify` · **Gereksinimler:** R-VER-01, R-VER-03 · **Bağımlılık:** —
- **Amaç:** Sayısal tutarlılık algoritmasının normalleştirme ve kip parçası.
- **Girdi:** B9 biçim listesi; [.claude/rules/turkce-tdk.md](../.claude/rules/turkce-tdk.md).
- **Görevler:**
  - T1 ✅ `verify/numbers.py`: Türkçe ayraç, ölçek, yüzde, birim, yıl.
  - T2 ✅ `verify/tense.py`: gerçekleşmiş ve tahmin kipi.
  - T3 ✅ Kasıtlı bozma denemesinde testler kırmızıya döndü.
- **Kabul:** Testler geçer; bilinen sınırlar modül belgesinde.
- **Doğrulama:** `python -m pytest -q services/report-service/tests`.
- **Geri dönüş:** —

## F5 · Derinleştirme (1 Mar – 4 Nis)

## S16: BERTurk / çok dilli ince ayar ve Türkçe spesifiklik başlığı · L · F5
- **Durum:** ⬜
- **Sorumlu:** `ml-engineer` · **Skill'ler:** `colab-train`, `gap-baseline` · **Gereksinimler:** R-GAP-02, R-GAP-04, R-REP-01 · **Bağımlılık:** S14, S08
- **Amaç:** Deney (a)'nın BERT kolu ve `s_spec` ablasyonu (D-01).
- **Girdi:** Onaylı etiketler; `assets/train_template.ipynb`.
- **Görevler:**
  - T1 ⬜ Colab defteri; tohum ve sürümler `run.json`'da.
  - T2 ✋ U-11: Mehmet defteri çalıştırır.
  - T3 ⬜ `s_spec` açık/kapalı ablasyonu.
  - T4 ⬜ Koşu onay arayüzünden kabul edilir.
- **Kabul:** Defter temiz çekirdekte çalıştı. Ablasyon sonucu `run_id`'ye bağlı.
- **Doğrulama:** `python .claude/skills/colab-train/scripts/run_record.py validate runs/<run_id>/run.json`.
- **Geri dönüş:** Model Drive'da sürümlü; kabul edilmemiş koşu kullanılmaz.

## S17: LLM seçimi, RAG yaz/tamamla, yer tutuculu üretim, injection testi 🔒 · L · F5
- **Durum:** 🟨
- **Sorumlu:** `ml-engineer` · **Skill'ler:** `rag-draft`, `numeric-verify` · **Gereksinimler:** R-GEN-01, R-GEN-02, R-GEN-03, R-GEN-04, R-SEC-01, R-SEC-03 · **Bağımlılık:** S08, S13
- **Amaç:** Kaynaklı Türkçe taslak üretimi.
- **Girdi:** ADR-004; D-02; D-05; [.claude/skills/rag-draft/SKILL.md](../.claude/skills/rag-draft/SKILL.md).
- **Görevler:**
  - T1 ✅ Yer tutucu doğrulama ve doldurma (`generation/placeholders.py`).
  - T2 ✅ İstem kurucu, belge metnini ayraçla ve temizleyerek verir (`build_prompt.py`).
  - T3 ✋ U-12: LLM seçimi ve API anahtarı (yeni harici servis, insan onayı).
  - T4 ⬜ `yaz` ve `tamamla` kipleri; kaynak atfı.
  - T5 ⬜ Talimat enjeksiyonu içeren sentetik PDF testi.
  - T6 ⬜ İstem sürümü kayıtlı ve onaylı.
- **Kabul:** Enjeksiyon testi geçer. İstem sürümü onaylı. Sayı içeren her cümle yer tutucudan geliyor.
- **Doğrulama:** `python -m pytest -q services/report-service/tests tests/skills -k "placeholder or prompt"`.
- **Geri dönüş:** İstem ve model sürümlüdür; önceki onaylı sürüme dönülür.

## S18: Doğrulama katmanı entegrasyonu, kaynaksız cümle, kiracı izolasyonu 🔒 · M · F5
- **Durum:** ⬜
- **Sorumlu:** `ml-engineer` · **Skill'ler:** `numeric-verify`, `rag-draft` · **Gereksinimler:** R-VER-02, R-VER-03, R-RET-02 · **Bağımlılık:** S17, S10
- **Amaç:** Taslak hattına doğrulamayı bağlamak.
- **Girdi:** S15, S17 çıktıları.
- **Görevler:**
  - T1 ⬜ Taslak → sayı denetimi → kaynaksız cümle işareti.
  - T2 ⬜ İki şirketli sızıntı testi (retrieval `company_id` filtresi).
- **Kabul:** Sızıntı testi ve kaynaksız cümle uyarısı testli.
- **Doğrulama:** `python -m pytest -q services/report-service/tests`.
- **Geri dönüş:** Doğrulama katmanı kapatılamaz; yalnızca deney (c) için ayrı bayrakla.

## S19: Maskeleme değerlendirme kümesi · M · F5
- **Durum:** ⬜
- **Sorumlu:** `evaluator` · **Skill'ler:** `experiment-run` · **Gereksinimler:** R-EVL-02 · **Bağımlılık:** S05
- **Amaç:** ROUGE-L ve BERTScore için referanslı küme (D-03).
- **Girdi:** Tam karşılanan (2) paragraflar.
- **Görevler:**
  - T1 ⬜ Küme rapor bazında bölünür.
  - T2 ⬜ Ölçüm betiği; BERTScore model adı yazılı.
- **Kabul:** Küme rapor bazında bölünmüş; ölçüm betiği testli.
- **Doğrulama:** `python -m pytest -q tests/skills -k bootstrap`.
- **Geri dönüş:** Küme sürümlü.

## S26: Boşluk matrisi ve taslak editörü · L · F5
- **Durum:** ⬜
- **Sorumlu:** `frontend-engineer` · **Skill'ler:** — · **Gereksinimler:** R-GAP-01, R-HIL-01 · **Bağımlılık:** S25, S17
- **Amaç:** Madde × durum matrisi ve kaynak atıflı taslağın düzenlenip onaylandığı ekran.
- **Girdi:** API_SPEC v1; S17 çıktı biçimi.
- **Görevler:**
  - T1 ⬜ Boşluk matrisi: tam / kısmi / eksik, kanıt paragrafına bağlantı.
  - T2 ⬜ Taslak editörü: kaynak atfı görünür; sayılar yer tutucudan; onay kaydı.
- **Kabul:** Matris API verisinden; onay kaydı R-HIL-01'e uygun. Bileşen testleri geçer.
- **Doğrulama:** `web/` test komutu.
- **Geri dönüş:** Yalnızca arayüz; veri etkilenmez.

## F6 · Entegrasyon (5 – 18 Nis)

## S20: Tahmin JSON'unun taslağa bağlanması · M · F6
- **Durum:** ⬜
- **Sorumlu:** `backend-engineer` · **Skill'ler:** `numeric-verify` · **Gereksinimler:** R-INT-01, R-VER-03 · **Bağımlılık:** S11, S17
- **Amaç:** Zemzem'in kayıtlarının `veri_turu` korunarak taslağa girmesi.
- **Girdi:** Sözleşme v1.
- **Görevler:**
  - T1 ⬜ `POST /exports/forecast-to-report`.
  - T2 ⬜ Tahmin kaydı taslakta "(tahmin)" ve öngörü kipiyle; uçtan uca test.
- **Kabul:** Gerçekleşmiş ve tahmin karışımı reddediliyor; uçtan uca test geçer.
- **Doğrulama:** `python -m pytest -q services/report-service/tests tests/contracts`.
- **Geri dönüş:** Uç sürümlüdür.

## S21: Uçtan uca demo ve DOCX/PDF dışa aktarım · M · F6
- **Durum:** ⬜
- **Sorumlu:** `backend-engineer` · **Skill'ler:** — · **Gereksinimler:** R-EXP-01 · **Bağımlılık:** S20
- **Amaç:** Yükle → analiz → taslak → onay → dışa aktar.
- **Görevler:**
  - T1 ⬜ Tek komutla demo betiği.
  - T2 ⬜ DOCX/PDF dışa aktarım; tahmin etiketleri korunur.
- **Girdi:** Tüm hat.
- **Kabul:** Tek komutla demo; dışa aktarımda tahmin etiketleri korunuyor.
- **Doğrulama:** Demo betiği (S21.T1 ile tanımlanır).
- **Geri dönüş:** —

## S27: Panel sayfası: tahmin ve senaryo grafikleri · M · F6
- **Durum:** ⬜
- **Sorumlu:** `frontend-engineer` · **Skill'ler:** — · **Gereksinimler:** R-INT-01 · **Bağımlılık:** S26, S11
- **Amaç:** Zemzem'in tahmin, senaryo ve duyarlılık çıktılarını grafikle göstermek (grafik çizimi Mehmet'tedir, Teknik Kapsam §9).
- **Girdi:** Sözleşme v1.
- **Görevler:**
  - T1 ⬜ Tahmin serisi ve güven aralığı grafiği.
  - T2 ⬜ Senaryo karşılaştırması ve duyarlılık sıralaması.
- **Kabul:** Grafikler sözleşmeye uyan gerçek veriden; uydurma sayı yok.
- **Doğrulama:** `web/` test komutu.
- **Geri dönüş:** Yalnızca arayüz.

## F7 · Test ve pilot (19 Nis – 9 May)

## S22: Deneyler (a), (b), (c) ve ablasyonlar 🔒 · L · F7
- **Durum:** ⬜
- **Sorumlu:** `evaluator` · **Skill'ler:** `experiment-run`, `agreement-kappa` · **Gereksinimler:** R-EVL-01, R-EVL-04, R-GAP-02 · **Bağımlılık:** S12, S16, S18
- **Amaç:** Tezin ana sonuçları.
- **Girdi:** Altın küme (manifest doğrulanmış); [.claude/skills/experiment-run/references/experiments.md](../.claude/skills/experiment-run/references/experiments.md).
- **Görevler:**
  - T1 ⬜ Deney (a): taban çizgisi ile BERT.
  - T2 ⬜ Deney (b): RAG'li, RAG'siz, yer tutuculu.
  - T3 ⬜ Deney (c): doğrulama açık/kapalı.
  - T4 ⬜ Gruplu bootstrap güven aralıkları.
- **Kabul:** Her sayı bir `run_id`'ye bağlı; güven aralıkları var.
- **Doğrulama:** `python tools/gold_manifest.py verify`; `run_record.py validate`.
- **Geri dönüş:** Sonuçlar koşulara bağlı; yeniden koşulabilir.

## S23: Uzman değerlendirmesi (Likert) ve iddia etiketlemesi · M · F7
- **Durum:** ⬜
- **Sorumlu:** `evaluator` · **Skill'ler:** `experiment-run`, `agreement-kappa` · **Gereksinimler:** R-EVL-03 · **Bağımlılık:** S22
- **Amaç:** Halüsinasyonun iddia düzeyinde ölçülmesi.
- **Girdi:** Taslak örneklemi.
- **Görevler:**
  - T1 ✋ U-13: Uzman katılımcıların belirlenmesi.
  - T2 ⬜ Örneklem, Likert formu, iddia etiketleri; κ.
- **Kabul:** Örneklem büyüklüğü ve uzman sayısı yazılı; desteksiz ve çelişen oranları ayrı.
- **Doğrulama:** `python tools/kappa.py <A.csv> <B.csv>`.
- **Geri dönüş:** —

## F8 · Tez ve sunum (10 – 31 May)

## S24: Tez tabloları ve figürleri koşu kayıtlarından · M · F8
- **Durum:** ⬜
- **Sorumlu:** `evaluator` · **Skill'ler:** `experiment-run` · **Gereksinimler:** R-REP-01 · **Bağımlılık:** S22, S23
- **Amaç:** Tezdeki her sayının bir koşuya bağlanması.
- **Girdi:** `runs/`, `reports/experiments/`.
- **Görevler:**
  - T1 ⬜ Tablo ve figürleri üreten betikler.
  - T2 ⬜ Elle yazılmış sayı denetimi.
- **Kabul:** Elle yazılmış sayı yok; her tablo bir betikle yeniden üretilebilir.
- **Doğrulama:** Betiklerin yeniden koşulması ve `git diff --exit-code` ile aynı çıktı.
- **Geri dönüş:** —
