# EcoIzge · Sürdürülebilirlik Yönetim ve Güvence Sistemi

İki bitirme projesinin ortak reposu (GİBTÜ, 2026–2027):
- Mehmet Güneş: raporlama modülü (PDF işleme, boşluk analizi, RAG taslak, sayısal doğrulama).
- Zemzem Boyluğ: tahminleme modülü.

Şu anki faz ve durum: `docs/PROGRESS.md`, `tasks/README.md`.

## Çalışma modeli

- Ana oturum `engineering-orchestrator` ajanıdır (`.claude/settings.json`). Görev dağıtımı, birleştirme, çelişki çözümü ve nihai karar onundur. Alt ajanlar birbirini çağıramaz.
- Ajanlar: `.claude/agents/` · Skill'ler: `.claude/skills/` · Kurallar: `.claude/rules/`
- Yönlendirme tablosu: `docs/ORCHESTRATION.md` · Yetkinlik matrisi: `docs/COMPETENCY_MATRIX.md`
- Yazma alanları ve korumalı yollar: `.claude/hooks/write_scopes.json` (tek kaynak, `guard.py` zorlar)

## Komutlar

| İş | Komut |
|---|---|
| Kurulum | `pip install -r requirements-dev.txt` (çıkarım ve eğitim için ayrıca `requirements-train.txt`) |
| Tüm kalite kapısı (bitti tanımı) | `python tools/check_all.py` |
| Testler | `python -m pytest -q` |
| Veri doğrulama | `python tools/validate_data.py [dosya]` |
| Sistem bütünlüğü | `python tools/check_consistency.py` |
| Etiketleyici uyumu | `python tools/kappa.py A.csv B.csv` |
| Onay arayüzü | `streamlit run services/review-ui/app.py` |

## Her zaman

- Bir görevi tamam saymadan önce `python tools/check_all.py` çıktısını gör (`.claude/rules/quality-gates.md`).
- Test edilmemiş işi "tamam" yazma; "test edilemedi: neden" yaz.
- Gerçek sonuçlar yalnızca `docs/PROGRESS.md`'ye, tarih ve komutla yazılır.
- Belgelerde durum etiketi kullan: `[uygulandı]`, `[kısmi]`, `[hedef]` (`.claude/rules/docs.md`).
- Gizli veri, altın küme ve insan onayı kuralları: `.claude/rules/security.md`.

## Belgeler

- Gereksinimler ve izlenebilirlik: `docs/REQUIREMENTS.md`, `docs/TRACEABILITY.md`
- Mimari ve veri modeli: `docs/ARCHITECTURE.md`, `docs/DATA_MODEL.md`
- API ve güvenlik: `docs/API_SPEC.md`, `docs/SECURITY.md`
- Test planı ve kararlar: `docs/TEST_PLAN.md`, `docs/DECISIONS.md`
- Etiketleme kılavuzu: `docs/labeling/etiket_kilavuzu_v0.md` · Katalog: `data/catalog/`
- Analiz geçmişi: `docs/analysis/`
