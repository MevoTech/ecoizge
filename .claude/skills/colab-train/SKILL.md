---
name: colab-train
description: Google Colab'da çalışacak eğitim veya değerlendirme defteri hazırlamak için kullan. Ajanlar Colab'ı çalıştıramaz; defteri kullanıcı çalıştırır.
---

# colab-train

## Defter iskeleti (`notebooks/colab/<ad>.ipynb`)
1. Kurulum: repoyu belirli commit'te klonla (`git checkout <sha>`), `pip install -r requirements-train.txt`.
2. Drive bağla: veri `MyDrive/ecoizge/data/`, model çıktısı `MyDrive/ecoizge/models/<run_id>/`.
3. Tohum: `random`, `numpy`, `torch` (+ `torch.backends.cudnn.deterministic = True`).
4. Eğitim/değerlendirme.
5. `run.json` yaz: `{run_id, git_sha, gorev, veri_surumu, katalog_surumu, tohum, paketler, donanim, metrikler, model_yolu, durum: "onay_bekliyor"}`.
6. `run.json`'u indir veya Drive'dan repoya `runs/<run_id>/run.json` olarak ekle.

## Kurallar
- Model dosyası git'e girmez.
- Gizli veri Colab'a yüklenmez (ADR-011).
- Altın küme yalnızca `evaluator` deneyinde ve manifest doğrulamasından sonra.

## Kontrol listesi
- [ ] Defter baştan sona temiz çekirdekte çalıştı (kullanıcı onayı)
- [ ] run.json alanları eksiksiz
