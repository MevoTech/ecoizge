# Skill Yeniden Düzenlemesi ve Ajanların Ayrıntılandırılması

Tarih: 2026-10-22 · Tetikleyen: kullanıcı ("skill dosyalarının çoğu gerçekten bir skill dosyasına benzemiyor"; "herkes işini detaylıca anlamalı") · Kanıtlar: [../PROGRESS.md](../PROGRESS.md)

## 1. Tespit (değişiklikten önce)

| Ölçüt | Değer |
|---|---|
| Skill sayısı | 30 |
| SKILL.md dışında dosyası olan skill | 0 |
| Çözümlü örnek içeren skill | 0 |
| Toplam satır / skill başına ortalama | 657 / 22 |
| "Etkin değil" yazan skill | 4 |

Kök nedenler:
1. Kural 2 ("ajan **veya** skill") yanlış okunup her yetkinliğe skill üretildi.
2. 30 skill tek bir şablondan tek seferde üretildi.
3. Genel kontrol listeleri (debug, code-review, perf-profile, plan-task) modelin zaten bildiği şeyleri tekrar ediyordu.

## 2. Yapılan

**Skill'ler.**
- **12 kaldı:** pdf-extract, label-propose, label-review, agreement-kappa, catalog-update, numeric-verify, rag-draft, gap-baseline, embed-eval, colab-train, experiment-run, adr.
- **Her skill'de:**
  - tetikleyicileri yazan açıklama;
  - "ne zaman / ne zaman değil";
  - tam komutlarla adımlar;
  - projede gerçekten yaşanmış tuzaklar;
  - çözümlü örnek;
  - kontrol listesi.
- **Destek dosyaları:** 22 (betik, referans, şablon).
- **18 skill kaldırıldı.** Projeye özgü içerikleri ilgili ajan dosyalarına taşındı:
  - inceleme kuralları → `code-reviewer`;
  - tehdit kontrolleri → `security-auditor`;
  - OS, ağ ve performans teşhisi → `backend-engineer`;
  - sözleşme ve şema prosedürü → `architect`;
  - planlama ve belge senkronu → `engineering-orchestrator`.

**Ajanlar.** 12 dosya yeniden yazıldı. Her alt ajanda zorunlu iki yeni bölüm var; denetleyici bunları zorluyor:
- **Projeye özgü bilgiler:** ilgili ADR'ler, dosya yolları, bu projede yaşanmış hatalar.
- **Örnek:** gerçek ya da gerçekçi bir görev ve ajanın döneceği rapor.

**Yeni çalışan kod** (hepsi testli):
- `pipelines/extract.py`;
- `services/report-service/report_service/nlp/coverage.py`;
- `.claude/skills/*/scripts/*.py` (11 betik);
- Colab şablonu.

**Denetleyici** (`tools/check_consistency.py`):
- her skill'de Adımlar, Tuzaklar, Örnek ve Kontrol listesi bölümleri;
- skill içi `scripts/`, `references/` ve `assets/` atıflarının varlığı;
- her betiğin `tests/skills` altında testi;
- belgelerdeki katalog kimliklerinin katalogda bulunması;
- ajanlarda "Projeye özgü bilgiler" ve "Örnek" bölümleri.

Yetkinlik matrisinde skill sütunu artık isteğe bağlı.

## 3. Kalan riskler

1. **Onay bekleyen bağımlılıklar.** PyMuPDF (AGPL-3.0) ve scikit-learn kullanıcı onayı bekliyor. O zamana kadar çıkarım ve taban çizgisi testleri CI'da atlanıyor; yalnızca yerelde koştu.
2. **Gerçek veri yok.** Skill betikleri sentetik veriyle doğrulandı. İlk gerçek rapor (S04) yeni tuzaklar çıkaracaktır; bunlar ilgili skill'in "Tuzaklar" bölümüne eklenmeli.
3. **Canlı ajan davranışı test edilmedi.** S01'deki canlı yönlendirme senaryoları hâlâ bekliyor.
