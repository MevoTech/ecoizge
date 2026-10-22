# Son Rapor: Ajan Sistemi v1

Tarih: 2026-10-22 · Kapsam: kullanıcının 10 zorunlu kuralı · Kanıtlar: [../PROGRESS.md](../PROGRESS.md)

## 1. Yapılan değişiklikler

| Alan | Sonuç |
|---|---|
| Ana ajan | `.claude/agents/engineering-orchestrator.md` + `settings.json` `"agent"` (ADR-001) |
| Alt ajanlar | 11 ajan; her birinde rol, yazma alanı, girdi ve çıktı sözleşmesi, prosedür, kabul kriterleri, geri dönüş koşulu ve yasaklar |
| Skill'ler | 30: 18 genel mühendislik, 12 projeye özel; 4'ü "etkin değil" ve tetiklenme koşullu |
| Kurallar | `.claude/rules/`: orchestration, quality-gates, security (genel); python, data, docs (yol kapsamlı) |
| Zorlama | `guard.py` (ajan bazlı yazma alanı, korumalı yollar, okuma yasakları, yıkıcı Bash), `permissions.deny/ask`, iç içe ajan derinliği 1 |
| Araçlar | `validate_data`, `kappa`, `gold_manifest`, `check_consistency`, `check_all` |
| Proje kodu | Türkçe sayı ve birim normalleştirme, kip denetimi, yer tutuculu üretim (B10, ADR-004), onay arayüzü, ortak sözleşme şeması |
| Belgeler | REQUIREMENTS (34 R-*), TRACEABILITY, ARCHITECTURE, DATA_MODEL, API_SPEC, SECURITY, TEST_PLAN, DECISIONS (12 ADR), ORCHESTRATION, COMPETENCY_MATRIX, PROGRESS |
| Görevler | `tasks/S01…S24` + README dizini + şablon |
| CI | `.github/workflows/ci.yml`: kalite kapısı + gitleaks |

## 2. Çözülen çelişkiler

Ayrıntı: [01_DENETIM_RAPORU.md](01_DENETIM_RAPORU.md) §2, Ç1–Ç12. Uygulama sırasında iki çelişki daha bulunup düzeltildi:
- **YAML önbilgisi.** 42 dosyanın 18'inde geçersiz YAML vardı (`: ` içeren açıklamalar). Claude Code bu dosyaları okuyamazdı. Denetleyici bunu buldu, önbilgiler yeniden yazıldı.
- **Skill ile guard çelişkisi.** `label-review` skill'i, guard'ın engellediği bir komutu (`data/labels/reviewed` yolunu içeren) öneriyordu. Komut argümansız doğrulayıcıya çevrildi.

## 3. Kapsanan yetkinlikler

18 yetkinliğin 18'i: [../COMPETENCY_MATRIX.md](../COMPETENCY_MATRIX.md). Denetleyici her satırda ajanın ve skill'in var olduğunu ve skill'in o ajanın listesinde bulunduğunu doğruluyor.
- 9 etkin.
- 5 hazır (ilgili fazda).
- 4 etkin değil (frontend şimdilik; mobil, bilgisayarlı görü, gömülü kapsam dışı).

## 4. Test sonuçları (2026-10-22)

- `python tools/check_all.py`: 6/6 adım geçti; Python 3.13'te ve CI ile aynı temiz 3.11 ortamında.
- 127 test geçti; 1760 tutarlılık kontrolü geçti, 0 hata.
- Mutasyon denemesi: 9/9 yakalandı.
- GitHub Actions (run 39697479060): kalite kapısı ve gitleaks taraması başarılı.

## 5. Kalan riskler (doğrulanmamış, başarılı sayılmayan)

1. **Canlı ajan davranışı test edilmedi.** Yönlendirme ve guard'ın Claude Code içindeki davranışı, özellikle ana oturumda `agent_type` alanı, yalnızca belgelere ve doğrudan JSON testlerine dayanıyor. Doğrulama: S01, 6 senaryo.
2. **Bash ile alan aşımı.** Dolaylı yazma yakalanmıyor (SECURITY.md, bilinen sınır 1).
3. **Kök dizinde Grep.** `ml-engineer` altın kümeyi kök aramasında görebilir (SECURITY.md, bilinen sınır 2).
4. **Windows.** Kancalar `python3` çağırıyor; Windows'ta komut adı farklıysa `settings.local.json` ile değiştirilmeli.
5. **Kip denetimi kural tabanlı.** Karmaşık cümlelerde yanlış alarm verebilir (`verify/tense.py`, modül belgesi).
6. **ADR-007…ADR-012 önerildi durumunda.** Mehmet'in onayını bekliyor (S08).
