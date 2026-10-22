---
id: S03
baslik: Rapor derlemi ve tarama tablosu
faz: F1
durum: devam
sorumlu: researcher
skills: []
gereksinimler: [R-PDF-01]
bagimlilik: []
insan_onayi: Hangi raporların kullanılacağı
---

# S03 · Rapor derlemi ve tarama tablosu

**Amaç.** En az 10 rapor (hedef 5 KOBİ) toplamak ve Geliştirme 2 §4 tarama tablosunu doldurmak.

## Girdi

KAP, şirket siteleri; Karel 2025, Sabancı 2024.

## Çıktı

`docs/research/` altında tarama notu; PDF'ler `data/raw/public/`.

## Kabul kriterleri

- ≥10 rapor, her biri için kaynak URL ve erişim tarihi
- KOBİ raporu bulunamazsa durum açıkça yazılı (G2 §4)

## Test komutu

```
python tools/check_all.py
```

## Kanıt

Tarama notu.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

- 2026-10-22: Derlem dört kategoridir: `sirket` (KGK resmî listesi 2022–2025), `kap` (KAP ekleri), `bist` (Borsa İstanbul), `kidr` (YÖKAK 2025). Manifest `data/raw/public/KAYNAKLAR.csv`; PDF'ler git dışında, kullanıcının makinesinde `Documents/ecoizge-raporlar/`. Araç: `tools/rapor_derlemi.py`.
- 2026-10-22: Tarayıcı paneliyle toplu indirme her dosya için "Farklı kaydet" penceresi açabiliyor; toplu indirme bu yolla yapılmaz. Kalan dosyalar `rapor_derlemi.py indir` ile (ağ izni gerekir) indirilecek.
