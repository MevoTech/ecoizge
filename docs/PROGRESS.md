# İlerleme Takibi (tek kaynak)

**Kurallar:**
- Bir aşama ya da görev yalnızca **kanıtla** ✅ olur: koşulan komut, kısa sonuç özeti, varsa çıktı yolu. "Geçmesi beklenir" ✅ değildir.
- Bu dosyayı `/start-phase` ve `/phase-gate` günceller ([AI_WORKFLOW.md](AI_WORKFLOW.md) §4). Elle düzenlemede de aynı biçim kullanılır.
- Plan [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)'dedir. §1'deki durum, plandaki "Durum" satırıyla aynı olmak zorundadır (`tools/check_consistency.py` denetler).

**Durum simgeleri:** ⬜ Başlamadı · 🟨 Sürüyor · ✅ Tamamlandı (kanıtlı) · ✅ (✋ hariç) Kullanıcı eylemi bekleyenler dışında tamamlandı · ⛔ Engelli (neden yazılır) · ✋ Kullanıcı eylemi bekliyor

**Çalışma modu:** Yarı otonom ([../AGENTS.md](../AGENTS.md) §6). Ajan kararlarını §6'ya yazar ve ilerler; `.claude/rules/security.md` "İnsan onayı" listesinde durur.

## 1. Aşama durumu

S01–S24 aşama protokolünden önce `main` dalında yürüdü; dal ve etiket düzeni 2026-10-23'ten itibaren uygulanır.

| Aşama | Ad | Durum | Dal | Etiket | Başlangıç | Bitiş | Kanıt bölümü |
|---|---|---|---|---|---|---|---|
| S01 | Ajan, skill, kural ve kanca altyapısı | ✅ (✋ hariç) · U-08 | main (protokol öncesi) | s01-done | 2026-10-22 | 2026-10-23 | §4 S01 |
| S02 | Katalog v1 🔒 | ⬜ |  |  |  |  |  |
| S03 | Rapor derlemi ve tarama tablosu | 🟨 | main (protokol öncesi) |  | 2026-10-22 |  | §4 S03 |
| S04 | PDF çıkarım hattı v0 ve kalite kümesi | 🟨 | main (protokol öncesi) |  | 2026-10-22 |  | §4 S04 |
| S05 | Pilot etiketleme, κ, kılavuz v1 | 🟨 | main (protokol öncesi) |  | 2026-10-23 |  | §4 S05 |
| S06 | REQUIREMENTS, DATA_MODEL, API_SPEC v1 🔒 | ⬜ |  |  |  |  |  |
| S07 | Onay arayüzü v1 ve toplu ön etiketleme | 🟨 | main (protokol öncesi) |  | 2026-10-22 |  | §4 S07 |
| S08 | Yöntem kararları 🔒 | 🟨 | main (protokol öncesi) |  | 2026-10-22 |  | §4 S08 |
| S09 | Docker Compose, PostgreSQL + pgvector, Alembic | ⬜ |  |  |  |  |  |
| S10 | report-service iskeleti | ⬜ |  |  |  |  |  |
| S11 | Ortak JSON sözleşmesi 🔒 | 🟨 | main (protokol öncesi) |  | 2026-10-22 |  | §4 S11 |
| S12 | Altın test kümesi 🔒 | ⬜ |  |  |  |  |  |
| S13 | Embedding modeli seçimi | ⬜ |  |  |  |  |  |
| S14 | TF-IDF + LR taban çizgisi | 🟨 | main (protokol öncesi) |  | 2026-10-22 |  | §4 S14 |
| S15 | Türkçe sayı normalleştirici ve kip denetimi | ✅ | main (protokol öncesi) | s15-done | 2026-10-22 | 2026-10-22 | §4 S15 |
| S16 | BERTurk ince ayar | ⬜ |  |  |  |  |  |
| S17 | LLM, RAG, yer tutuculu üretim 🔒 | 🟨 | main (protokol öncesi) |  | 2026-10-22 |  | §4 S17 |
| S18 | Doğrulama katmanı entegrasyonu 🔒 | ⬜ |  |  |  |  |  |
| S19 | Maskeleme değerlendirme kümesi | ⬜ |  |  |  |  |  |
| S20 | Tahmin JSON'unun taslağa bağlanması | ⬜ |  |  |  |  |  |
| S21 | Uçtan uca demo ve dışa aktarım | ⬜ |  |  |  |  |  |
| S22 | Deneyler (a), (b), (c) 🔒 | ⬜ |  |  |  |  |  |
| S23 | Uzman değerlendirmesi | ⬜ |  |  |  |  |  |
| S24 | Tez tabloları ve figürleri | ⬜ |  |  |  |  |  |
| S25 | Web arayüzü iskeleti ve veri giriş formları | ⬜ |  |  |  |  |  |
| S26 | Boşluk matrisi ve taslak editörü | ⬜ |  |  |  |  |  |
| S27 | Panel sayfası | ⬜ |  |  |  |  |  |
| S28 | Tablo ve grafik çıkarımı | 🟨 | asama/S28-tablo-grafik |  | 2026-10-23 |  | §4 S28 |

## 2. Kararlar ve kullanıcı eylemleri

Ayrıntılar [DECISIONS.md](DECISIONS.md)'de. Kabul edilenler: ADR-001…ADR-006. Açık olanlar:

| D | Durum | Engellediği | Gereken |
|---|---|---|---|
| D-01…D-06 | Açık (ADR-007…012 önerildi) | S02, S14, S16, S17, S19, S05.T7 | ✋ U-05 |
| D-07 | Açık | S04 kapanışı | S04.T6 ölçümü, ardından ADR |
| D-08 | Kapandı (2026-10-23): `data/labels/blind/**` korumalı | — | — |

### 2.1 Kullanıcı eylemleri listesi ✋

