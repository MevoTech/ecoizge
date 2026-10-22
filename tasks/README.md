# Görevler

Her görev bir dosyadır. Önbilgi alanları (`id, baslik, faz, durum, sorumlu, skills, gereksinimler, bagimlilik, insan_onayi`) `tools/check_consistency.py` tarafından denetlenir. Durum değerleri: `bekliyor`, `devam`, `tamam`, `engelli`. Bu tablodaki durum, dosyadaki durumla aynı olmak zorundadır. Fazlar `Geliştirme 2` takvimindendir (F1: 12 Eki–15 Kas … F8: 10–31 May). Yeni görev şablonu: [_TEMPLATE.md](_TEMPLATE.md).

| Görev | Başlık | Faz | Durum | Sorumlu |
|---|---|---|---|---|
| [S01](S01-ajan-altyapisi.md) | Ajan, skill, kural ve kanca altyapısı | F1 | devam | `engineering-orchestrator` |
| [S02](S02-katalog-v1.md) | Katalog v1: TSRS 1 çekirdek ve alt maddelere bölme | F1 | bekliyor | `engineering-orchestrator` |
| [S03](S03-rapor-derlemi.md) | Rapor derlemi ve tarama tablosu | F1 | bekliyor | `researcher` |
| [S04](S04-pdf-cikarim.md) | PDF çıkarım hattı v0 ve çıkarım kalite kümesi | F1 | devam | `ml-engineer` |
| [S05](S05-pilot-etiketleme.md) | Pilot etiketleme, κ ve kılavuz v1 | F1 | bekliyor | `annotation-assistant` |
| [S06](S06-belge-uzlastirma.md) | REQUIREMENTS, DATA_MODEL ve API_SPEC v1 uzlaştırması (Zemzem ile) | F2 | bekliyor | `architect` |
| [S07](S07-onay-arayuzu.md) | Onay arayüzü v1 ve toplu ön etiketleme | F2 | devam | `backend-engineer` |
| [S08](S08-yontem-kararlari.md) | Yöntem kararları (ADR-007…ADR-012) | F2 | devam | `engineering-orchestrator` |
| [S09](S09-compose-db.md) | Docker Compose, PostgreSQL + pgvector, Alembic | F3 | bekliyor | `backend-engineer` |
| [S10](S10-report-service-iskelet.md) | report-service iskeleti, POST /reports, iş tablosu, yükleme güvenliği | F3 | bekliyor | `backend-engineer` |
| [S11](S11-ortak-sozlesme.md) | Ortak JSON sözleşmesi ve iki serviste sözleşme testleri | F3 | devam | `architect` |
| [S12](S12-altin-kume.md) | Altın test kümesini dondur | F4 | bekliyor | `engineering-orchestrator` |
| [S13](S13-embedding-secimi.md) | Embedding modeli seçimi | F4 | bekliyor | `ml-engineer` |
| [S14](S14-taban-cizgisi.md) | TF-IDF + LR taban çizgisi, gruplu CV, eşikler, unsur kapsama | F4 | devam | `ml-engineer` |
| [S15](S15-sayisal-dogrulama.md) | Türkçe sayı normalleştirici ve kip denetimi | F4 | tamam | `ml-engineer` |
| [S16](S16-bert-ince-ayar.md) | BERTurk / çok dilli ince ayar ve Türkçe spesifiklik başlığı (Colab) | F5 | bekliyor | `ml-engineer` |
| [S17](S17-rag-taslak.md) | LLM seçimi, RAG yaz/tamamla, yer tutuculu üretim, injection testi | F5 | devam | `ml-engineer` |
| [S18](S18-dogrulama-katmani.md) | Doğrulama katmanı entegrasyonu, kaynaksız cümle, kiracı izolasyonu | F5 | bekliyor | `ml-engineer` |
| [S19](S19-maskeleme-kumesi.md) | Maskeleme değerlendirme kümesi | F5 | bekliyor | `evaluator` |
| [S20](S20-tahmin-baglama.md) | Tahmin JSON'unun taslağa bağlanması | F6 | bekliyor | `backend-engineer` |
| [S21](S21-uctan-uca-demo.md) | Uçtan uca demo ve DOCX/PDF dışa aktarım | F6 | bekliyor | `backend-engineer` |
| [S22](S22-tez-deneyleri.md) | Deneyler (a), (b), (c) ve ablasyonlar | F7 | bekliyor | `evaluator` |
| [S23](S23-uzman-degerlendirme.md) | Uzman değerlendirmesi (Likert) ve iddia etiketlemesi | F7 | bekliyor | `evaluator` |
| [S24](S24-tez-tablolari.md) | Tez tabloları ve figürleri koşu kayıtlarından | F8 | bekliyor | `evaluator` |
