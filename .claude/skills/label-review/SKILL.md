---
name: label-review
description: "İnsan onay akışını yürütmek için kullan: öneri dosyalarını onay arayüzüne (Streamlit) hazırlamak, kuyruk durumunu izlemek, onaylanan etiketleri doğrulamak. Tetikleyiciler: yeni öneri dosyası üretildiğinde, kullanıcı onay turu bitirdiğinde, düzeltme oranı sorulduğunda, altın küme dondurulmadan önce."
---

# label-review

İnsan onayı bu projede bir tasarım ilkesidir (R-HIL-01): model önerir, insan karar verir, karar silinmez. Bu skill, akışın ajan tarafındaki işini tarif eder. **Kararları insan verir**; ajanlar onaylı dosyalara ve onay günlüğüne yazamaz (guard bu yolları korur).

## Akış

```
data/labels/proposals/<dosya>.csv          ← label-propose (model)
        │  insan: streamlit run services/review-ui/app.py
        ▼
data/labels/reviewed/<aynı ad>.csv         ← yalnızca arayüz yazar
data/reviews/reviews.jsonl                 ← her karar bir satır; yalnızca ekleme
        │  insan: python tools/gold_manifest.py freeze --by "<ad>"   (test raporları için, S12)
        ▼
data/gold/ + MANIFEST.json                 ← dondurulmuş altın küme
```

Kararların anlamı:
- **Onayla:** satır olduğu gibi kabul; `kaynak = insan_onayli`, `etiketleyen` = inceleyen kişi.
- **Düzelt:** yeni karşılama değeri ve gerekçe zorunlu; `kaynak = insan`. `NONE` seçilirse `madde_id` de `NONE` olur.
- **Reddet:** satır onaylı dosyaya girmez (ör. yanlış madde eşleşmesi), ama günlükte kalır. Gerekçe zorunludur.

## Adımlar

1. Öneri dosyasının geçerli olduğunu doğrula:
   `python tools/validate_data.py data/labels/proposals/<dosya>.csv` → 0.
2. Kullanıcıya şu komutu ver (kendi makinesinde, repo kökünde):
   ```
   pip install -r services/review-ui/requirements.txt
   streamlit run services/review-ui/app.py
   ```
   Sol panelde adını yazar, dosyayı seçer; her öneri için Onayla, Düzelt ya da Reddet'e basar.
3. Tur bitince durumu oku:
   ```
   python .claude/skills/label-review/scripts/review_status.py
   ```
4. Onaylı dosyaların doğruluğunu argümansız doğrulayıcıyla kontrol et: `python tools/validate_data.py`. Korumalı yol adını komuta yazma; guard engeller.
5. Orkestratöre raporla: dosya başına bekleyen, onaylanan, düzeltilen ve reddedilen sayıları; düzeltme ve red oranını. Oran %30'u geçerse kılavuz ya da öneri kalitesi sorununu ayrıca vurgula.

## Tuzaklar

- **Yeniden öneri üretmek kararları silmez.** Aynı dosya adına yeni öneri yazılırsa eski kararlar günlükte `etiket_id` ile kalır ve eşleşen satırlar "karara bağlanmış" sayılır. Yeni tur için yeni dosya adı kullan (tarih son eki).
- **`etiket_id` kararlıdır**: `<paragraf_id>::<madde_id>`. Çıkarım yeniden yapılıp `paragraf_id` kayarsa eski kararlar yetim kalır (bkz. `pdf-extract` → Tuzaklar).
- **Pilot körleme turunda** model önerileri arayüze yüklenmez; insan kendi etiketini ayrı bir dosyada üretir. κ bu iki bağımsız dosyadan hesaplanır (`agreement-kappa`). Model önerisini görüp onaylamak, κ'yı şişirir.
- **Arayüz yerelde çalışır.** Colab'da Streamlit doğrudan açılmaz, tünel gerekir; önerilen kullanım yereldir (ADR-006).

## Örnek

`review_status.py` çıktısı:
```
| dosya | toplam | bekleyen | onay | düzeltme | red | düzeltme+red oranı |
|---|---|---|---|---|---|---|
| toplu-karel-2026-11-02.csv | 214 | 0 | 158 | 41 | 15 | 26% |
```
Bu sonuç orkestratöre şöyle raporlanır: "214 önerinin 158'i onaylandı. Düzeltme ve red oranı %26, eşiğin altında. Düzeltmelerin 29'u 2 → 1 yönünde; model 'genel cümle'yi fazla tam sayıyor. Kılavuz §4.3'e örnek eklenmesi önerilir."

## Kontrol listesi

- [ ] Öneri dosyası doğrulayıcıdan geçti
- [ ] Kullanıcı turu bitirdi; `review_status.py` çıktısı rapora eklendi
- [ ] `python tools/validate_data.py` 0
- [ ] Düzeltme yönleri (2→1, 1→NONE …) özetlendi

## Dosyalar

- `scripts/review_status.py`: kuyruk durumu (salt-okunur)
- `services/review-ui/app.py`, `services/review-ui/review_ui/logic.py`: arayüz ve karar mantığı (sahibi `backend-engineer`)
