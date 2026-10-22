---
name: systems-diagnostics
description: 'İşletim sistemi ve ağ düzeyinde teşhis için kullan: süreç, bellek, disk, dosya izinleri, port, DNS, konteyner ağı, TLS, servisler arası bağlantı sorunları.'
---

# systems-diagnostics

## Adımlar
1. Belirtiyi katmana yerleştir: uygulama / süreç / dosya sistemi / ağ / konteyner.
2. Süreç ve kaynak: `ps aux`, `free -h`, `df -h`, `ulimit -a`; konteynerde `docker stats`.
3. Ağ: `ss -ltnp` (dinleyen portlar), `curl -v http://<servis>:<port>/health`, compose içinde servis adıyla çözümleme (`docker compose exec <a> getent hosts <b>`).
4. TLS: `curl -vI https://...`; sertifika zinciri hatasında doğrulamayı kapatma, CA ayarını düzelt.
5. Bulguyu ve düzeltmeyi raporla; kalıcı düzeltme `docker-compose.yml` veya yapılandırmada.

## Kontrol listesi
- [ ] Teşhis komutları ve çıktıları raporda
- [ ] Güvenlik ayarı gevşetilmedi
