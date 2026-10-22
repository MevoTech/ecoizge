---
name: label-propose
description: Etiketleme kılavuzuna göre paragraf × madde etiket önerisi üretmek için kullan. Çıktı yalnızca data/labels/proposals/ altına gider.
allowed-tools: Bash(python tools/validate_data.py *)
---

# label-propose

## Girdi
`paragraphs.jsonl`, katalog sürümü, kılavuz sürümü, tur türü (`pilot-kor` | `toplu`).

## Çıktı
`data/labels/proposals/<tur>-<rapor_id>-<tarih>.csv` — sütunlar `data/labels/etiket_sablonu.csv` ile aynı; `kaynak = model_onerisi`, `etiketleyen = claude`.

## Adımlar
1. Her paragraf için kılavuz §4 karar adımlarını uygula.
2. İlgili madde yoksa tek satır `madde_id = NONE`.
3. `karsilama` ∈ {2, 1, U, NONE}; `guven` ∈ [0,1]; `gerekce` ≤ 2 cümle ve kılavuz bölümüne atıf.
4. Kılavuzda karşılığı olmayan durumda `gerekce` başına `kılavuz-belirsiz:` yaz.
5. `python tools/validate_data.py <dosya>` → 0.

## Kontrol listesi
- [ ] Körleme turunda insan etiketleri görülmedi
- [ ] Doğrulayıcı geçti