| # | Eylem | Ne zaman | Ayrıntı |
|---|---|---|---|
| U-01 | ✅ 2026-10-23, ajan yaptı (kullanıcının "ne gerekiyorsa kur" izniyle): Anaconda ortamı `ecoizge`, depo `C:\Users\mevog\Documents\ecoizge` | — | `tools/windows/kurulum.bat`; §4 |
| U-02 | ✅ açılış 2026-10-23 ajan tarafından doğrulandı; kullanıcı `tools\windows\arayuz.bat` ile açar | — | Kılavuz §2 |
| U-03 | Çıkarım kontrolü: 4 rapor × 5 sayfa = 20 sayfa | S04.T4 | Kılavuz §3 |
| U-04 | Kör etiketleme: 50 paragraf | S05.T3 | Kılavuz §4 |
| U-05 | D-01…D-06 kararları (ADR-007…012): kabul, değişiklik ya da ret | S08.T2 | [DECISIONS.md](DECISIONS.md) |
| U-06 | ZemCeng'i GitHub deposuna ortak çalışan olarak ekle | S06.T4 | GitHub → Settings → Collaborators |
| U-07 | Zemzem'in ortak şema ve sözleşme PR onayı | S06.T5, S11.T3 | security.md "İnsan onayı" 4 |
| U-08 | Claude Code oturumunda 6 canlı yönlendirme senaryosu | S01.T6 | `docs/analysis/00_ANALIZ_RAPORU.md` §9; KL-10 |
| U-09 | Katalog v1 onayı | S02.T4 | security.md "İnsan onayı" 3 |
| U-10 | Altın kümeyi dondur: `python tools/gold_manifest.py freeze --by "Mehmet Güneş"` | S12.T3 | Yalnızca insan koşar |
| U-11 | Colab defterlerini çalıştır, `run.json`'u depoya ekle | S13.T2, S16.T2 | ADR-005 |
| U-12 | LLM seçimi ve API anahtarı (yeni harici servis) | S17.T3 | ADR-011 |
| U-13 | Uzman değerlendiricileri belirle | S23.T1 | — |
| U-14 | Docker Desktop (WSL 2) kur | S09.T1 | — |
| U-15 | Zemzem ikinci etiketleyici olarak 30–50 paragraf etiketler (D-06 kabul edilirse) | S05.T7 | ADR-012 |
| U-16 | Altın tablo kümesi: 4 rapor × 5 tablo PDF'ten elle CSV'ye (en az 2 kenarlıksız, 1 bölünen, 1 birleşik başlıklı); `altin_donustur.py` ile `data/gold/tables/`; olguların birim ve dönemini kontrol | S28.T6 | `.claude/skills/table-eval/SKILL.md` Adımlar 1 |

## 3. Riskler

| # | Risk | Etki | Azaltma | Sahip |
|---|---|---|---|---|
| R-01 | Derlemde KOBİ raporu az; çoğu büyük şirket (C-03) | VSME tarafı zayıf kalır; Geliştirme 2 §4 sorusu cevapsız | S03.T5 ölçek sınıflandırması; azsa tezde sınırlılık olarak | Ajan |
| R-02 | Tek insan etiketleyici | κ yalnızca insan–model; güvenilirlik iddiası zayıf | D-06 / U-15: Zemzem alt kümeyi etiketler | Kullanıcı |
| R-03 | Kör pilotun bozulması (öneri insana gösterilir) | κ geçersiz olur | Onay ekranı pilot bitene kadar pilot önerilerini göstermez (testli); guard okuma yasağı | Ajan |
| R-04 | F1 takvimi: 15 Kasım'a kadar U-03 ve U-04 | S05 ve sonrası kayar | Kılavuz hazır; ekranlar kısa oturumlara bölünebilir (kayıt her paragrafta) | Kullanıcı |
| R-05 | Windows ortam farkları (KL-08, KL-11) | Arayüz kullanıcıda açılmaz ya da kayıt hatası verir | U-01, U-02 erken; `OSError` yakalanıyor, kılavuzda Excel uyarısı | Kullanıcı + Ajan |
| R-06 | Kaynak sunucuların değişmesi (KGK HTML döndü, KAP yansısı) | Derlem yeniden üretilemez | SHA-256 manifest, yerel kopya, erişim tarihi | Ajan |
| R-07 | Harici LLM maliyeti ve veri sınıfı (ADR-011) | S17 gecikir | U-12 erken; yerel model seçeneği | Kullanıcı |
| R-08 | Colab GPU kotası | S13, S16 gecikir | Küçük modelle önce deneme, `run.json` ile yeniden üretilebilirlik | Kullanıcı |
| R-09 | Zemzem tarafının sözleşmeye geç uyması | S20, S27 gecikir | S11 iki taraflı sözleşme testi; örnek kayıtla geliştirme | Kullanıcı |

## 4. Kanıt günlüğü

**Biçim:**
```text
### Sxx: <ad> (yyyy-aa-gg)
- Görev Sxx.Tm: ✅/⛔ kısa açıklama
  - Komut: `…`
  - Sonuç: `… geçti, … başarısız`
- Öz-denetim (AGENTS §7): kısa cevaplar
- Ertelenen: görev → hangi aşama, neden
- Etiket: sxx-done (commit)
```

En yeni kayıt en üstte. 2026-10-23 öncesi kayıtlar eski düzende tarih başlıklıydı; içerikleri olduğu gibi korunup aşama kimlikleriyle yeniden başlıklandırıldı.

### S28: Tablo ve grafik çıkarımı: ızgara, olgu, şekil, ölçüm (2026-10-23)
Kullanıcı isteği: "tablolar ve içindeki veriler ayrışıyor mu … bu yapıyı kurduğundan emin ol … alt ajan ve skilleri geliştir … skillerin GitHub reposunu bul". Dal `asama/S28-tablo-grafik`, PR #1 (taslak, CI için).

- **Önceki durum (ölçüldü):**
  - Tablo yalnızca düz metin birimiydi.
  - Klimasan'da "Tablo N" başlıklı 34 sayfanın 13'ünde tablo bulunmuyordu.
  - Bölünen tablolar birleşmiyordu; grafiklerden hiçbir şey okunmuyordu.
- **Görev S28.T1 ✅** Şema `tablo-0.1` / `olgu-0.1` / `sekil-0.1`, ızgara değişmezi; `validate_data.py` yapısal dosyalar.
  - Komut: `python -m pytest -q tests/tools/test_validate_data.py` → geçti.
- **Görev S28.T2 ✅** `pipelines/tables.py`:
  - ızgara ve birleşik hücre; başlık rolleri; kenarlıksız sezgi; sayfalar arası birleştirme;
  - uyarılar; çerçeve kutusu ayıklama; hücre metni sözcük merkezinden.
- **Görev S28.T3 ✅** Olgular:
  - `numbers`: `hucre_degeri` (eksi, muhasebe ayracı, artı, eksik, dipnot, dönem öneki), `birim_bul`/`birimler_bul`, para birimi, önek para birimi;
  - düzeltilen eski hatalar: "ton CO₂ " çökmesi ve "CO 2 e" alt simge.
- **Görev S28.T4 ✅** `pipelines/figures.py`:
  - ortak tabanlı çubuk grupları, küresel etiket–çubuk eşlemesi, lejant rengi → seri;
  - görüntü grafikte veri yok işareti.
- **Görev S28.T5 ✅** Docling uyarlayıcısı ve `pipelines/structure.py`; iki motorla 4 rapor (`run_id` s28-kapsama-2026-10-23).
  - Rapor: [reports/experiments/s28-kapsama-2026-10-23.md](../reports/experiments/s28-kapsama-2026-10-23.md).
  - 24 çıktı dosyasının hepsi `validate_data.py` OK.
  - Kaçan "Tablo N" sayfası: PyMuPDF Klimasan 2 (s. 26, 62), Akbank 2 (s. 5, 35); Docling 0.
  - Klimasan olguları: PyMuPDF 27 (16 birimli), Docling 27 (27 birimli). Akbank Şekil 6: 9/9 değer.
  - Bu bir doğruluk ölçümü değildir (altın küme yok).
