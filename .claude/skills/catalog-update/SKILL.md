---
name: catalog-update
description: "Gereklilik kataloğuna (TSRS 1, TSRS 2, VSME, GRI) madde eklemek, maddeyi alt unsurlara bölmek ya da güncellemek için kullan. Resmî metinden doğrulama ve kullanıcı onayı zorunludur. Tetikleyiciler: kapsam kararı (ADR-010), kappa anlaşmazlığının madde tanımından kaynaklanması, çok unsurlu maddenin bölünmesi (ADR-008)."
---

# catalog-update

Katalog bütün sistemin ortak dilidir: etiketler, boşluk analizi, RAG istemi ve arayüz aynı `madde_id`'leri kullanır. Bir madde kimliğini değiştirmek, ona bağlı bütün etiketleri yetim bırakır. Bu yüzden katalog **yalnızca yeni sürüm dosyası açarak** ve kullanıcı onayıyla değişir.

## Kurallar

- Eski sürüm dosyası silinmez ve değiştirilmez: `catalog_v0.csv` → `catalog_v1.csv`.
- Her satırın `dogrulama` alanı `resmi_metin_YYYY-AA-GG` biçiminde olur. Tarih, resmî metnin açılıp okunduğu gündür. İkincil kaynaktan (blog, danışmanlık sitesi) madde eklenmez.
- `gereklilik_ozeti` **kendi cümlenle** yazılır; resmî metinden uzun alıntı yapılmaz.
- Kimlik biçimi: `<STANDART>-<BÖLÜM>-<paragraf ref>`. Örnekler:
  - `TSRS2-MET-29a-i`: TSRS 2, Metrikler, 29(a)(i).
  - `VSME-B3-29`: VSME, B3 modülü, paragraf 29.
- Alt unsur (v1): kimliğin sonuna `-a`, `-b` … eklenir ve `ust_madde` sütunu üst kimliği gösterir. Üst madde katalogda kalır. Unsur kapsama kararı alt unsurlardan toplanır (`report_service/nlp/coverage.py`).

Sütunların ayrıntılı anlamı: `references/catalog_schema.md`.

## Adımlar

1. Resmî metni aç: KGK (TSRS) ya da EFRAG (VSME). Maddeyi paragraf numarasıyla bul.
2. `data/catalog/catalog_v<N>.csv`'yi `catalog_v<N+1>.csv` olarak kopyala ve değişiklikleri yeni dosyada yap. İlk alt unsur bölmesinde dosyanın sonuna `ust_madde` sütunu eklenir.
3. Doğrula: `python tools/validate_data.py data/catalog/catalog_v<N+1>.csv` → 0.
4. Farkı üret ve kullanıcıya **onay için** göster:
   ```
   python .claude/skills/catalog-update/scripts/diff_catalog.py data/catalog/catalog_v<N>.csv data/catalog/catalog_v<N+1>.csv
   ```
5. Silinen ya da kimliği değişen madde varsa, o maddeye bağlı etiket satırlarının sayısını raporla (`grep -c '<madde_id>' data/labels/proposals/*.csv`).
6. Onaydan sonra:
   - `CLAUDE.md` ve `.claude/rules/data.md` en yeni sürüme işaret ediyor mu, kontrol et;
   - `python tools/check_all.py` → 0.

## Tuzaklar

- **Kapsam 3 geçiş hükmü:** TSRS'nin ilk uygulama dönemlerinde Kapsam 3 açıklaması zorunlu değil (Teknik Kapsam 3; KGK kararıyla güncellenebilir). `TSRS2-MET-29a-i` satırının `not` alanında bu yazılı. Bölünmüş katalogda Kapsam 3 alt unsurunun `zorunluluk` değeri `koşullu` olmalı.
- **VSME Temel ile Kapsamlı farkı** `profil` sütunundadır. Boşluk analizi seçilen profile göre çalışır (R-KAT-02). Kapsamlı modül maddesini Temel profile koyma.
- **Aynı içerik, iki standart.** TSRS 2 ve VSME emisyon maddeleri örtüşür ama aynı değildir. Birleştirme; ayrı satır olarak tut, eşlemeyi `not` alanına yaz.
- **GRI madde numaraları doğrulanmadı** (Teknik Kapsam 11). GRI eklenecekse önce resmî GRI metni açılır.

## Örnek

`TSRS2-MET-29a-i` maddesinin bölünmesi:

| madde_id | madde_ref | baslik | zorunluluk | ust_madde |
|---|---|---|---|---|
| TSRS2-MET-29a-i | 29(a)(i) | Brüt sera gazı emisyonları | zorunlu | |
| TSRS2-MET-29a-i-a | 29(a)(i) | Kapsam 1 brüt emisyon | zorunlu | TSRS2-MET-29a-i |
| TSRS2-MET-29a-i-b | 29(a)(i) | Kapsam 2 brüt emisyon | zorunlu | TSRS2-MET-29a-i |
| TSRS2-MET-29a-i-c | 29(a)(i) | Kapsam 3 brüt emisyon | koşullu | TSRS2-MET-29a-i |

`diff_catalog.py` çıktısında bu satırlar "Eklenen" bölümünde görünür. Üst madde değişmediği için mevcut etiketler korunur.

## Kontrol listesi

- [ ] Yeni sürüm dosyası; eski dosya değişmedi
- [ ] Her yeni ya da değişen satırda `dogrulama` bugünün tarihi
- [ ] Doğrulayıcı 0, fark tablosu kullanıcıya gösterildi, onay alındı
- [ ] Yetim kalacak etiket sayısı raporlandı

## Dosyalar

- `scripts/diff_catalog.py`: sürüm farkı (onay tablosu)
- `references/catalog_schema.md`: sütun tanımları ve izin verilen değerler
