---
name: phase-gate
description: "Aktif aşamayı kapatmak için kullan: test, çalıştırma, kabul maddelerinin tek tek doğrulanması, öz-denetim, inceleme, kanıt ve PROGRESS güncellemesi, birleştirme ve sxx-done etiketi. Kullanım /phase-gate. Tetikleyiciler: bir aşamanın görevleri bittiğinde, kullanıcı aşamanın kapanıp kapanamayacağını sorduğunda."
argument-hint: "[Sxx]"
---

# phase-gate

Aşama döngüsünün ikinci yarısı ([docs/AI_WORKFLOW.md](../../../docs/AI_WORKFLOW.md) §4). Aktif aşama PROGRESS §1'de 🟨 olandır; birden çoksa argümanla verilir. Her adımın komut çıktısının özetini (geçen ve kalan sayıları, hata satırları) not al. Koşmadığın komutu "geçti" diye yazma.

## Adımlar

1. **Test:** `python tools/check_all.py` (ruff, biçim, pytest, veri doğrulama, tutarlılık, altın küme). Aşamaya özgü komutlar planın "Doğrulama" satırındadır; hepsini koş.
2. **Statik kontroller**
   - Yeni TODO yok: `git diff main...HEAD | grep -n "^+.*TODO"` → 0 satır.
   - Türkçe kuralı: yeni kodda Türkçe metin üzerinde `.lower()`/`.upper()` yok; sayı ayrıştırma `report_service.verify.numbers` dışında yok; `f"{x:,}"` yok.
   - Gizli yol yok: yeni kodda `data/raw/pilot`, `.env`, `secrets/` okuması yok.
3. **Çalıştır:** Aşamanın ana akışını bir kez gerçekten yürüt. Arayüz değiştiyse `streamlit run services/review-ui/app.py` ile başsız açılış ve tarayıcı görüntüsü; çıkarım değiştiyse gerçek bir raporla `pipelines/extract.py`. Gerçek veri yoksa "yalnızca sentetik veriyle denendi" yaz.
4. **Doğrula:** Planın "Kabul" maddelerini **tek tek** listele: ✅ (kanıt komutu ve özet) ya da ❌ (neden). Ortak kriterler AK-G1…AK-G5'i ekle.
5. **Öz-denetim:** `AGENTS.md` §7'deki her soruya bir cümleyle cevap ver.
6. **İnceleme:** Kod değiştiyse `code-reviewer`; güvenlik kritikse (`guard`, yükleme, istem, retrieval, gizli veri) ayrıca `security-auditor`. Kritik bulgular düzeltilmeden devam etme.
7. **Belge tutarlılığı:** `git diff main...HEAD --stat` → davranışı değişen her alanın belgesi aynı dalda güncel mi? `python tools/check_consistency.py`.
8. **Düzelt:** ❌ olan madde varsa önce kırmızı test, sonra düzeltme; 1. adımdan tekrar. Aynı yaklaşım iki kez başarısız olursa dur ve kullanıcıya seçenekleri sun. Düzeltilemeyenler KL-xx ya da PROGRESS §5'e.
9. **🔒 aşama mı?** Bağımsız denetim ([docs/AI_WORKFLOW.md](../../../docs/AI_WORKFLOW.md) §6) → `docs/audits/Sxx.md`. Kritik ve yüksek bulgular kapanmadan ✅ yapma.
10. **PROGRESS:** §4'e kanıt günlüğü (biçim §4'ün başında); §1'de durum, bitiş tarihi, etiket. Plandaki "Durum" satırını ve görev simgelerini eşitle.
    - Bütün kabul maddeleri kanıtlı → ✅.
    - Yalnızca ✋ görevler eksik → "✅ (✋ hariç)"; bekleyenler PROGRESS §5'e.
    - Başka eksik var → 🟨 kalır ya da ⛔ (neden yazılır).
11. **Birleştir:** `git switch main && git merge --no-ff asama/Sxx-*`, `git tag sxx-done`. `git push` kullanıcıya sorulur (`--force` asla).
12. **Rapor** ([.claude/rules/orchestration.md](../../rules/orchestration.md) biçimi): Sonuç, Yapılanlar, Kanıt, Test edilemeyenler, Açık konular, Onay gerektirenler, sonraki bağımsız aşama.

## Tuzaklar

- **"Geçmesi beklenir" kanıt değildir.** Komut koşulamadıysa "test edilemedi: <neden>" yazılır ve aşama en fazla 🟨 kalır.
- **Sentetik veriyle ✅.** Gerçek rapor gerektiren kabul maddesi (S04, S05, S14) sentetik testle kapanmaz.
- **Testi gevşeterek geçirmek** yasaktır; eşik değişikliği yalnızca gerekçeli ADR ile.
- **Eski `.pyc` önbelleği** kasıtlı bozma denemesinde yanlış sonuç verebilir; deneme `python -B` ile tekrarlanır (2026-10-22).
- **Etiketi kapanıştan önce koymak.** `sxx-done` yalnızca PROGRESS §1 güncellenip commit edildikten sonra.

## Örnek

S15'in kapanışı (2026-10-22): `python tools/check_all.py` 6/6 GEÇTİ. `services/report-service/tests` 40 geçti. Kasıtlı bozma: Türkçe ayraç ayrıştırma ve yer tutucu tür kontrolü bozulunca birer test kırmızıya döndü, geri alınınca yeşil. Kabul maddeleri: "Testler geçer" ✅, "bilinen sınırlar modül belgesinde" ✅ (`numbers.py` docstring). 🔒 değil, bağımsız denetim gerekmedi. PROGRESS §1 → ✅, §4 kaydı `### S15`.

## Kontrol listesi

- [ ] `python tools/check_all.py` çıkış 0, özet PROGRESS'te
- [ ] Her kabul maddesi ✅/❌ ve kanıtıyla listelendi; AK-G1…G5
- [ ] Öz-denetim cevapları yazıldı
- [ ] İnceleme yapıldı; 🔒 ise `docs/audits/Sxx.md` var
- [ ] PROGRESS §1, §4 ve plan "Durum" satırı eşit; `check_consistency` 0 hata
- [ ] Birleştirme ve `sxx-done` etiketi; push kullanıcı onayıyla
