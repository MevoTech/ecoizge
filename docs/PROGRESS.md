# İlerleme

Yalnızca gerçekten koşulmuş komutların sonuçları yazılır. En yeni kayıt en üstte.

## 2026-10-23 · Rapor derlemi: ağ izniyle indirme

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

## 2026-10-22 (3) · Rapor derlemi (S03) ve ilk gerçek çıkarım (S04)

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

## 2026-10-22 (2) · Skill yeniden düzenlemesi ve ajanların ayrıntılandırılması

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

## 2026-10-22 · Ajan sistemi v1 ve ilk çalışan modüller

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
