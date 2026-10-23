# Bağımsız denetim raporları

🔒 işaretli aşamaların (S02, S06, S08, S11, S12, S17, S18, S22) kapanıştan önceki bağımsız denetim raporları burada `Sxx.md` adıyla tutulur. İstem ve kurallar: [../AI_WORKFLOW.md](../AI_WORKFLOW.md) §6.

- Rapor kodu yazmamış bir denetçinin çıktısıdır; orkestratör olduğu gibi kaydeder.
- Bulgular önem sırasıyla yazılır: kritik, önemli, küçük. Her bulgunun düzeltme durumu raporun sonuna eklenir.
- Kayıt silinmez. Yeniden denetim aynı dosyaya tarihli yeni bölüm olarak eklenir.
- 🔒 olmayan aşamaların kod incelemeleri de buraya `Sxx-inceleme-<tarih>.md` adıyla konabilir.

| Rapor | Aşama | Tarih | Sonuç |
|---|---|---|---|
| [S04-S05-S07-inceleme-2026-10-23.md](S04-S05-S07-inceleme-2026-10-23.md) | S04, S05, S07 (pilot ekranları, commit 7b4ecaf) | 2026-10-23 | 1 kritik, 6 önemli; düzeltme durumu raporda |
| [S05-S07-inceleme-2026-10-23-sema.md](S05-S07-inceleme-2026-10-23-sema.md) | S05, S07 (etiket şeması 0.1, analiz ekranı; commit 999683c) | 2026-10-23 | 1 kritik, 8 önemli; Ö2 açık (KL-12) |
