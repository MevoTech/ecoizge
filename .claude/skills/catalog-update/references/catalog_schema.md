# Katalog şeması

Doğrulayıcı: `tools/validate_data.py`. İzin verilen değerler oradaki sabitlerle birebir aynıdır; burada değişirse orada da değişmelidir.

| Sütun | Zorunlu | İzin verilen / biçim | Anlamı |
|---|---|---|---|
| `madde_id` | evet | benzersiz; `TSRS2-MET-29a-i`, `VSME-B3-29` | Sistemdeki tek kimlik; etiketler buna bağlı |
| `standart` | evet | `TSRS 1`, `TSRS 2`, `VSME`, `GRI` | Kaynak standart |
| `bolum` | evet | serbest (ör. `Yönetişim`, `Metrikler`, `B3 Enerji ve sera gazı`) | Standarttaki bölüm |
| `madde_ref` | evet | resmî paragraf numarası (ör. `29(a)(i)`) | Resmî metinde bulmak için |
| `baslik` | evet | kısa ad | Arayüzde ve istemde görünür |
| `gereklilik_ozeti` | evet | kendi cümlemizle 1–2 cümle | Etiketleyici ve model buna göre karar verir |
| `zorunluluk` | evet | `zorunlu`, `koşullu`, `isteğe bağlı` | `koşullu`: belirli durumda gerekir (U etiketi mümkün) |
| `veri_turu` | evet | `anlatı`, `sayısal`, `tablo`, `karma`, `evet/hayır` | Sayısal maddelerde değer + birim + dönem aranır |
| `profil` | evet | `TSRS1`, `TSRS2`, `VSME-Temel`, `VSME-Kapsamlı`, `GRI` | Boşluk analizi profile göre çalışır |
| `not` | hayır | serbest | Muafiyet, açık soru, standartlar arası eşleme |
| `dogrulama` | evet | `resmi_metin_YYYY-AA-GG` | Resmî metnin okunduğu gün |
| `ust_madde` | v1'den | boş ya da aynı katalogdaki bir `madde_id` | Alt unsurun üst maddesi (ADR-008) |