- **GriTS doğrulaması:**
  - `tools/tablo_olcum.py` Microsoft table-transformer `src/grits.py` (MIT, commit 16d124f) ile 300 rastgele ızgara çiftinde karşılaştırıldı.
  - En büyük fark 0,00e+00 (betik bulut kapsayıcıda koşuldu; başvuru kodu depoya alınmadı).
  - Kasıtlı bozma (yalnız köşegen hizalama) → test kırmızı.
- **Bağımsız inceleme:** `code-reviewer`, [audits/S28-inceleme-2026-10-23.md](audits/S28-inceleme-2026-10-23.md).
  - Bulgular: 1 kritik (yanlış birim, ×1000 hatalı değer), 12 önemli, 2 küçük. Hepsi için önce kırmızı test, sonra düzeltme.
  - Gerçek veriyle ek 5 hata bulundu ve düzeltildi:
    - çerçeve kutusu 4 raporda 180 hücreyi yutuyordu;
    - Docling 0×0 tablo;
    - birleştirme zinciri;
    - Windows yumuşak tire;
    - hücre sınırına taşan sözcük.
- **Kalite kapısı:** `python tools/check_all.py` → 6/6 GEÇTİ; CI ubuntu-latest ve windows-latest (son commit'in sonucu PR #1'de).
  - Windows'ta CI iki kez kırmızı oldu: Arial "-" karakterini U+00AD olarak kodluyor. İki düzeltme de regresyon testli.
- **Skill ve ajanlar:**
  - `table-extract`, `figure-extract` (`ml-engineer`), `table-eval` (`evaluator`);
  - yetkinlik matrisi: "Bilgisayarlı görü" etkin;
  - yönlendirme tablosuna "Tablo / grafik çıkarımı" satırı.
  - Dış skill depoları: [docs/research/tablo-grafik-cikarimi.md](research/tablo-grafik-cikarimi.md) §4. anthropics/skills `pdf` özel lisanslı olduğundan kopyalanmadı. Docling resmî skill'i (MIT) `uvx library-skills --claude` ile bağlanabilir. PaddleOCR skill'i bulut API'si istiyor, kullanılmadı.
- **Öz-denetim (AGENTS §7):**
  - Gerçek veri: 4 kamu raporu (pilot gizli verisi değil); testler sentetik.
  - Koşulamayan: altın kümeye karşı doğruluk (U-16 yok).
  - Rapor bazında bölme ve altın küme yalıtımı: bu aşamada eğitim yok; `data/gold/tables` korumalı yol, yalnızca insan yazar.
  - Türkçe: sayı ayrıştırma yalnızca `verify.numbers`'ta; TL/EUR ayrımı yapılıyor; "MİLYON" büyük harfi okunuyor.
  - Belge kaynaklı talimat: hücre metni yalnızca veri; istem yok.
  - Gizli veri: Docling yerel, belge dışarı gitmiyor.
  - İnsan onayı atlanamıyor: altın küme ve motor kararı insanda.
  - Windows: CI windows-latest'te iki gerçek fark bulundu ve düzeltildi.
  - Sonuçlar `run_id` s28-kapsama-2026-10-23'e bağlı.
- **Kalan:** S28.T6 ✋ U-16 altın tablo kümesi; T7 ölçüm ve D-09 kararı; T8 görüntü grafik denemesi (KL-14).

### S05, S07: Etiket şeması 0.1 (ADR-013), analiz ekranı ve bağımsız inceleme (2026-10-23)

- **Kullanıcı isteği ve kararı.** Kullanıcı etiketleme sisteminin yetersiz ve analiz edilemez olduğunu söyledi. Sunulan üç seçenekten "çekirdek + 4 alan + analiz"i seçti (ADR-013). Etiketleme henüz başlamamıştı; bilgisayarında kör etiket dosyası yoktu.
- **Görev S05.T2 (şema 0.1) ✅**
  - Çekirdek (paragraf × madde × düzey) ve CSV başlığı değişmedi; κ ve doğrulayıcı uyumlu.
  - Yan dosya `pilot_v0.paragraf.jsonl`: beyan türü, madde başına kanıt cümlesi (numara ve metin), belirsizlik nedeni, emin değilim, etkin süre, bölme sürümü, birim türü.
  - Sözlük `data/labels/etiket_semasi.json`'da. Kurallar ve cümle bölme tek modülde (`tools/etiket_kurallari.py`); ekran ve doğrulayıcı aynı fonksiyonu kullanır.
  - Kılavuz v0.1 §3a–3c.
- **Görev S07.T7 (4 · Analiz) ✅**
  - Çıkarım hata türleri ve rapor bazında hatasız oran.
  - Düzey, beyan türü ve belirsizlik dağılımları; çıkarım hatası "ilgisiz"den ayrı sayılıyor.
  - Etkin süre (n ve kesintili sayısıyla), rapor ve madde tabloları.
  - `;` ayraçlı CSV indirme.
  - Pilot bitince κ ve anlaşmazlık tablosu. Yüzde ve sayılar `format_tr` ile.
