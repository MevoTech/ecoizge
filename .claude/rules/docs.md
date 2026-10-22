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
- Görev dosyalarının önbilgisi (`tasks/Sxx-*.md`) `tools/check_consistency.py` tarafından denetlenir; alan adları değiştirilmez.
- `CLAUDE.md` 200 satırın altında kalır; ayrıntı belgelere taşınır.
