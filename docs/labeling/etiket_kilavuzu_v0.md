# Etiketleme Kılavuzu v0.1 (Boşluk Analizi)

Durum: **taslak, pilotta test edilecek.** Dosya adı pilot boyunca `v0` kalır; içerik v0.1'dir (§9). Aşağıdaki kararlar bir başlangıç önerisidir; pilot sonrası v1'e dönüşür. Her değişiklik sürüm notuna yazılır.

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

Bu düzeyler etiketin **çekirdeğidir**: boşluk analizi ve κ yalnızca bunlarla ölçülür. Aşağıdaki üç alan (§3a–3c) her paragraf için ayrıca kaydedilir; çekirdeği değiştirmez, kararın neden ve nasıl verildiğini analiz edilebilir kılar (ADR-013). Kodlar `data/labels/etiket_semasi.json`'dadır; doğrulayıcı ve ekranlar o dosyayı okur.

### 3a. Beyan türü (paragraf başına, en az bir tane)

Paragrafın ne tür bir açıklama yaptığı. Bir paragraf birden çok türü taşıyabilir ("2024'te %12 azalttık, 2030 hedefimiz %40" → `gerceklesen` + `hedef`).

| Kod | Ne zaman | Örnek |
|---|---|---|
| `politika` | Genel ilke, niyet, bağlılık; ölçülebilir hedef ya da sonuç yok | "Su kaynaklarının verimli kullanımını destekliyoruz." |
| `hedef` | Gelecek için tarihli ya da ölçülebilir amaç | "2030'a kadar Kapsam 1 emisyonunu %40 azaltmayı hedefliyoruz." |
| `gerceklesen` | Ölçülmüş performans ya da yapılmış iş | "2024'te Kapsam 1 emisyonumuz 12.450 tCO2e oldu." |
| `yontem` | Nasıl yapıldığı: hesaplama yöntemi, sınır, varsayım, süreç | "Emisyonlar GHG Protokolü'ne göre operasyonel kontrol yaklaşımıyla hesaplanmıştır." |
| `risk_firsat` | Risk ya da fırsatın tanımı, etkisi, senaryosu | "Kuraklık, üretim tesislerinde su temini riskini artırmaktadır." |
| `yonetisim` | Kim sorumlu, nasıl gözetiliyor, ne sıklıkla raporlanıyor | "Sürdürülebilirlik Komitesi yılda iki kez kurula sunum yapar." |
| `genel` | Şirket, rapor ya da bağlam tanıtımı; standart açısından içerik yok | "Şirketimiz 1985 yılında kurulmuştur." |

Neden gerekli: RAG taslağında hedef ile gerçekleşen sonuç karışırsa sistem şirketin hedefini başarılmış gibi yazar (kip denetimi, R-VER-03). Ayrıca yalnızca `politika` taşıyan bir paragraf çoğunlukla en fazla **1** alır; bu ilişki pilotta ölçülür.

### 3b. Kanıt cümlesi (2 ya da 1 verilen her madde için)

Ekran paragrafı numaralı cümlelere böler (tabloda satırlara). Maddeyi karşılayan cümlenin numarasını seç; birden çok cümle gerekiyorsa hepsini seç. Kural: **yalnızca o cümleler okunsa da aynı düzeyi verirdin.** U için kanıt gerekmez; gerekçe yeterlidir.

Neden gerekli: RAG'ın kaynak göstermesi ve modelin "hangi cümleye bakarak karar verdi" sorusu buna dayanır; anlaşmazlıklarda iki tarafın aynı cümleye mi baktığı görülür.

### 3c. Emin değilim ve belirsizlik nedeni

Kararından emin değilsen **Emin değilim**'i işaretle ve en az bir neden seç. Tahminini yine ver (çoğunlukla 1); belirsizlik ayrı kaydedilir, kararın yerine geçmez.

