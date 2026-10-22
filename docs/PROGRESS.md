# İlerleme

Yalnızca gerçekten koşulmuş komutların sonuçları yazılır. En yeni kayıt en üstte.

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
| `python tools/check_consistency.py` | 1779 kontrol, 0 hata |

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
