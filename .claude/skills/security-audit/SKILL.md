---
name: security-audit
description: 'Güvenlik ve gizlilik denetimi için kullan: gizli anahtar taraması, bağımlılık açıkları, dosya yükleme, prompt injection, kiracı izolasyonu, veri sınıfı akışı.'
---

# security-audit

## Girdi
Değişen dosyalar, `docs/SECURITY.md` tehdit modeli, tarama çıktıları.

## Taramalar (orkestratör koşturur, çıktıyı denetçiye verir)
- Gizli anahtar: `gitleaks detect --no-banner` (CI'da `gitleaks/gitleaks-action`)
- Bağımlılık: `pip-audit` (kuruluysa)
- Korumalı yollar: `python -m pytest tests/hooks -q`
- Injection: `python -m pytest -q -k injection` (S17'den sonra)

## Kontrol listesi
- [ ] Yüklenen belge metni prompta veri olarak ve ayraçla giriyor (R-SEC-01)
- [ ] Boşluk kararı LLM'e bırakılmamış
- [ ] Retrieval `company_id` filtresiz çağrılamıyor (R-RET-02)
- [ ] Gizli sınıf veri git'e, loga, harici API'ye gitmiyor (R-SEC-02, R-SEC-03)
- [ ] Dosya yükleme: boyut sınırı, MIME/uzantı denetimi, sayfa sınırı
- [ ] Kimlik ve rol kontrolü her uçta (F3'ten sonra)
- [ ] `audit_log` yazılıyor (R-SEC-04)

## Çıktı
Tehdit · varlık · saldırı senaryosu · önem · önerilen kontrol · bağlı R-SEC-*.
