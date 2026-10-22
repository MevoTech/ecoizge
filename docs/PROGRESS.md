# İlerleme

Yalnızca gerçekten koşulmuş komutların sonuçları yazılır. En yeni kayıt en üstte.

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
- GitHub Actions ilk koşusu: push sonrası bu kayda eklenecek.
- `docker compose`: S09'a kadar kurulum yok.
- Onay arayüzünün gerçek kullanıcıyla denenmesi (S07).
