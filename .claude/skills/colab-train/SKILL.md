---
name: colab-train
description: "Google Colab'da çalışacak eğitim veya değerlendirme defteri hazırlamak ve koşu kaydını (run.json) üretip doğrulamak için kullan. Ajanlar Colab'ı çalıştıramaz; defteri kullanıcı çalıştırır. Tetikleyiciler: GPU gerektiren iş (BERT ince ayarı, embedding üretimi), taban çizgisinin temiz ortamda koşulması, bir sonucun tezde kullanılacak olması."
---

# colab-train

Tezde raporlanacak her sayı tekrarlanabilir bir koşuya bağlı olmalıdır (R-REP-01, ADR-005). Colab oturumu kalıcı değildir. Bu yüzden koşunun kimliğini bir kayıt dosyası taşır: hangi commit, hangi veri, hangi tohum, hangi paketler, hangi donanım. Model dosyası Drive'da kalır, kayıt repoya girer.

## Sınır

Ajanların Colab'a erişimi yoktur. `ml-engineer` defteri hazırlar, **kullanıcı çalıştırır** ve `run.json`'u repoya ekler. Ajan, kullanıcının çalıştırmadığı bir koşunun sonucunu raporlayamaz.

## Adımlar

1. Şablonu kopyala: `assets/train_template.ipynb` → `notebooks/colab/<görev>-<ad>.ipynb`.
2. Yalnızca 1. hücredeki parametreleri ve 5. hücredeki eğitim kodunu değiştir. Diğer hücreler aynı kalır:
   - 2. hücre: belirli commit'i klonlar;
   - 3. hücre: Drive'ı bağlar;
   - 4. hücre: tohumları sabitler;
   - 6. hücre: run.json yazar.
3. Defteri commit'le. `GIT_SHA` olarak **bu commit'in** kimliğini kullanıcıya ver.
4. Kullanıcıya talimat ver:
   1. Colab'da aç.
   2. Çalışma zamanı → GPU (gerekiyorsa).
   3. Çalışma zamanını yeniden başlat ve tümünü çalıştır.
   4. Drive'daki `ecoizge/runs/<run_id>/run.json` dosyasını repoya `runs/<run_id>/run.json` olarak ekle.
5. Kaydı doğrula:
   ```
   python .claude/skills/colab-train/scripts/run_record.py validate runs/<run_id>/run.json
   ```
6. Koşuyu `evaluator`'a ver. Kabul kararı onay arayüzünden geçer (`durum: onay_bekliyor` → `kabul`); ajan bu alanı kendisi değiştirmez.

## run.json alanları

Şema: `references/run.schema.json`. `create` komutu şu alanları kendisi doldurur; elle yazılmaz:
- `run_id` (`YYYYMMDD-HHMMSS-<görev>`);
- `git_sha`;
- `paketler`;
- `donanim`;
- `olusturma`;
- `durum = onay_bekliyor`.

Çağıran şunları verir: `gorev`, `veri_surumu`, `katalog_surumu`, `tohum`, `metrikler`, isteğe bağlı olarak `parametreler`, `model_yolu`, `altin_kume_kullanildi`.

## Tuzaklar

- **"Tümünü çalıştır" yetmez, önce yeniden başlat.** Önceki hücre durumuyla üretilmiş sonuç tekrarlanamaz.
- **GPU belirlenimsizliği.** `cudnn.deterministic = True` olsa bile bazı işlemler GPU'da bit düzeyinde aynı sonucu vermez. Tezde aynı tohumla iki koşunun farkını bir kez ölç ve raporla.
- **Altın küme yalnızca nihai deneylerde.** Şablondaki `assert`, `ALTIN_KUME=True` değerini yalnızca S22 ve S23 için kabul eder. Bunun dışında altın kümeyle koşu yapılmaz.
- **Gizli veri Colab'a yüklenmez** (ADR-011). Drive'a yalnızca kamu ve iç sınıf veri konur.
- **Model dosyası git'e girmez** (`.gitignore`: `*.pt`, `*.bin`, `*.safetensors`, `models/`).

## Örnek

```json
{"run_id": "20261120-143005-s14", "git_sha": "56d1b10", "gorev": "S14", "veri_surumu": "reviewed-2026-11-20",
 "katalog_surumu": "catalog_v1", "tohum": 43, "paketler": {"scikit-learn": "1.5.2", "numpy": "2.1.3"},
 "donanim": "Linux x86_64 · Python 3.11.9", "metrikler": {"f1_makro": 0.47, "f1_karsilanan": 0.58},
 "durum": "onay_bekliyor", "olusturma": "2026-11-20T14:30:05"}
```

## Kontrol listesi

- [ ] Defter şablondan; yalnızca parametre ve eğitim hücresi değişti
- [ ] `GIT_SHA` gerçek commit; kullanıcı yeniden başlatıp tümünü çalıştırdı
- [ ] `run_record.py validate` 0
- [ ] Koşu onaya gönderildi

## Dosyalar

- `assets/train_template.ipynb`: Colab şablonu (6 hücre)
- `scripts/run_record.py`: run.json üret ve doğrula
- `references/run.schema.json`: kayıt şeması
