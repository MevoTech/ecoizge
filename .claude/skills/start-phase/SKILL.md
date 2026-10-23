---
name: start-phase
description: "Bir geliştirme aşamasını başlatmak için kullan: bağımlılık ve kullanıcı eylemi kontrolü, girdi belgelerinin okunması, uygulama planı, dal ve PROGRESS güncellemesi. Kullanım /start-phase Sxx. Tetikleyiciler: kullanıcı yeni bir aşamaya geçmek istediğinde, bir aşama kapandıktan sonra sıradaki bağımsız aşama seçilirken."
argument-hint: "<Sxx>"
---

# start-phase

Aşama döngüsünün ilk yarısı ([docs/AI_WORKFLOW.md](../../../docs/AI_WORKFLOW.md) §4). Argüman: `$ARGUMENTS` (ör. `S04`). Kapanış `phase-gate` skill'indedir.

## Adımlar

1. **Bağımlılık kontrolü**
   - `docs/DEVELOPMENT_PLAN.md` içinde `## Sxx:` bölümünü bul; "Bağımlılık" satırını oku.
   - Her bağımlılığın `docs/PROGRESS.md` §1'de ✅ ya da "✅ (✋ hariç)" olduğunu doğrula. Görev düzeyindeki bağımlılıkta (`S03.T3`) plan satırının ✅ olması yeter.
   - Karşılanmıyorsa aşamayı başlatma; eksik bağımlılığı ve onu açacak işi kullanıcıya bildir.
2. **Kararlar ve kullanıcı eylemleri**
   - `docs/DECISIONS.md` "Açık kararlar" tablosunda bu aşamayı engelleyen D-xx var mı? Varsa ilgili görevleri ✋ işaretle ve bağımsız görevlerle devam et.
   - PROGRESS §2.1'de bu aşamanın U-xx maddelerini listele.
3. **Bağlamı yükle**
   - Aşamanın "Girdi" satırındaki belgeleri ve skill'leri oku (yalnızca ilgili bölümler).
   - `docs/00_INDEX.md` §2 tablosuyla karşılaştır.
   - `docs/KNOWN_LIMITATIONS.md` ve PROGRESS §5'te bu aşamaya ait madde var mı?
4. **Ortam kontrolü:** `python --version` (≥ 3.11), `git status` (temiz değilse önceki işi commit et ya da ayır), aşamaya göre `streamlit --version`, `docker compose version`.
5. **Uygulama planı** (PROGRESS §4'e `### Sxx: <ad> (tarih)` başlığıyla):
   - Her `Sxx.Tm` için: değişecek dosyalar, yazılacak testler, sorumlu alt ajan ve skill.
   - Her kabul maddesinin hangi komutla kanıtlanacağı.
   - Riskler ve varsayımlar.
   - 🔒 aşamada bağımsız denetimin ne zaman yapılacağı.
6. **Dal:** `git switch -c asama/Sxx-kisa-ad` (ad, plan başlığından ASCII `slug`).
7. **PROGRESS §1:** durum 🟨, dal adı, başlangıç tarihi. Plandaki "Durum" satırını da 🟨 yap (denetleyici ikisini karşılaştırır).
8. **Kullanıcıya özet** (en fazla 5 satır): hedef, görev sayısı, bekleyen U-xx, ilk görev. Ardından ilk göreve başla.

## Tuzaklar

- **Plan ile PROGRESS'in ayrışması.** Durum iki yerde yazılıdır; biri değişince diğeri de değişmezse `check_consistency` hata verir. Her iki dosyayı aynı commit'te güncelle.
- **✋ görevi ajanın yapması.** Altın küme dondurma, katalog onayı, Colab koşusu ve etiket kabulü kullanıcınındır. Ajan yalnızca hazırlığı yapar.
- **Bağımlılığı "neredeyse bitti" saymak.** 🟨 bir bağımlılık başlatma için yetmez. Görev düzeyinde bağımlılık yazılmışsa (`S04.T2`) yalnızca o görev bakılır.
- **Bağlamı şişirmek.** PDF'ler ve birim JSONL'leri bağlama alınmaz; özetleri betikle çıkarılır.

## Örnek

`/start-phase S05` (2026-10-23 durumu): Bağımlılık `S04.T2` ✅ ve `S07.T2` ✅, yani başlatılabilir. Açık karar D-06 yalnızca `S05.T7`'yi engeller. Bekleyen eylem U-04 (Mehmet'in kör etiketlemesi). Plan: T4 `annotation-assistant` öneri üretir (insan etiketini görmeden), T5 `evaluator` κ hesaplar. Kanıt `python tools/kappa.py data/labels/blind/<ad>/pilot_v0.csv data/labels/proposals/pilot_v0.csv`. İlk görev, U-04 tamamlanana kadar T4'tür.

## Kontrol listesi

- [ ] Bağımlılıklar PROGRESS'te ✅
- [ ] Engelleyen D-xx ve U-xx listelendi, ilgili görevler ✋
- [ ] Plan PROGRESS §4'te; her kabul maddesinin kanıt komutu yazılı
- [ ] Dal açıldı; PROGRESS §1 ve plan "Durum" satırı 🟨
- [ ] `python tools/check_consistency.py` 0 hata
