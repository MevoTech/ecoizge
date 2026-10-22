---
name: plan-task
description: Bir isteği ölçülebilir alt görevlere bölmek, her birine ajan, kabul kriteri ve kanıt komutu atamak için kullan. Yeni bir tasks/Sxx dosyası açılırken veya büyük bir istek geldiğinde.
---

# plan-task

## Girdi
Kullanıcı isteği veya görev kimliği; `tasks/README.md`; ilgili R-* kimlikleri.

## Çıktı
Alt görev listesi (görev paketi biçiminde, `.claude/rules/orchestration.md`). Yeni görevse `tasks/Sxx-<ad>.md` (şablon: `tasks/_TEMPLATE.md`).

## Adımlar
1. İsteği tek cümlelik amaca indir; hangi R-* gereksinimlerine dokunduğunu bul. Karşılığı yoksa önce `architect`'ten REQUIREMENTS güncellemesi iste.
2. Bağımlılıkları çıkar: hangi çıktı hangisinin girdisi? Bağımsız olanları paralel işaretle.
3. Her alt görev için ajan seç (`docs/ORCHESTRATION.md` §2), yazma alanının yettiğini doğrula (`.claude/hooks/write_scopes.json`).
4. Kabul kriterlerini ölçülebilir yaz ("çalışır" değil, "`pytest tests/x -q` 0 ile çıkar, 12 test").
5. İnsan onayı gereken adımları işaretle (`.claude/rules/security.md` §İnsan onayı).

## Kontrol listesi
- [ ] Her alt görevin tek sahibi var
- [ ] Her kabul kriterinin bir kanıt komutu var
- [ ] Paralel görevlerin yazma alanları kesişmiyor
- [ ] Geri alınamaz adım varsa onay noktası konmuş
