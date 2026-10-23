# Bilinen Kısıtlar

Tamamlanamayan iş kodda TODO olarak bırakılmaz; burada gerekçesiyle listelenir ([DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) AK-G5). Kodda `# KL-xx` yorumuyla, belgelerde kimlikle atıf yapılır.

- **Durum:** `Planlı` (bilinçli kapsam dışı) · `Aktif` (uygulamada var olan kısıt) · `Kapandı`.
- Yeni kayıt eklenirken numara artırılır. Eski kayıt silinmez; durumu güncellenir.

| ID | Kısıt | Gerekçe | Etki | Çıkış yolu | Durum |
|---|---|---|---|---|---|
| KL-01 | Taranmış (görüntü) sayfalardan metin çıkarılmıyor; sayfa `ocr_gerekli` diye işaretlenip atlanıyor | OCR hattı kurulmadı; derlemde 3 rapor `belirsiz` (Kardemir 2025 ABBYY ile taranmış) | Bu sayfalardaki açıklamalar boşluk analizine girmez; madde yanlışlıkla "eksik" çıkabilir | Türkçe OCR (Tesseract `tur`) ile ayrı hat ve QA; ölçüm S04.T5'te | Aktif |
| KL-02 | Sayfa sonunda bölünen tablo iki ayrı birim oluyor; devam birimi başlıksız | `pipelines/extract.py` sayfa sayfa çalışıyor (Derimod s. 22→23, 25→26) | Tablonun ikinci yarısı yanlış bölüme bağlanabilir | S04.T7: ardışık sayfalardaki aynı sütun yapısını birleştirme, önce kırmızı test | Aktif |
| KL-03 | Kardeş alt maddeler (`TSRS2-YON-06a` ile `TSRS2-YON-06a-iii`) taban çizgisinde ayırt edilemiyor | Benzerlik öznitelikleri iki maddeye neredeyse aynı skoru veriyor | Taban çizgisinin alt madde F1'i düşük çıkar | BERT kolu (S16) ve katalog v1 bölmesi (S02); ölçüm deney (a)'da | Planlı |
| KL-04 | İki sütunlu sayfalarda okuma sırası doğrulanmadı | Pilot raporların çoğu tek sütunlu; elle QA henüz yapılmadı (U-03) | Paragraflar karışık sırada birleşebilir | S04.T5 sonucuna göre sütun algılama | Aktif |
| KL-05 | Pilot örneklemi 100 karakterden kısa ve 1.500 karakterden uzun birimleri dışarıda bırakıyor | Kısa başlıklar ve uzun tablolar örneklemi tek başına dolduruyordu (2026-10-23) | Kısa sayısal cümleler ve uzun tablolar pilot κ'ya girmiyor; rastgele kolun kaçırılan pozitifleri ölçmesi bu filtreye koşullu | Toplu etiketlemede (S07.T5) filtre yok; tez yönteminde filtre açıkça yazılır | Aktif |
| KL-06 | Derlemin 37 raporu (TSRS öncesi şirket raporları 2022–2023) yalnızca bulut çalışma alanında | Kullanıcının makinesine aktarım yavaş; öncelik TSRS raporlarıydı | Kullanıcının makinesinde bu raporlarla çıkarım yapılamaz | İstenirse aynı aktarım yöntemiyle; SHA-256 manifestte | Aktif |
| KL-07 | Yalnızca Türkçe (`tr`) raporlar etiketlenir ve eğitime girer | [.claude/rules/turkce-tdk.md](../.claude/rules/turkce-tdk.md) derlem kuralı | İngilizce raporlar (Arçelik 2022) ve karışık raporların İngilizce paragrafları kapsam dışı | — (bilinçli tercih; D-06 İngilizce veri setleri ayrıca) | Planlı |
| KL-08 | Kullanıcının Windows makinesinde kalite kapısı ve arayüz henüz koşulmadı | Geliştirme bulut çalışma alanında (Linux, Python 3.11–3.13) | Yol, kodlama ve dosya kilidi farkları geç fark edilebilir | U-01, U-02; kılavuz [kullanim/ELLE_KONTROL_VE_PILOT.md](kullanim/ELLE_KONTROL_VE_PILOT.md) | Aktif |
| KL-09 | KAP ekleri KAP'ın kendisinden değil, fintables yansısından indirildi | KAP eki adresleri oturum ve JavaScript gerektiriyor | Kaynağın yansı olması doğrulanabilirliği azaltır | SHA-256 manifestte; tez için KAP bildirim numarası eklenir (S03.T4) | Aktif |
| KL-10 | Claude Code içinde canlı ajan yönlendirmesi ve guard'ın canlı davranışı denenmedi | Bulut çalışma alanında Claude Code oturumu açılamıyor | Yönlendirme tablosu yalnızca birim testleriyle sınandı | U-08: 6 senaryo kullanıcının makinesinde | Aktif |
| KL-11 | Arayüzde kayıtlar dosyaya yazılıyor; aynı dosyanın Excel'de açık olması kaydı engeller | Onay arayüzü veritabanı kullanmıyor (ADR-006); Windows dosyayı kilitler | Kayıt reddedilir; ekran uyarı verir, veri kaybolmaz | Kılavuzda uyarı; S10 sonrası veritabanı | Aktif |