- **İnceleme (AK-G4).** `code-reviewer` 1 kritik, 8 önemli, 10 küçük bulgu verdi. Rapor ve durum: [audits/S05-S07-inceleme-2026-10-23-sema.md](audits/S05-S07-inceleme-2026-10-23-sema.md).
  - Her bulgu için önce kırmızı test yazıldı: 17 yeni ekran ve mantık testi, 2 doğrulayıcı testi.
  - Ö2 açık kaldı (KL-12, D-06'ya bağlı).
  - Kritik bulgu K1: körleme açıldıktan sonra kör etiket değiştirilebiliyordu. Artık model önerisi ya da κ bir kez gösterilince kilit dosyası yazılıyor (zaman, neden, SHA-256) ve kör etiketler donuyor.
- **Kasıtlı bozma (`python -B`):** dört kural tek tek devre dışı bırakıldı; her seferinde ilgili test kırmızıya döndü (4/4).
  - "neden varken emin" → 1 test.
  - "çıkarım hatasında madde" → 2 test.
  - "beyan türü zorunlu" → 2 test.
  - Körleme kilidi → 1 test.
- **Çalıştır.** Arayüz gerçek pilot verisinin bir kopyasıyla başsız açıldı ve Playwright ile görüntülendi:
  - kör etiketleme ekranında numaralı cümleler ve yeni alanlar;
  - analiz ekranında örnek kayıtlarla çubuk grafikler ve tablolar.
- **Örneklemde cümle sayısı** (bölme sürümü 2): 23 birim tek cümle, 12 birim 2, 9 birim 3, 5 birim 4, 1 birim 6.

| Komut | Sonuç |
|---|---|
| `python tools/check_all.py` | 6/6 GEÇTİ |
| `python -m pytest -q` | 290 geçti |

- **Öz-denetim:**
  - Körleme kod düzeyinde korunuyor: onay ekranı ve analiz kilitliyken öneri göstermiyor; gösterince kör etiketler donuyor.
  - İki etiketleyici aynı bilgisayardaysa kimlik doğrulama yok (KL-12).
  - Windows: iki dosyanın birlikte yazımı, artan bekleme ve `fsync` testli; gerçek Excel kilidi denenmedi (KL-08).
- **Ertelenen:**
  - Model önerisinin aynı alanları üretmesi → S05.T8.
  - Beklenen etiketleyiciler dosyası → S05.T7 (D-06).

### S04, S07: Windows kurulumu kullanıcının makinesinde, Windows'ta bulunan çıkarım hatası, D-08 (2026-10-23)

- **Kullanıcının izni:** "ne gerekiyorsa kur, full kontrol sende" (2026-10-23).
- **U-01 ✅ Kurulum.** Ajan kurulum betiğini yazdı (`tools/windows/kurulum.bat`) ve Dosya Gezgini'nden çalıştırdı. Bilgisayar denetimi yalnızca tıklamaya izin veriyor, terminale yazılamıyor.
  - Anaconda ortamı `ecoizge` (conda-forge, `--override-channels`): Python 3.11.17, git 2.56.0, poppler.
  - Depo `C:\Users\mevog\Documents\ecoizge`.
  - `pip install -r requirements-dev.txt` geçti (PyMuPDF 2.0, Streamlit, scikit-learn).
- **İlk Windows koşusu:**
  - `python tools/check_all.py` → pytest 239 geçti, **2 başarısız** (`tests/pipelines/test_extract.py`).
  - Neden: Windows'ta Arial ile üretilen test PDF'inde boşluklar U+00A0, satır sonu tiresi U+00AD olarak çıkıyor.
  - Gerçek raporlarda da görülür: Akbank 2025'te bir paragrafta U+00A0 vardı.
  - Düzeltme: `join_lines` bölünemez boşlukları boşluğa çevirir; satır sonundaki yumuşak tireyi tireleme sayar, satır içindekini siler. Önce birim testi kırmızı yazıldı.
  - Pilot birimleri yeniden çıkarıldı:
    - Derimod, Klimasan ve QUA Granite bayt bayt aynı (`cmp`).
    - Akbank'ta yalnızca `sirket-akbank-2025-p020-36` değişti; bu paragraf örneklemde değil.
    - Örneklem yeniden üretildi; SHA-256 aynı (`c180ccc1…`).
- **İkinci Windows koşusu (commit 4def89d):** `python tools/check_all.py` → 6/6 GEÇTİ, 243 test geçti (46 sn). `s01-done` etiketi kullanıcının makinesinden GitHub'a gönderildi.
- **U-02 / S07.T3 ✅** `tools/windows/arayuz.bat` ile arayüz kullanıcının makinesinde açıldı. Masaüstü uygulamasının tarayıcısıyla `http://localhost:8501` doğrulandı:
  - Hazırlık denetiminde örneklem, birimler ve PDF klasörü ✅ (ad kullanıcıya kalıyor).
  - Çıkarım kontrolünde Akbank 2025, s. 3 PDF görüntüsü çizildi.
- **CI:** kalite kapısı işine `windows-latest` eklendi (KL-08 daraltıldı).
- **D-08 ✅** `data/labels/blind/**` korumalı yollarda. Guard testi önce kırmızı (`tests/hooks`: 1 başarısız), sonra 53 geçti.
- **Öz-denetim:**
  - Gerçek ortam: kullanıcının Windows makinesi ve gerçek pilot verisi.
  - Örneklem değişmedi; körleme korunuyor.
  - Gizli veri okunmadı; kurulum yalnızca kamu deposu ve paket dizinlerine erişti.
  - Disk: C: sürücüsünde 16,4 GB boş kaldı (önce 19,9 GB).
- **Test edilemeyen:** gerçek Excel kilidi (KL-08).
- **Not:** İndirilenler klasöründe, tarayıcıdan indirilmiş eski rapor PDF'leri duruyor (152 öğe). Silme izni istenmedi.

### S01, S04, S05, S07: Plan yapısı (noor uyarlaması), inceleme düzeltmeleri, kullanım kılavuzu (2026-10-23)

- Görev S01.T5: ✅ `noor` deposundaki belge yapısı raporlama modülüne uyarlandı.
  - Yeni dosyalar: [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) (S01–S27), bu dosyanın altı bölümlü düzeni, [00_INDEX.md](00_INDEX.md), [../AGENTS.md](../AGENTS.md) (`CLAUDE.md` → `@AGENTS.md`), [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) (KL-01…KL-11), [AI_WORKFLOW.md](AI_WORKFLOW.md), DECISIONS'ta D-01…D-08 ve C-01…C-04.
  - İş akışları: `/start-phase` ve `/phase-gate` skill'leri, `.agents/workflows/` yönlendiricileri, [audits/README.md](audits/README.md).
  - Ayrı `tasks/` dosyaları kaldırıldı (C-04); içerikleri plana taşındı. Geliştirme 2'deki web arayüzü için S25–S27 eklendi (C-01).
  - Denetleyiciye eklenen kontroller:
    - plan alanları;
    - aşama durumu ↔ görev simgeleri, plan ↔ PROGRESS §1;
    - ✋ görevde U-xx;
    - U, KL, D ve C atıflarının tanımlı olması;
    - gereksinim kapsaması;
    - ✅ aşamanın §4 kaydı, 🔒 ✅ aşamanın denetim raporu;
    - `CLAUDE.md`'nin `AGENTS.md`'yi içe aktarması.
  - Komut: `python -m pytest -q tests/tools/test_check_consistency.py` → 12 geçti.
  - Kasıtlı bozma: beş yeni kuralın her biri tek tek devre dışı bırakıldı (`python -B`); her seferinde ilgili test kırmızıya döndü (5/5), geri alınca yeşil.
- İnceleme (AK-G4): `code-reviewer`, commit 7b4ecaf.
  - Bulgular: 1 kritik, 6 önemli, 12 küçük. Rapor ve düzeltme durumu: [audits/S04-S05-S07-inceleme-2026-10-23.md](audits/S04-S05-S07-inceleme-2026-10-23.md).
  - 17 bulgu düzeltildi; her biri için önce kırmızı test yazıldı (`test_kor_qa.py`'de 16 test, `test_skill_scripts.py`'de 3 test).
  - Bulgu 8 (D-08) de kullanıcının genel onayıyla kapandı: `data/labels/blind/**` korumalı yollarda (guard testi önce kırmızı). Bulgu 18 KL-05 olarak kaydedildi.
  - En önemli düzeltme: kör etiketleme sürerken onay ekranı pilot paragraflarının önerilerini göstermiyor (R-03).
- İnceleme sırasında bulunan: pilot örneklemi, rapor dosyalarının komut satırındaki sırasına bağlıydı. Yinelenen metinden hangi kopyanın kaldığı sıraya göre değişiyordu; 6 paragraf farklı çıkıyordu.
  - Düzeltme: birimler `paragraf_id`'ye göre sıralanıyor. Önce kırmızı test yazıldı.
  - Örneklem, etiketleme başlamadan `--force` ile yeniden üretildi:
    - Komut: `python .claude/skills/label-propose/scripts/sample_pilot.py data/labels/pilot/birimler/*.jsonl --catalog data/catalog/catalog_v0.csv --aday 30 --rastgele 20 --seed 43 --out data/labels/pilot/orneklem.jsonl --hints data/labels/proposals/pilot_ipuclari.json --force`
    - Sonuç: 50 paragraf (30 aday, 20 rastgele), havuz 1.340.
    - Rapor dağılımı: Klimasan 14, QUA Granite 14, Akbank 13, Derimod 9.
    - Tür: 45 paragraf, 5 tablo. Uzunluk: ortalama 329 karakter, aralık 108–962.
    - SHA-256 `c180ccc1ae51e52d345e54542edd724cb61024861a498755f80de275a4d4283f`.
    - Dosyalar ters sırayla verildiğinde aynı bayt dizisi üretildi (`cmp`).
- Kullanım kılavuzu: [kullanim/ELLE_KONTROL_VE_PILOT.md](kullanim/ELLE_KONTROL_VE_PILOT.md) (U-01…U-04).
  - Kullanıcının makinesinde denetlendi: Anaconda kurulu.
  - PDF'ler `Documents\ecoizge-raporlar\sirket` altında ve ekranın aradığı adlarla duruyor (`ecoizge__sirket-akbank-2025.pdf` vb.).
- Çalıştır: arayüz gerçek pilot verisiyle başsız açıldı (`streamlit run services/review-ui/app.py --server.headless true`) ve Playwright ile görüntü alındı.
  - Başlangıç: 0 / 20 sayfa, 0 / 50 paragraf, "pilot sürüyor".
  - Kör etiketleme: ilk paragraf, seçili düzey yok.
  - Çıkarım kontrolü: Akbank için sayfalar manifestteki 1–N aralığından seçildi (s. 3, 10, 19, 30, 45).
  - PDF görüntüsü bulut çalışma alanında denenemedi: Akbank 2025 PDF'i burada yok, yalnızca kullanıcının makinesinde.

| Komut | Sonuç |
|---|---|
| `python tools/check_all.py` | 6/6 GEÇTİ |
| `python -m pytest -q` | 241 geçti |
| `python -m pytest -q services/review-ui/tests` | 39 geçti |
| `python tools/check_consistency.py` | 2135 kontrol, 0 hata |

- Öz-denetim (AGENTS §7):
  - Gerçek veri: örneklem ve ekranlar gerçek pilot birimleriyle denendi. Kilit testi, Windows'ta değil, taklitle yapıldı.
  - Bölme ve altın küme bu işte etkilenmedi.
  - Türkçe harf: arama artık `tr_kucuk` kullanıyor (testli).
  - Gizli veri ve talimat: yeni kod `data/raw/pilot` ya da `.env` okumuyor.
  - Körleme: onay ekranından atlama kapatıldı (testli). Korumalı yol eksikliği D-08'de.
  - Windows: kilitli dosya ve BOM ele alındı; gerçek Windows denemesi U-02'de (KL-08).
- Ertelenen: D-08 (kullanıcı onayı); S01.T6 → U-08.
- Etiket: `s01-done` (commit 743e541). Etiket yalnızca yerelde: bulut çalışma alanının vekili etiket göndermeye izin vermiyor; kullanıcının makinesinden `git tag s01-done 743e541 && git push origin s01-done` ile gönderilir.

### S03: Rapor derlemi, ağ izniyle indirme ve aktarım (2026-10-23)

Komut: `python tools/rapor_derlemi.py indir --hedef /home/claude/derlem --manifest …/KAYNAKLAR.csv --buyuk` (container, 4 geçiş). Ağ iznini kullanıcı verdi.

**Sonuç (container):** 418/424 `dogrulandi`.
- Dil: `tr` 414, `belirsiz` 3, `en` 1.
  - `en`: Arçelik 2022.
  - `belirsiz`: Kardemir 2025 (ABBYY ile taranmış), QNB Yatırım 2025, Bereket Sigorta 2024.
- Kalan 2 `hata`, ikisi de boyut farkı: Pınar Süt 2024 ve TKYB 2024.
- Manifest repoda: `data/raw/public/KAYNAKLAR.csv`.

**Kullanıcının makinesi:** 195 rapor `dogrulandi`, 665 MB (`yerlestir` ile yeniden doğrulandı). Aktarım hızı düşük: 7 dosyalık bir grup (yaklaşık 28 MB) zaman aşımına düştü. Kalanın nasıl aktarılacağını kullanıcı seçecek.

**Testlerin ve denemenin bulduğu sorunlar** (her biri için önce kırmızı test yazıldı):
1. **KAP eki ve bazı KGK PDF'lerinin başında 27 baytlık Java serileştirme öneki var** (`ac ed 00 05 …`). İmza artık ilk 1024 baytta aranıyor; PDF okuyucular da böyle arıyor.
2. **Vekil üzerinden büyük dosyalar 192 baytın katları kadar eksik geliyor** (Tüpraş 2024, ENKA 2024 vb.). Boyut denetimi yakaladı. Dosya artık önce `.part` olarak doğrulanıyor, yalnızca sağlam olanı kalıcı ada taşınıyor. Silme izni gerekmiyor.
3. **KGK dosya adlarının bir kısmı ayrışık Unicode (NFD) ya da karışık biçimde.** NFC ile kodlanan adres `302 → Error404` dönüyor. 8 adres sayfadaki ham `href`'ten düzeltildi.
4. **YÖKAK sunucusu sertifika zincirini eksik gönderiyor** (yalnızca yaprak sertifika). Eksik Sectigo DV R36 ara sertifikası crt.sh'den alındı ve sistemdeki R46 köküyle doğrulandı (`openssl verify: OK`). TLS doğrulaması açık kaldı.
5. **Önceki koşudan kalan hata notu, başarılı doğrulamadan sonra da kalıyordu.** Hata notu artık kaynak notundan ayrı tutuluyor (`HATA:` öneki) ve başarıda temizleniyor.
6. **Tekrar tekrar düşen büyük bir dosya kuyruğu tıkıyordu.** Artık önce hiç denenmemiş satırlar işleniyor.

| Komut | Sonuç |
|---|---|
| `python tools/check_all.py` | 6/6 GEÇTİ · 194 test geçti |

**Kullanıcının makinesine aktarım tamamlandı (öncelik kullanıcıdan: TSRS raporları).**
- Komut: `rapor_derlemi.py yerlestir` (yerinde yeniden doğrulama).
- Sonuç: 387 rapor `dogrulandi`, 1,3 GB.
  - TSRS (2024–2025 şirket raporları + KAP ekleri): 161/161.
  - KİDR 205/205, Borsa İstanbul 10/10.
  - TSRS öncesi şirket raporları (2022–2023): 11/48. Kalan 37 yalnızca bulutta, istenirse aktarılır.
- Yöntem notu:
  - Tek dosyalık paralel aktarım çağrıları, toplu çağrılardan çok daha hızlı.
  - 30 MB üstü dosyalar 20 MB'lık parçalarla aktarıldı ve cihazda birleştirildi: Tüpraş 2025 (3 parça), TKYB 2024 (10 parça).
  - Birleştirilen her dosyanın SHA-256'sı container'daki doğrulanmış dosyayla aynı.
- Cihazda kalanlar:
  - 18 boşaltılmış `.part` dosyası ve `_araclar/parca/` altında 13 boş parça. Silme izni olmadığı için silinmedi.
  - İndirilenler'deki geçici tarayıcı dosyaları temizlenmiş: geriye yalnızca kullanıcının kendi `.tmp` dosyası kaldı.

### S03, S04: Rapor derlemi ve ilk gerçek çıkarım (2026-10-22)

**Kaynak listesi.** `data/raw/public/KAYNAKLAR.csv`, 424 satır. Erişim tarihi: 2026-10-22.

| Kategori | Kaynak | Satır |
|---|---|---|
| `sirket` | KGK "Yayımlanan Raporlar" (2025: 45, 2024: 105, 2023: 7, 2022: 41) | 198 |
| `kap` | KAP ekleri, fintables yansısı (Batıçim, Kalekim, Gersan, Odaş, İsdemir, Şişecam, Arçelik, Çimsa, Petkim, TSKB, Katılımevim; 2025) | 11 |
| `bist` | Borsa İstanbul rehberleri, faaliyet ve sürdürülebilirlik raporları | 10 |
| `kidr` | YÖKAK `mis.yokak.gov.tr` 2025 KİDR'leri (GİBTÜ dahil; yurt dışı 2 İngilizce rapor dışarıda) | 205 |

Her URL tarayıcıdan HEAD isteğiyle denetlendi: 424/424 HTTP 200.

**İndirme ve doğrulama.**
- Komut: `python3 _araclar/rapor_derlemi.py yerlestir --kaynak ~/Downloads --hedef . --manifest KAYNAKLAR.csv` (kullanıcının makinesi, `Documents/ecoizge-raporlar`).
- Sonuç: 105 rapor `dogrulandi`. Her birinde `%PDF` imzası doğru, SHA-256 yazıldı, boyut KGK/YÖKAK başlığıyla aynı, dil tahmini `tr`.
- Dağılım: `sirket` 17, `bist` 8, `kidr` 80. Toplam 9.425 sayfa, 169 MB.
- 319 satır `planlandi` durumunda.

**Çıkarım (S04), container, Python 3.11.**

| Rapor | Birim | Tablo | Atılan üst/alt bilgi | OCR gereken | QA işaretleri |
|---|---|---|---|---|---|
| `sirket-derimod-2025` | 240 | 15 | 0 | s. 2, 60 | bozuk_sayi 1, cok_uzun 9, tire_kalintisi 1 |
| `sirket-akbank-2025` | 856 | 30 | 84 | yok | basliksiz 1, bozuk_sayi 3, cok_uzun 15, tire_kalintisi 1, tablo_sizintisi 4 |

- Komutlar: `pipelines/extract.py` ve `qa_report.py --sayfa 20 --seed 43`.
- Türkçe harf kaybı: iki raporda 0 (ş/ı/ğ sayısı 7.593 ve 12.270).
- Elle kontrol tabloları henüz doldurulmadı.

**Testlerin ve denemenin bulduğu sorunlar:**
1. Tarayıcı panelinden toplu indirme bazı dosyalarda "Farklı kaydet" penceresi açtı ve masaüstü bağlantısı bir kez koptu. Döngüler durduruldu. Toplu indirme bu yolla yapılmayacak; S03 "Kararlar" bölümüne yazıldı.
2. KGK sunucusu bir süre sonra PDF yerine HTML döndü: 195 istekten 174'ü `PDF değil` ya da `Failed to fetch`. Doğrulayıcı bu dosyaları zaten reddeder: `dogrula` HTML hata sayfasını `hata` yapar ve bunun testi var.
3. Sayfa sonunda bölünen tablolar ayrı birim oluyor ve devam birimi başlıksız geliyor (Derimod s. 22→23, 25→26). `pdf-extract` Tuzaklar bölümüne yazıldı.
4. Test yazılırken bulundu: PyMuPDF'in varsayılan Helvetica yazı tipi ş/ı glifini taşımıyor; üretilen test PDF'inde bu harfler `·` olarak çıkıyor. Bu yalnızca test verisini etkiliyor; gerçek raporlarda kayıp yok.

**Bağımlılıklar.** PyMuPDF ve scikit-learn kullanıcı tarafından onaylandı (2026-10-22). İkisi de `requirements-dev.txt`'ye eklendi; CI'da artık atlanmayacaklar.

**Test edilemeyenler:**
- Kalan 319 raporun indirilmesi. Tarayıcı yolu pencere açıyor. `rapor_derlemi.py indir` dört alan adına ağ izni bekliyor.
- Elle çıkarım kontrolü (QA tabloları).

### S01: Skill yeniden düzenlemesi ve ajanların ayrıntılandırılması (2026-10-22)

Yapılanlar: ayrıntı `docs/analysis/03_SKILL_YENIDEN_DUZENLEME.md`.
- 30 skill → 12 skill. Her biri betik, çözümlü örnek ve tuzak listesi içeriyor; toplam 22 destek dosyası.
- 18 skill kaldırıldı (genel kontrol listeleri ve etkin olmayan yer tutucular); içerikleri ilgili ajan dosyalarına taşındı.
- 12 ajan dosyası yeniden yazıldı: proje bağlamı, projeye özgü bilgiler, adım adım prosedür, gerçek örnek.
- Yeni kod:
  - `pipelines/extract.py` (PDF çıkarımı);
  - `report_service/nlp/coverage.py` (unsur kapsama);
  - 10 skill betiği (örneklem, öneri dönüştürücü, onay durumu, katalog farkı, taslak denetimi, istem kurucu, taban çizgisi, retrieval metrikleri, gruplu bootstrap, run.json) ve çıkarım QA betiği;
  - Colab şablonu.
- Denetleyiciye yeni kurallar:
  - skill bölümleri (Adımlar, Tuzaklar, Örnek, Kontrol listesi);
  - skill içi dosya varlığı;
  - her betiğin testi;
  - katalog kimliği atıfları;
  - ajan "Projeye özgü bilgiler" ve "Örnek" bölümleri.

| Komut | Sonuç |
|---|---|
| `python tools/check_all.py` (3.13, PyMuPDF + scikit-learn kurulu) | 6/6 GEÇTİ · 173 test geçti |
| `python tools/check_all.py` (temiz 3.11, yalnızca `requirements-dev.txt`, CI ile aynı) | 6/6 GEÇTİ · 165 geçti, 3 atlandı (PyMuPDF ve scikit-learn yok) |
| ├ `tests/hooks` · `tests/tools` · `tests/contracts` | 50 · 22 · 8 geçti |
| ├ `tests/pipelines` · `tests/skills` | 6 · 23 geçti |
| └ `services/report-service/tests` · `services/review-ui/tests` | 57 · 7 geçti |
| `python tools/check_consistency.py` | 1785 kontrol, 0 hata |
| GitHub Actions run 39706249760 (commit 56a6deb) | `kalite-kapisi`: success · `gizli-anahtar-taramasi`: success |

**Testlerin bulduğu gerçek hatalar:**
1. PyMuPDF `table.extract()` Türkçe binlik ayracını bozuyor ("12.450" → "12 450 ."). Çözüm: hücre metni hücre alanından okunuyor.
2. Taban çizgisinde öznitelikler ölçeklenmediği için log uzunluk benzerliği bastırıyordu; uzun bir paragrafın bütün madde çiftleri "karşılandı" çıkıyordu. F1 0,67'den 1,0'a çıktı (sentetik veri). Çözüm: `StandardScaler`.
3. Kardeş alt maddeler (`TSRS2-YON-06a` ile `TSRS2-YON-06a-iii`) benzerlik tabanlı modelle ayırt edilemiyor. Bu bir hata değil, taban çizgisinin bilinen sınırı; `gap-baseline` skill'inin "Tuzaklar" bölümüne yazıldı.
4. İstem kurucu madde alanlarını temizlemiyordu (`security-auditor` örneği yazılırken bulundu). Çözüm ve regresyon testi eklendi.

**Kasıtlı bozma (mutasyon) denemesi:**
- Yeni kodda 12 bozmanın 12'si yakalandı.
- İlk turda 3 bozma kaçmıştı (örneklem, öneri dönüştürücü, istem temizleme); testler güçlendirildi, tekrar denendi.
- Denetleyici kurallarının 3'ü de yakalandı: testi olmayan betik, eksik Tuzaklar bölümü, eksik Örnek bölümü.
- Not: Aynı uzunlukta bir değişiklik aynı saniyede geri alınınca Python eski `.pyc` önbelleğini kullandı ve yanlış bir kırmızı sonuç verdi. Deneme `python -B` ile tekrarlandı; tuzak `test-engineer` dosyasına yazıldı.

**Test edilemeyenler:**
- PyMuPDF ve scikit-learn testleri CI'da atlanıyor: bağımlılıklar kullanıcı onayı bekliyor (`requirements-train.txt`).
- Gerçek rapor PDF'i ile çıkarım (S04).
- Canlı ajan yönlendirmesi (S01).

### S01, S11, S15: Ajan sistemi v1 ve ilk çalışan modüller (2026-10-22)

Yapılanlar: `docs/analysis/01_DENETIM_RAPORU.md` (12 çelişki, 8 eksik). Ayrıca:
- 1 ana + 11 alt ajan, 30 skill, 6 kural dosyası;
- guard ve biçimlendirme kancaları;
- 24 görev, 34 gereksinim;
- yer tutuculu üretim (ADR-004), Türkçe sayı ve kip denetimi;
- onay arayüzü, sözleşme şeması, araçlar ve CI.

Ortamlar: (1) Python 3.13; (2) temiz Python 3.11 sanal ortamı + yalnızca `requirements-dev.txt` (CI ile aynı sürüm).

| Komut | Sonuç |
|---|---|
| `python tools/check_all.py` (3.13) | 6/6 adım GEÇTİ |
| `python tools/check_all.py` (3.11, temiz kurulum) | 6/6 adım GEÇTİ |
| `python -m pytest -q` | 127 geçti, 0 başarısız |
| ├ `tests/hooks` | 50 geçti |
| ├ `tests/tools` | 22 geçti |
| ├ `tests/contracts` | 8 geçti |
| ├ `services/report-service/tests` | 40 geçti |
| └ `services/review-ui/tests` (AppTest dahil) | 7 geçti |
| `python tools/check_consistency.py` | 1760 kontrol, 0 hata |
| `python tools/validate_data.py` | katalog_v0 (93 madde) ve şablon: 0 hata |
| `python tools/gold_manifest.py verify` | Altın küme henüz yok (beklenen) |
| GitHub Actions run 39697479060 (commit 8757246) | `kalite-kapisi`: success · `gizli-anahtar-taramasi`: success |

**Mutasyon denemesi.** Kod testlerden önce yazıldığı için testlerin hata yakalayabildiği ayrıca sınandı: kodda kasıtlı hata yapıldı, ilgili testler koşuldu, kod geri alındı. 9 mutasyonun 9'u yakalandı.

| Bozulan yer | Sonuç |
|---|---|
| guard korumalı yol kontrolü | 5 test kırmızı |
| guard yazma alanı kontrolü | 6 test kırmızı |
| serbest metin sayı kontrolü | 1 test kırmızı |
| yer tutucu tür kontrolü | 1 test kırmızı |
| Türkçe ayraç ayrıştırma | 1 test kırmızı |
| κ karesel ağırlık | 1 test kırmızı |
| manifest değişiklik tespiti | 1 test kırmızı |
| onay kaynak etiketi | 1 test kırmızı |
| yinelenen kimlik tespiti | 1 test kırmızı |

Geri alma sonrası: 121/121 geçti. Tutarlılık testleri bu denemeden sonra eklendi.

**Denetleyicinin bulduğu gerçek hata.** İlk koşuda 42 ajan ve skill önbilgisinden 18'i geçersiz YAML idi. Açıklamalardaki `: ` yüzünden Claude Code bu dosyaları okuyamazdı. Önbilgiler güvenli biçimde yeniden yazıldı; denetleyici artık YAML hatasını raporluyor.

**Test edilemeyenler:**
- Claude Code içinde canlı ajan yönlendirmesi ve guard'ın canlı davranışı (S01, 6 senaryo, kullanıcının makinesinde).
- `docker compose`: S09'a kadar kurulum yok.
- Onay arayüzünün gerçek kullanıcıyla denenmesi (S07).

## 5. Ertelenenler

| Kaynak görev | Ne | Hedef aşama | Neden |
|---|---|---|---|
| S03.T3 | TSRS öncesi 37 şirket raporunun kullanıcının makinesine aktarımı | İstenirse | Öncelik TSRS raporlarıydı (KL-06) |
| S03.T3 | Kullanıcının makinesindeki 18 boş `.part` dosyası ve `_araclar/parca/` | U-01 sırasında kullanıcı siler | Bu klasörde silme izni yok |
| S02 | GRI 302/305 maddeleri | İkinci aşama (D-04) | MVP kapsamı |
| — | ESRS | Gelecek çalışma (D-04) | MVP kapsamı |
| S28.T2 | Olguların (`facts.jsonl`, `olgu_metni`) retrieval birimi olarak dizine girmesi | S13 | Embedding modeli seçilmeden dizin kurulmaz |
| S28.T3 | Taslak sayısının olguya bağlanması (yer tutucu doldurma ve `verify.match` kaynağı olarak olgu) | S18 | Doğrulama katmanı entegrasyonu orada |
| S28.T6 | Onay arayüzünde "Tablo kontrolü" ekranı (ızgarayı PDF yanında gösterme, düzeltme) | S07 sonrası, ihtiyaç olursa | Altın küme şimdilik CSV ile; ekran insan yükünü azaltırsa açılır |
| S28.T2 | `paragraphs.jsonl` tablo birimlerinin yapısal tablodan yeniden üretilmesi | Kılavuz v1 turu (S05 sonrası) | Etiket kimlikleri bağlı; kimlik eşlemesi gerekir (KL-02) |

## 6. Otonom kararlar

Ajanın kullanıcıya sormadan verdiği kararlar. Kullanıcı bu tabloyu okuyarak herhangi birini geri çevirebilir.

| Tarih | Aşama/görev | Karar | Gerekçe | Kayıt |
|---|---|---|---|---|
| 2026-10-22 | S03.T1 | Derlem dört kategoriye ayrıldı: `sirket`, `kap`, `bist`, `kidr` | Kullanıcının istediği kaynak türleri; ayrı ayrı sayılabilsin | §4 S03, S04 |
| 2026-10-23 | S03.T3 | YÖKAK'ın eksik gönderdiği Sectigo DV R36 ara sertifikası pakete eklendi; TLS doğrulaması açık kaldı | Sistem R46 köküyle `openssl verify: OK`; doğrulamayı kapatmak yasak | §4 S03 |
| 2026-10-23 | S03.T3 | KGK adresleri sayfadaki ham `href`'ten düzeltildi (NFD Unicode) | NFC ile kodlanan adres `302 → Error404` | §4 S03 |
| 2026-10-23 | S04.T3 | Çıkarım kontrolü rapor başına 5 sayfa (toplam 20), seed 43 | Geliştirme 2 F1: 20 sayfalık elle kontrol; `qa_report.py` ile aynı seçim | Plan S04 |
| 2026-10-23 | S05.T1 | Pilot raporları: Derimod, Akbank, Klimasan, QUA Granite 2025 | Farklı sektör ve ölçek; `tr`; TSRS dönemi | Plan S05 |
| 2026-10-23 | S05.T1 | Aday seçimi Ochiai benzerliği, 100–1.500 karakter, yinelenen metin dışarıda | Uzunluk yanlılığı ve kısa başlık yığılması ölçüldü (KL-05) | `.claude/skills/label-propose/SKILL.md` |
| 2026-10-23 | S05.T2 | `annotation-assistant` `data/labels/blind/**` okuyamaz | Kör pilotun korunması | `.claude/hooks/write_scopes.json` |
| 2026-10-23 | S05.T2 | Körleme kilidi: model önerisi ya da κ bir kez gösterilince kör etiketler donar; düzeltme kılavuz v1 turunda (`pilot_v1`). İncelemenin ikinci seçeneği (gerekçeli ayrı düzeltme dosyası) seçilmedi | Kör κ'nın garanti edilmesi; kılavuz §7 zaten yeni tur öngörüyor | ADR-013 |
| 2026-10-23 | S05.T2 | Cümle bölme: sayıdan sonraki nokta bölmez, yalnızca 4 haneli yıl bölünür; kanıt metniyle saklanır ve metinden yeniden eşlenir | "11. Kalkınma Planı", "Tablo 1." gibi yanlış bölmeler daha zararlı | ADR-013 |
| 2026-10-23 | S07.T7 | 10 dakikayı aşan paragraf süresi "kesintili" sayılır, toplam ve medyana girmez | Ara verme etiketleme maliyetini şişirmesin | ADR-013 |
| 2026-10-23 | S01.T5 | `noor` belge yapısı uyarlandı; `tasks/` kaldırıldı, plan tek dosyada | Kullanıcı isteği; tek kaynak ilkesi | C-04 |
| 2026-10-23 | S01.T5 | Geliştirme 2'deki web arayüzü için S25–S27 eklendi | Plan ile kaynak belge çelişkisi | C-01 |
| 2026-10-23 | S28 | Tablo ve grafik işi yeni aşama S28 olarak açıldı (S04'e eklenmedi) | S04 elle kontrol bekliyor (U-03); tablo yapısı ayrı gereksinimler (R-TAB-01…05) ve ayrı ölçüm ister | Plan S28 |
| 2026-10-23 | S28.T1 | Kayıt biçimi motordan bağımsız, hücre alanları docling-core `TableCell` anlamında; `paragraphs.jsonl` değişmedi | Motor değişince şema değişmesin; pilot örneklemi ve kör etiket kimlikleri korunsun | ADR-014 |
| 2026-10-23 | S28.T3 | `verify.numbers`'a para birimi (TL, EUR, USD) eklendi; farklı birimler eşlenmez, kur çevrimi yok | Finansal etki tabloları TL/EUR; birimsiz kalırsa "805.299 TL" ile "805.299 ton" ayırt edilemez | ADR-014 |
| 2026-10-23 | S28.T5 | Docling isteğe bağlı ikinci motor (`requirements-extract.txt`), CI'da kurulmaz; varsayılan PyMuPDF; karar ölçümle (D-09) | Torch + model indirmesi ağır; ölçümsüz motor değişikliği yapılmaz | ADR-014, D-09 |
| 2026-10-23 | S28.T4 | Grafikte değer yalnızca yazılı etiketten; çubuk boyundan ve görüntüden değer üretilmez | Uydurma sonuç yasağı; yaklaşık değer ayrı işaret ve ölçüm ister | ADR-014, KL-14 |
| 2026-10-23 | S28.T6 | Altın tablo kümesi motor çıktısından kopyalanmaz, insan PDF'ten yazar; kutu koordinatı yok, eşleme içerikle | Ölçülen motoru kayırmamak; insan için kutu ölçmek pratik değil | `table-eval` |
