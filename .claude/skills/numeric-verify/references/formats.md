# Sayı biçimleri (`report_service.verify.numbers`)

| Yazım | Değer | Birim tabanı | Not |
|---|---|---|---|
| `12.450,5` | 12450,5 | — | '.' binlik, ',' ondalık |
| `12.450` | 12450 | — | noktadan sonra 3 hane → binlik |
| `1.234.567` | 1234567 | — | çoklu binlik |
| `1,5` | 1,5 | — | yalnız virgül → ondalık |
| `12.5` | 12,5 | — | noktadan sonra 3 hane değil → ondalık (İngilizce biçimli tablolar) |
| `1.234` | 1234 | — | **belirsiz**: İngilizce metinde 1,234 olurdu; Türkçe varsayımı |
| `1,234.5` | hata | — | İngilizce binlik + ondalık; reddedilir |
| `1,2 milyon kWh` | 1.200.000 | kWh | ölçek × birim |
| `3,4 GWh` | 3.400.000 | kWh | GWh = 10⁶ kWh |
| `12,4 ktCO2e` | 12.400 | tCO2e | kt = 10³ t |
| `1,1 MtCO2e` | 1.100.000 | tCO2e | Mt = 10⁶ t |
| `2,5 bin ton` | 2.500 | t | |
| `850 kg` | 0,85 | t | |
| `%12,5` · `yüzde 40` | 12,5 · 40 | % | yüzde ve yüzde puanı ayrımı yapılmaz; KPI adı belirtir |
| `2024` | yıl | — | ayraçsız, birimsiz, 1900–2100 |
| `CO2`, `S-03` | — | — | sözcük içindeki rakam atlanır |

Eşleme: aynı taban birimde `|n − n*| / |n*| ≤ ε` (varsayılan ε = 0,005).
