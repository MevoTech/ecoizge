# Etiketleme Kılavuzu v0 (Boşluk Analizi)

Durum: **taslak, pilotta test edilecek.** Aşağıdaki kararlar bir başlangıç önerisidir; pilot sonrası v1'e dönüşür. Her değişiklik sürüm notuna yazılır.

## 1. Amaç

Bir şirket raporundaki paragrafların, `catalog_v0.csv` içindeki hangi maddeleri ne ölçüde karşıladığını belirlemek. Etiketler iki iş için kullanılır:

1. Boşluk analizi sınıflandırıcısının eğitimi ve değerlendirilmesi (precision, recall, F1).
2. RAG taslak üretiminde "bu madde raporda eksik" kararının doğruluğunun ölçülmesi.

Etiketleyen, **bilginin raporda bulunup bulunmadığını** değerlendirir. Şirketin sürdürülebilirlik performansını, verinin doğruluğunu veya mevzuata uyumunu değerlendirmez.

## 2. Etiketleme birimi

- Birim, rapordan çıkarılmış bir **paragraf**tır (başlık dahil bağlam: sayfa ve bölüm başlığı yanında verilir).
- Bir **tablo**, başlığıyla birlikte tek birim sayılır.
- Bir paragraf birden çok maddeyle ilişkili olabilir. Her ilişki ayrı satırdır (paragraf × madde).
- Hiçbir maddeyle ilgisi olmayan paragraf tek satırla `madde_id = NONE` olarak kaydedilir. Böylece paragrafın incelendiği bilinir.

## 3. Karşılama düzeyleri (paragraf × madde)

| Kod | Ad | Ölçüt |
|---|---|---|
| 2 | Tam | Paragraf, maddenin istediği unsurların **tamamını** şirkete özgü, somut içerikle verir. Sayısal maddelerde değer, birim ve dönem vardır. |
| 1 | Kısmi / yüzeysel | Konuya değinir ama (a) bir veya daha fazla zorunlu unsur eksiktir, ya da (b) ifade genel ve şirkete özgü değildir, ya da (c) sayısal veride birim, dönem veya kapsam eksiktir. |
| U | Uygulanamaz | Koşullu bir madde için rapor, uygulanamaz olduğunu **gerekçesiyle** belirtir. |
| NONE | İlgisiz | Paragraf bu maddeyle ilgili değildir (paragraf düzeyinde, çoğunlukla satır olarak yazılmaz; yalnızca hiçbir maddeyle ilişkisi yoksa tek satır). |

Rapor düzeyi sonuç ayrıca tutulur: bir madde için hiçbir paragraf 1 veya 2 almadıysa madde **0 (Eksik)** olur. 0 kodu paragraf düzeyinde verilmez; 5. bölümdeki ikinci geçişle doğrulanır.

## 4. Karar adımları

Her paragraf için sırayla:

1. Paragrafın konusu hangi maddelerin başlığıyla örtüşüyor? (Katalogda `baslik` ve `gereklilik_ozeti` sütunlarına bak.)
2. Madde birden çok unsur içeriyorsa (örneğin Kapsam 1, 2 ve 3), paragraf kaç unsuru karşılıyor?
3. Karşılanan unsurlar şirkete özgü ve somut mu, yoksa herhangi bir şirketin yazabileceği genel bir cümle mi?
4. Sayısal ise: değer, birim ve dönem var mı?
5. Tümü evet ise **2**, bir kısmı evet ise **1**.
6. Emin değilsen **1** ver ve `gerekce` alanına kısaca nedenini yaz. Gerekçe, kılavuzun hangi noktasının belirsiz olduğunu gösterir.

## 5. Sınır durumlar (pilotta karara bağlanacak)

