# Orkestrasyon

Bağlayıcı kısa kurallar: `.claude/rules/orchestration.md`. Bu belge yönlendirme tablosunu ve gerekçeleri verir.

## 1. Model

```
                    Kullanıcı  ◀──── onay arayüzü (Streamlit)
                       │ ▲
                       ▼ │  (soru, onay, rapor)
             ┌───────────────────────┐
             │ engineering-orchestrator │   ana oturum: .claude/settings.json → "agent"
             └───────────────────────┘
        görev paketi │        ▲ yapılandırılmış rapor
   ┌──────────┬──────┴───┬─────┴─────┬───────────┬──────────┐
architect  researcher  backend-  ml-engineer  annotation-  evaluator  ...
                       engineer               assistant
   (alt ajanlar birbirini çağıramaz: `Agent` aracı yok, iç içe başlatma derinliği = 1)
```

Koordinasyon neden yalnızca orkestratör üzerinden:
1. Çelişkili kararlar tek yerde çözülür.
2. Bağlam maliyeti kontrol edilir.
3. Alt ajanlar kullanıcıya soru soramaz (Claude Code alt ajanlardan `AskUserQuestion`'ı kaldırır).
4. Bağımsız denetçilerin, denetledikleri işi yapan ajanın konuşmasını görmemesi sağlanır.

## 2. Yönlendirme tablosu

| İş türü | Sıra (→ sıralı, ‖ paralel) | İnsan onayı |
|---|---|---|
| Yeni özellik | `architect` → (`backend-engineer` ‖ `ml-engineer`) → `test-engineer` → `code-reviewer` | Sözleşme değişirse |
| Hata düzeltme | `test-engineer` (kırmızı test) → ilgili geliştirici → `code-reviewer` | — |
| Teknoloji seçimi | `researcher` → `ml-engineer` (deney) → `evaluator` → `architect` (ADR) | ADR kabulü |
| Etiketleme turu | `annotation-assistant` → onay arayüzü → `evaluator` (κ) | Her etiket |
| Model eğitimi | `ml-engineer` (defter) → kullanıcı Colab'da koşar → `evaluator` → onay arayüzü | Model terfisi |
| RAG / prompt değişikliği | `ml-engineer` → (`evaluator` ‖ `security-auditor`) → onay | Prompt sürümü |
| Güvenlik kritik değişiklik | geliştirici → `security-auditor` → `code-reviewer` | Kritik bulgu istisnası |
| Belge değişikliği | `architect` veya orkestratör → `docs-auditor` | — |
| Ortak şema / sözleşme | `architect` → Zemzem'in PR onayı → `test-engineer` | Her zaman |
| Katalog değişikliği | orkestratör (`catalog-update`) → `docs-auditor` | Her zaman |
| Tablo / grafik çıkarımı | `ml-engineer` (`table-extract`, `figure-extract`) → `test-engineer` → `code-reviewer` → `evaluator` (`table-eval`) | Altın tablo kümesi (insan), motor ADR'si |
| Faz sonu | `docs-auditor` ‖ `security-auditor` → orkestratör PROGRESS günceller | Faz kapanışı |

Seçim ilkesi: tablodaki en kısa yol. Tek dosyalık küçük iş için orkestratör kendisi yapar, ama kendi işini kendisi onaylamaz.

## 3. Karar yetkisi

| Karar | Kimde |
|---|---|
| Görev bölme, ajan seçimi, çelişki çözümü | `engineering-orchestrator` |
| Tasarım seçeneklerinin hazırlanması | `architect` (öneri) → orkestratör (karar) → ADR |
| Bir testin geçip geçmediği | Komut çıktısı (ajan değil) |
| Etiket, model, prompt, taslak kabulü | İnsan (onay arayüzü) |
| Altın küme dondurma | Yalnızca insan |
| Ortak sözleşme | Mehmet + Zemzem |

## 4. Paralel çalışma

- Yazma alanları ayrıktır (`.claude/hooks/write_scopes.json`). İki farklı ajan aynı dosyaya yazamaz; guard hook bunu engeller.
- Aynı ajandan iki örnek paralel çalışacaksa her biri `isolation: worktree` ile ayrı bir git çalışma ağacında çalışır. Birleştirmeyi orkestratör yapar.
- Paralel ajanların sonuçları birleştirilmeden önce orkestratör çakışan iddiaları karşılaştırır.

## 5. Çelişki çözümü

1. İki raporun iddiasını ve kanıtını yan yana koy.
2. Kanıtı komut çıktısına dayanan, dayanmayana üstün gelir.
3. İkisi de kanıtlıysa varsayım farkını bul ve ilgili uzmandan o varsayım için yeniden değerlendirme iste.
4. Hâlâ çözülmüyorsa kullanıcıya seçenekleri sun. Karar ADR'ye ya da görev dosyasının "Kararlar" bölümüne yazılır.

## 6. İnsan onayı akışı

Alt ajan "Onay gerektirenler" bölümüne yazar. Orkestratör iki yoldan birini seçer:
- tek seferlik karar ise kullanıcıya sorar;
- etiket, koşu ya da taslak gibi yığın kayıtsa onay arayüzüne gönderir.

Onay kaydı `data/reviews/reviews.jsonl` dosyasına yalnızca eklenir, silinmez.

## 7. Colab sınırı

Ajanların Colab'a erişimi yoktur. `ml-engineer` defteri `notebooks/colab/` altına yazar, kullanıcı Colab'da çalıştırır. Sonuç `runs/<run_id>/run.json` olarak repoya döner, model dosyası Drive'da kalır (ADR-005).
