---
name: numeric-verify
description: "Taslaktaki sayıları ve gerçekleşmiş/tahmin kipini denetlemek, yer tutucuları kaynak kayıtlarla doldurmak ve Türkçe sayı biçimi hatalarını teşhis etmek için kullan. Tetikleyiciler: RAG taslağı üretildikten sonra, sayısal tutarlılık (NC) ölçülürken, yeni bir sayı biçimi ya da birim görüldüğünde, verify modülü değiştirilecekken."
---

# numeric-verify

Bu proje, dil modelinin rakam uydurmasını iki katmanda engeller (ADR-004):
1. **Yapısal katman:** Model sayı yazmaz, `{{KPI:<kpi>:<yil>:<gerceklesmis|tahmin>}}` yer tutucusu yazar. Değeri kod yerleştirir.
2. **Denetim katmanı:** Taslak doldurulmadan önce şu kurallar denetlenir:
   - serbest metinde sayı olmamalı;
   - her yer tutucunun bir kaydı olmalı;
   - yer tutucunun türü kayıtla aynı olmalı;
   - tahmin değeri öngörü kipinde yazılmalı.

   Ayrıca serbest üretimli karşılaştırma kolunda (deney b, c) sayılar Türkçe biçimle ayrıştırılıp kaynakla ε toleransında eşlenir.

Kod: `services/report-service/report_service/verify/numbers.py`, `services/report-service/report_service/verify/tense.py`, `services/report-service/report_service/generation/placeholders.py`. Bu modüller projede sayı ayrıştırmanın **tek kaynağıdır** (`.claude/rules/python.md`).

## Adımlar

1. Bir taslağı denetle ve doldur:
   ```
   python .claude/skills/numeric-verify/scripts/check_draft.py --draft taslak.txt --records kayitlar.json
   ```
   - Çıkış 0: `text` alanı doldurulmuş taslaktır; `claims` alanındaki her öğe `draft_claim` tablosuna gider.
   - Çıkış 1: `errors` listesi döner. Her hata türünün ne yapılacağı aşağıdaki tabloda.
2. Hata türüne göre davran:

| Hata | Anlamı | Ne yapılır |
|---|---|---|
| `serbest metinde sayı` | Model yer tutucu yerine sayı yazdı | Yeniden üret (`rag-draft`); tekrarlıyorsa istem kuralı 3'ü güçlendir |
| `kaynak kaydı yok` | Model, verisi olmayan bir KPI/yıl istedi | Uydurma; cümleyi çıkar, "VERİ EKSİK" olarak raporla (R-GEN-04) |
| `tür uyuşmazlığı` | Tahmin kaydı gerçekleşmiş diye çağrıldı ya da tersi | Yeniden üret; tekrarlıyorsa yer tutucu listesindeki tür etiketini kontrol et |
| `kip hatası` | Tahmin geçmiş zamanla ya da gerçekleşmiş öngörüyle yazıldı | Yeniden üret; kural `tense.py`'yi tanımıyorsa önce test ekle |

3. Yeni bir biçim görüldüyse (ör. "1,2 milyar kWh", "‰") **önce** `services/report-service/tests/test_numbers.py`'ye başarısız bir test ekle, sonra `numbers.py`'yi düzelt.

## Desteklenen biçimler ve bilinen belirsizlikler

Ayrıntı: `references/formats.md`. Özet:
- `12.450,5` → 12450,5 · `1,5` → 1,5 · `12.5` → 12,5 · `1.234` → 1234 (**belirsiz**; Türkçe metin varsayımıyla binlik sayılır).
- Ölçek: bin, milyon, milyar. Yüzde: `%12,5`, `yüzde 40`.
- Birim tabanları: tCO2e (kt, Mt), kWh (MWh, GWh), m3, t (kg).
- Ayraçsız, birimsiz, 1900–2100 arası tam sayılar yıl sayılır, değer değil.
- Ad parçası sayılar değer değildir: "Kapsam 1", "TSRS 2", "GRI 305", "ISO 14001", "madde 29(a)".

## Tuzaklar

- **"%8 azaldı" bir değerdir.** Serbest metinde yazılamaz. Değişim oranı gerekiyorsa ayrı bir KPI kaydı olarak (ör. `emisyon_degisim_orani`) üretilir ve yer tutucuyla çağrılır.
- **Kip kuralları dar tutuldu.** `tense.py` tahmin cümlesinde bir öngörü işareti bulamazsa hata verir (güvenli taraf). "… düzeyindedir" gibi kipsiz cümleler reddedilir; bu bilinçli bir tercih.
- **Yan cümleler.** "2024'te gerçekleşen 43.650 tCO2e'ye göre 2028'de … öngörülmektedir" cümlesinde iki tür aynı cümlede geçer; kip denetimi bu durumda hata verebilir. İstem kuralı 4 bu yüzden iki türün aynı cümlede karıştırılmamasını ister.
- **ε göreli hatadır** (varsayılan 0,005, yani %0,5). Yuvarlanmış raporlarda ("yaklaşık 12 bin ton") eşleşme başarısız olabilir. ε'u gevşetmek ADR gerektirir.

## Örnek

`kayitlar.json`: `shared/contracts/examples/forecast_record.example.json` (2028, tahmin, 39870 tCO2e).

Taslak:
```
S-03 senaryosunda 2028 yılı emisyonunun {{KPI:toplam_emisyon:2028:tahmin}} olması öngörülmektedir [2].
```
Çıktı (`ok: true`):
```
S-03 senaryosunda 2028 yılı emisyonunun 39.870 tCO2e (tahmin) olması öngörülmektedir [2].
claims: [{"kpi": "toplam_emisyon", "yil": 2028, "deger": 39870, "veri_turu": "tahmin", "model_id": "xgb-v3.2", ...}]
```
Aynı cümle "… olarak gerçekleşmiştir" ile yazılsaydı çıktı `ok: false` ve `kip hatası: tahmin değeri geçmiş/gerçekleşmiş kipiyle yazılmış` olurdu.

## Kontrol listesi

- [ ] `python -m pytest services/report-service/tests -q` yeşil
- [ ] Yeni biçim için önce test, sonra kod
- [ ] Yeniden üretme döngüsü en fazla 2 tur; sonra orkestratöre

## Dosyalar

- `scripts/check_draft.py`: denetle + doldur (CLI)
- `references/formats.md`: biçim tablosu ve belirsizlikler