| # | Durum | Önerilen geçici kural |
|---|---|---|
| 1 | Rapor bir muafiyet kullandığını açıkça belirtiyor (örneğin Kapsam 3'ün geçiş hükmü nedeniyle açıklanmadığı) | İlgili unsur karşılanmış sayılır, `gerekce` alanına "muafiyet beyanı" yazılır. **Açık soru:** bu doğru mu? Hocayla netleştirilmeli. |
| 2 | Koşullu madde (örneğin geçiş planı) için "planımız yoktur" ifadesi | U (uygulanamaz) değil, 2 sayılır. Madde, durumun açıklanmasını istiyorsa ve açıklama varsa karşılanmıştır. **Açık soru.** |
| 3 | Çapraz atıf ("Ayrıntılar için bkz. sayfa 40") | Atıf yapılan içerik etiketlenir. Atıf paragrafı o madde için NONE sayılır. |
| 4 | Aynı bilgi raporun birden çok yerinde | Hepsi etiketlenir. Madde durumu en yüksek düzeydir. |
| 5 | Dönem belirtilmemiş sayı | 1. |
| 6 | Kaynak PDF'ten bozuk çıkmış paragraf (kırık tablo, karışık sütun) | Etiketleme; `gerekce` alanına "çıkarım hatası" yazıp ayrı listele. Bunlar PDF işleme hata analizine gider. |
| 7 | Tarihsel olay anlatan ama standardın istediği içeriği taşımayan paragraf | NONE. |

Pilotta en çok ayrışan durumlar bu tabloya eklenir.

## 6. Örnekler (UYDURMA, yalnızca kılavuzu açıklamak için)

**TSRS2-YON-06a-iii** (organın nasıl ve ne sıklıkta bilgilendirildiği):

- "Sürdürülebilirlik Komitesi iklim konularında yönetimden üç ayda bir yazılı rapor alır ve yılda iki kez Yönetim Kurulu'na sunum yapar." → **2**. Hem yöntem hem sıklık var.
- "Yönetim Kurulu iklim konularında düzenli olarak bilgilendirilmektedir." → **1**. Sıklık ve yöntem belirsiz.
- "Şirketimiz sürdürülebilirliğe büyük önem vermektedir." → **NONE**. Bilgilendirmeyle ilgili hiçbir unsur yok.

**TSRS2-MET-29a-i** (brüt emisyonlar, Kapsam 1-2-3):

- "2024'te Kapsam 1 emisyonumuz 12.450 tCO2e, Kapsam 2 (lokasyon bazlı) emisyonumuz 31.200 tCO2e'dir." → **1**. Kapsam 3 yok.
- Aynı cümle + "Kapsam 3 emisyonları geçiş hükmü kapsamında bu dönemde açıklanmamıştır." → **2** (5. bölüm, kural 1'e göre; açık soru).
- "Emisyonlarımız bir önceki yıla göre azalmıştır." → **1**. Sayı, birim ve kapsam yok.

## 7. Süreç

1. **Pilot (yaklaşık 50 paragraf).** İki etiketleyici (sen ve ben) birbirinin etiketini görmeden etiketler. Örnekleme: yaklaşık 30 paragraf anahtar kelime veya benzerlikle seçilen aday paragraflardan, yaklaşık 20 paragraf rastgele. Rastgele örnekleme tek başına çok az pozitif üretir, çünkü paragrafların çoğu hiçbir maddeyle ilgili değildir.
2. **Uyum ölçümü.** Ordinal etiketler için ağırlıklı Cohen's κ (kareli ağırlık) ve ayrışan örneklerin listesi. 50 paragraf κ için küçüktür; pilotun amacı κ değeri değil, kılavuzdaki belirsizlikleri bulmaktır.
3. **Kılavuz v1.** Ayrışan örnekler tartışılır, 5. bölüm güncellenir.
4. **Toplu ön etiketleme.** Kalan paragrafları model (ben) etiketler: etiket, güven puanı ve en fazla iki cümlelik gerekçeyle. `kaynak = model_onerisi`.
5. **İnsan incelemesi.** Mehmet şunları inceler: tüm düşük güvenli öneriler, 2 ile 1 arasında kararsız olanlar, ve kalanlardan rastgele %20. Onaylanan satırlar `kaynak = insan_onayli` olur.
6. **İkinci geçiş (eksik doğrulama).** Rapor düzeyinde 0 çıkan her madde için tüm rapor madde odaklı taranır; hiçbir yerde karşılığı yoksa `tur = rapor_duzeyi`, `karsilama = 0` satırı yazılır.
7. **Altın test kümesi.** Test için ayrılan raporların tamamı insanca doğrulanır ve **dondurulur**. Bu küme prompt, eşik veya model ayarı için kullanılmaz; yalnızca nihai ölçümde açılır.

## 8. Bilmen gereken yöntem sınırları

- Etiketleyen modelin kendisi, değerlendirilen sistemlerin bir kısmıdır (özellikle LLM tabanlı adımlar). Altın kümenin insan onaylı olması bu yüzden şarttır.
- Pilotta ölçülen κ, insan ile model arasındaki uyumdur; iki bağımsız insanın uyumu değildir. Tezde bu ayrım açıkça yazılmalıdır. Küçük bir alt kümeyi (30-50 paragraf) ikinci bir insana etiketletmek savunmayı güçlendirir.
- Veri bölünmesi **rapor veya şirket bazında** yapılır. Aynı raporun paragrafları hem eğitimde hem testte olmaz.

## 9. Sürüm notları

- v0 (2026-10-22): ilk taslak.
