---
paths:
  - "docs/**"
  - "tasks/**"
  - "README.md"
  - "CLAUDE.md"
---

# Belge kuralları

- Durum etiketleri: `[uygulandı]` (kodu ve testi var), `[kısmi]`, `[hedef]` (tasarlandı, kod yok). Etiketsiz tasarım cümlesi yazılmaz.
- Gerçek sonuç yalnızca `docs/PROGRESS.md`'de, tarih ve komutla birlikte yazılır. Diğer belgeler sonuca PROGRESS'ten bağlantı verir, sayıyı kopyalamaz.
- Gereksinim kimlikleri `docs/REQUIREMENTS.md`'de tanımlanır; başka yerde yeni kimlik uydurulmaz.
- Kararlar `docs/DECISIONS.md`'de ADR olarak tutulur; eski ADR silinmez, "yerini aldı: ADR-xxx" diye işaretlenir.
- Plan (`docs/DEVELOPMENT_PLAN.md`) biçimi ve plan ile PROGRESS §1 durum uyumu `tools/check_consistency.py` tarafından denetlenir; alan adları (Durum, Sorumlu, Gereksinimler, Bağımlılık, Amaç, Girdi, Görevler, Kabul, Doğrulama, Geri dönüş) değiştirilmez.
- Kimlikler: aşama `Sxx`, görev `Sxx.Tm`, karar `ADR-xxx`, açık karar `D-xx`, çelişki `C-xx`, kısıt `KL-xx`, kullanıcı eylemi `U-xx`, risk `R-xx` ([docs/00_INDEX.md](../../docs/00_INDEX.md) §3).
- Kurallar `AGENTS.md`'de; `CLAUDE.md` yalnızca onu içe aktarır. İkisi de 200 satırın altında kalır.
