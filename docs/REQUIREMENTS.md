# Gereksinimler

Kaynak:
- Mehmet'in proje formu ve Teknik Kapsam 7 (dört hedef);
- Teknik Kapsam 5.4 (denetim kuralları);
- Geliştirme 2 §5 (güvenlik);
- `docs/analysis/00_ANALIZ_RAPORU.md` bulguları (B1–B20).

Kimlikler yalnızca burada tanımlanır. Her kimlik `docs/DEVELOPMENT_PLAN.md`'de en az bir aşamanın "Gereksinimler" satırına ve `docs/TRACEABILITY.md`'ye bağlıdır; denetim: `python tools/check_consistency.py`.

| Kimlik | Gereksinim | Kaynak |
|---|---|---|
| R-KAT-01 | Standart maddeleri katalogda madde kimliği, standart, bölüm, referans, özet, zorunluluk, veri türü, profil ve resmî kaynak doğrulamasıyla tutulur | Form hedef 1, TK 7 |
| R-KAT-02 | Şirket bir rapor profili seçer (VSME Temel, VSME Kapsamlı, TSRS); boşluk analizi o profilin maddeleriyle çalışır | G2 §4 |
| R-PDF-01 | Yüklenen PDF'ten paragraf ve tablolar sayfa ve başlık bağlamıyla çıkarılır | TK 5.4, S-11 |
| R-PDF-02 | Çıkarım kalitesi elle kontrol edilmiş bir kümede ölçülür ve raporlanır | B14 |
| R-ETK-01 | Paragraf × madde etiketleri kılavuza göre üretilir, doğrulanır; uyum ağırlıklı κ ile ölçülür | S-11, B5, B6 |
| R-ETK-02 | Altın test kümesi insan onaylıdır, dondurulur ve değişmezliği otomatik doğrulanır | B11 |
| R-GAP-01 | Her madde için karşılandı / kısmi / eksik kararı verilir | Form hedef 2 |
| R-GAP-02 | TF-IDF + LR taban çizgisi ile BERT tabanlı model aynı kümede karşılaştırılır (deney a) | TK 7 |
| R-GAP-03 | Çok unsurlu maddelerde rapor düzeyi karar unsur kapsamasıyla verilir | B4, ADR-008 |
| R-GAP-04 | Spesifiklik skoru Türkçe metinde çalışır ve katkısı ablasyonla ölçülür | B1, ADR-007 |
| R-RET-01 | Embedding modeli kendi kümemizde Recall@k ve MRR ile seçilir | B2 |
| R-RET-02 | Retrieval her zaman şirket kimliğiyle filtrelenir; başka şirketin verisi bağlama girmez | G2 §5, B19 |
| R-GEN-01 | Eksik madde için kaynaklı Türkçe taslak üretilir; her cümle kaynak atfı taşır | Form hedef 3 |
| R-GEN-02 | Eksik maddeler için `yaz`, kısmi maddeler için `tamamla` kipi vardır | B3, ADR-008 |
| R-GEN-03 | Dil modeli sayı yazmaz; sayılar yer tutucuyla üretilir ve kaynak kayıttan deterministik doldurulur | B10, ADR-004 |
| R-GEN-04 | Veri yoksa sistem "veri eksik" der, değer uydurmaz | TK 1 |
| R-VER-01 | Taslaktaki sayılar Türkçe biçim, ölçek ve birimle normalleştirilip kaynakla ε toleransında eşlenir | TK 5.4, S-15, B9 |
| R-VER-02 | Kaynak atfı olmayan cümle işaretlenir | TK 5.4 |
| R-VER-03 | Gerçekleşmiş ve tahmin değerleri tür ve kip düzeyinde ayrılır; karışım reddedilir | S-19 |
| R-EVL-01 | Boşluk analizi P/R/F1 ile, rapor bazında bölünmüş veride ölçülür | Form hedef 2 |
| R-EVL-02 | Üretim kalitesi maskeleme kümesinde ROUGE-L ve BERTScore ile ölçülür | B7, ADR-009 |
| R-EVL-03 | Halüsinasyon iddia düzeyinde desteklenen / desteksiz / çelişen olarak ölçülür | B8 |
| R-EVL-04 | Deney (b) RAG'li/RAG'siz/yer tutuculu, deney (c) doğrulama açık/kapalı karşılaştırması yapılır | TK 7, ADR-004 |
| R-API-01 | Servisler REST + JSON sözleşmesiyle konuşur; her yanıt `schema_version` taşır | TK 5.3, B16 |
| R-API-02 | Uzun işler (analiz, taslak) asenkron iş olarak yürür ve durumu sorgulanır | S-21, B15 |
| R-SEC-01 | Yüklenen belge metni prompta veri olarak girer; belge içindeki talimatlar etkisizdir | B17 |
| R-SEC-02 | Gizli anahtarlar ve pilot veri sürüm kontrolüne, loglara ve ajanlara açılmaz | G2 §5 |
| R-SEC-03 | Harici LLM'e gönderilebilecek veri sınıfları tanımlıdır; gizli veri gönderilmez | B18, ADR-011 |
| R-SEC-04 | Her veri değişikliği denetim kaydına (kim, ne, ne zaman, eski/yeni) yazılır | TK 5.2 |
| R-REP-01 | Her eğitim ve deney koşusu tekrarlanabilir kayıt (`run.json`) üretir | B20, ADR-005 |
| R-HIL-01 | Etiket, model, prompt ve taslak kabulü insan onay arayüzünden geçer ve kayda alınır | Kullanıcı (2026-10-22) |
| R-INT-01 | Tahmin modülünün çıktısı ortak sözleşmeyle rapor taslağına bağlanır | TK 9 |
| R-EXP-01 | Onaylı taslak DOCX/PDF olarak dışa aktarılır | Kullanıcı ("yazdırma") |
| R-AGT-01 | Ajan, skill, kural, belge ve görev sistemi tutarlıdır ve otomatik denetlenir | Kullanıcı kuralları 1–10 |
