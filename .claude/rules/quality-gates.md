# Kalite kapıları

## Bitti tanımı (her görev)

1. Görev dosyasındaki (`tasks/Sxx-*.md`) bütün kabul kriterleri karşılandı.
2. `python tools/check_all.py` çıkış kodu 0. Çıktısı rapora eklendi.
3. Yeni davranış için test var. Test bir kez başarısız, düzeltmeden sonra başarılı koştu.
4. Kod değiştiyse `code-reviewer` incelemesi yapıldı. Güvenlik kritik bir değişiklikse `security-auditor` incelemesi de yapıldı. Kritik bulgu açık kalmadı.
5. `docs/PROGRESS.md` ve görevin `durum` alanı güncellendi. `[uygulandı]` etiketi yalnızca var olan ve test edilen öğelerde.

## Kanıt kuralları

- Kanıt, gerçekten koşulmuş komutun çıktısıdır. "Geçmesi beklenir" kanıt değildir.
- Koşulamayan kontrol "test edilemedi: <neden>" diye yazılır ve görev en fazla `KISMİ` olur.
- Model ya da deney sonucu bir `run_id`'ye bağlı değilse raporlanmaz.

## Hata prosedürü

1. Hatayı yeniden üret ve en küçük örneğe indir: tam komut, girdi, beklenen ve gerçek çıktı; değişkenleri tek tek sabitle.
2. Önce başarısız bir regresyon testi yaz, sonra düzelt.
3. Aynı yaklaşım iki kez başarısız olursa dur: orkestratör kullanıcıya bulguyu ve seçenekleri sunar.
4. Bir kontrolü geçirmek için testi, eşiği ya da doğrulayıcıyı gevşetmek yasaktır. Gevşetme yalnızca gerekçeli bir ADR ile yapılır.
5. Geri alınamayan bir adım yarıda kaldıysa ilerleme ve durum `docs/PROGRESS.md`'ye yazılır.
