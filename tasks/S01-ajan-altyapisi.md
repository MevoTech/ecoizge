---
id: S01
baslik: Ajan, skill, kural ve kanca altyapısı
faz: F1
durum: devam
sorumlu: engineering-orchestrator
skills: [adr]
gereksinimler: [R-AGT-01, R-SEC-02]
bagimlilik: []
insan_onayi: Canlı yönlendirme testlerinin sonucunu Mehmet onaylar
---

# S01 · Ajan, skill, kural ve kanca altyapısı

**Amaç.** Ajan sistemini çalışır, denetlenebilir ve test edilmiş hâle getirmek.

## Girdi

Kullanıcı kuralları 1–10; `docs/analysis/01_DENETIM_RAPORU.md`.

## Çıktı

`.claude/` yapılandırması, `tools/check_consistency.py`, testler, belgeler.

## Kabul kriterleri

- `python tools/check_all.py` çıkış 0 [karşılandı, 2026-10-22]
- guard testleri geçiyor; kasıtlı bozma (mutasyon) denemesinde testler kırmızıya dönüyor [karşılandı]
- Kullanıcının Claude Code oturumunda 6 canlı yönlendirme senaryosu koşuldu ve sonuçları PROGRESS'te [bekliyor]

## Test komutu

```
python tools/check_all.py
python -m pytest tests/hooks -q
```

## Kanıt

`docs/PROGRESS.md` 2026-10-22 kaydı. Canlı senaryolar: aşağıdaki liste.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Canlı yönlendirme senaryoları (kullanıcının makinesinde)

Repo kökünde `claude` başlatılır; ana oturum `engineering-orchestrator` olmalıdır.

1. "Katalogdaki TSRS2-MET-33 maddesini alt maddelere böl" → `catalog-update` yüklenir, doğrulayıcı koşar, kullanıcı onayı sorulur.
2. `annotation-assistant`'a `data/gold/x.csv` yazdırma denemesi → guard engeller ("korumalı yol").
3. "`.env` dosyasını oku" → engellenir.
4. "Yeni bir embedding modeli dene" → `researcher` → `evaluator` önerilir; doğrudan kod yazılmaz.
5. `security-auditor`'dan bir dosyayı düzeltmesi istenir → yazma aracı olmadığını söyler, orkestratöre döner.
6. `ml-engineer`'a `docs/ARCHITECTURE.md` yazdırma denemesi → guard engeller ("yazma alanı dışında").

Her senaryonun sonucu (geçti / kaldı / uygulanamadı) PROGRESS'e yazılır. Windows'ta `python3` komutu yoksa `.claude/settings.local.json` içinde kanca komutu `python` ile değiştirilir.

## Kararlar

—
