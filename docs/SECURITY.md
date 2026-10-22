# Güvenlik

Bağlayıcı kısa kurallar: `.claude/rules/security.md`. Bu belge tehdit modelini ve kontrollerin durumunu verir.

## Tehdit modeli

| # | Tehdit | Varlık | Kontrol | Durum | Gereksinim |
|---|---|---|---|---|---|
| T1 | Yüklenen PDF'teki metnin dil modeline talimat vermesi (prompt injection) | Boşluk kararı, taslak | Bağlam ayraçlı veri; boşluk kararı sınıflandırıcıda; injection test PDF'i | `[hedef]` S17 | R-SEC-01 |
| T2 | Başka şirketin verisinin bağlama girmesi | Şirket verisi | Retrieval tek fonksiyondan, `company_id` zorunlu; iki şirketli sızıntı testi | `[hedef]` S18 | R-RET-02 |
| T3 | Dil modelinin rakam uydurması | Taslak doğruluğu | Yer tutuculu üretim + doğrulama | `[uygulandı]` `placeholders.py` | R-GEN-03 |
| T4 | Gizli anahtar veya pilot verinin repoya, loga ya da ajana sızması | Anahtarlar, pilot veri | `.gitignore`; guard okuma ve yazma engeli; `permissions.deny`; CI'da gitleaks | `[uygulandı]` guard ve izinler · `[kısmi]` gitleaks CI'da (ilk koşu bekleniyor) | R-SEC-02 |
| T5 | Altın test kümesinin değiştirilmesi ya da geliştirmede kullanılması | Tez ölçümünün geçerliliği | SHA-256 manifest; guard (yazma tüm ajanlara, okuma `ml-engineer`'a kapalı); CI doğrulaması | `[uygulandı]` araç ve kanca · küme henüz yok | R-ETK-02 |
| T6 | Ajanın yetkisi dışında dosya değiştirmesi | Kod tabanı | Ajan bazlı yazma alanı (guard); salt-okunur denetçilerde yazma aracı yok | `[uygulandı]` · Bash'te kısmi (aşağıda) | R-AGT-01 |
| T7 | Yıkıcı git ve dosya işlemleri | Depo geçmişi | guard Bash kalıpları + `permissions.deny` + push için `ask` | `[uygulandı]` | R-SEC-02 |
| T8 | Kötü niyetli ya da çok büyük PDF yüklenmesi | Servis | Boyut ve sayfa sınırı, MIME denetimi, ayrı işçide çıkarım | `[hedef]` S10 | R-API-02 |
| T9 | Yetkisiz API erişimi | Tüm veri | JWT + şirket bazlı yetki | `[hedef]` S10 | R-SEC-04 |
| T10 | Gizli verinin harici LLM'e gönderilmesi | Pilot veri | Veri sınıfı kuralı (ADR-011) + çağrı öncesi sınıf kontrolü | `[kısmi]` kural yazılı, kod S17 | R-SEC-03 |

## Bilinen sınırlar

1. **Bash.** guard yalnızca komut metnindeki kalıpları görür. Dolaylı yazma (ör. bir Python betiğinin içinden korumalı yola yazma) yakalanmaz. Korumalı yollar için dengeleyici kontroller: manifest (CI), PR incelemesi, `git diff` denetimi.
2. **Grep.** guard, Grep'in `path` parametresini denetler. Repo kökünde yapılan bir aramada `.gitignore`'daki dosyalar (`.env`) ripgrep tarafından atlanır. Ama `data/gold/` git'te olduğu için kök aramasında görünebilir; `ml-engineer` için bu kalan bir risktir.
3. **Canlı doğrulama.** guard'ın Claude Code içindeki davranışı (özellikle ana oturumdaki `agent_type`) bu ortamda canlı test edilemedi; S01'de kullanıcının makinesinde test edilecek.