| Kod | Ne zaman |
|---|---|
| `eksik_baglam` | Karar için önceki ya da sonraki paragraf gerekiyor |
| `cikarim_hatasi` | Metin bozuk: kırık tablo, karışık sütun, eksik metin. **Madde seçme, NONE kaydet** (§5, durum 6) |
| `birden_fazla_anlam` | İki yorum da savunulabilir |
| `kilavuz_belirsiz` | Kılavuz bu durumu kapsamıyor (eski "kılavuz-belirsiz:" gerekçesinin yerini alır) |
| `yetersiz_kanit` | Madde ile bağ zayıf; 1 ile NONE arasında kaldın |

Ekran ayrıca paragraf başına süreyi kendiliğinden tutar (ilk görünüşten kayda kadar). Süre etiketleme maliyetini raporlamak içindir; hız için acele etme.

Değer, birim, dönem ve hedef yılı **elle girilmez**: sayılar `report_service.verify.numbers` ile otomatik çıkarılır ve taslak doğrulamasında (S18) insan onayından geçer.

Rapor düzeyi sonuç ayrıca tutulur: bir madde için hiçbir paragraf 1 veya 2 almadıysa madde **0 (Eksik)** olur. 0 kodu paragraf düzeyinde verilmez; 5. bölümdeki ikinci geçişle doğrulanır.

## 4. Karar adımları

Her paragraf için sırayla:

1. Paragrafın konusu hangi maddelerin başlığıyla örtüşüyor? (Katalogda `baslik` ve `gereklilik_ozeti` sütunlarına bak.)
2. Madde birden çok unsur içeriyorsa (örneğin Kapsam 1, 2 ve 3), paragraf kaç unsuru karşılıyor?
3. Karşılanan unsurlar şirkete özgü ve somut mu, yoksa herhangi bir şirketin yazabileceği genel bir cümle mi?
4. Sayısal ise: değer, birim ve dönem var mı?
5. Tümü evet ise **2**, bir kısmı evet ise **1**.
6. Emin değilsen **1** ver, **Emin değilim**'i işaretle ve nedenini seç (§3c). İstersen `gerekce` alanına serbest not ekle.
7. 2 ya da 1 verdiğin her madde için kanıt cümlesini seç (§3b); paragrafın beyan türünü işaretle (§3a).

## 5. Sınır durumlar (pilotta karara bağlanacak)

| # | Durum | Önerilen geçici kural |
|---|---|---|
| 1 | Rapor bir muafiyet kullandığını açıkça belirtiyor (örneğin Kapsam 3'ün geçiş hükmü nedeniyle açıklanmadığı) | İlgili unsur karşılanmış sayılır, `gerekce` alanına "muafiyet beyanı" yazılır. **Açık soru:** bu doğru mu? Hocayla netleştirilmeli. |
| 2 | Koşullu madde (örneğin geçiş planı) için "planımız yoktur" ifadesi | U (uygulanamaz) değil, 2 sayılır. Madde, durumun açıklanmasını istiyorsa ve açıklama varsa karşılanmıştır. **Açık soru.** |
| 3 | Çapraz atıf ("Ayrıntılar için bkz. sayfa 40") | Atıf yapılan içerik etiketlenir. Atıf paragrafı o madde için NONE sayılır. |
| 4 | Aynı bilgi raporun birden çok yerinde | Hepsi etiketlenir. Madde durumu en yüksek düzeydir. |
| 5 | Dönem belirtilmemiş sayı | 1. |
| 6 | Kaynak PDF'ten bozuk çıkmış paragraf (kırık tablo, karışık sütun) | Madde seçme; belirsizlik nedeni `cikarim_hatasi`, NONE kaydet. Bunlar PDF işleme hata analizine gider. |
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
- v0.1 (2026-10-23, pilot başlamadan): §3a beyan türü, §3b kanıt cümlesi, §3c emin değilim ve belirsizlik nedeni eklendi; çekirdek (§3) değişmedi. Karar: ADR-013. Şema sürümü `etiket-0.1`.
