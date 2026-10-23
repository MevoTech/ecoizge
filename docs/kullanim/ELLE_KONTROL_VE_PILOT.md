# Elle Kontrol ve Pilot Etiketleme Kılavuzu (Mehmet için)

Bu kılavuz senin yapacağın dört işi adım adım anlatır: kurulum (U-01), arayüzü açma (U-02), çıkarım kontrolü (U-03) ve kör etiketleme (U-04). Plan karşılıkları:
- U-01 ve U-02: S07.T3;
- U-03: S04.T4;
- U-04: S05.T3.

Durum [../PROGRESS.md](../PROGRESS.md) §2.1'de izlenir.

| İş | Süre (tahmin) | Çıktı |
|---|---|---|
| 1. Kurulum | yapıldı (2026-10-23) | Depo ve Python ortamı |
| 2. Arayüzü açma | 2 dk | Tarayıcıda "EcoIzge · Çalışma ekranları" |
| 3. Çıkarım kontrolü | 20 sayfa × 2–3 dk ≈ 1 saat | `reports/experiments/extraction-qa-elle.csv` |
| 4. Kör etiketleme | 50 paragraf × 3–5 dk ≈ 3–4 saat | `data/labels/blind/mehmet-gunes/pilot_v0.csv` + `pilot_v0.paragraf.jsonl` |

İşleri istediğin kadar parçaya bölebilirsin. Her kayıt anında diske yazılır; arayüzü kapatıp açınca kaldığın yerden devam edersin.

## 1. Kurulum (U-01): yapıldı

Kurulum 2026-10-23'te senin bilgisayarında yapıldı ve kalite kapısı orada da 6/6 geçti (PROGRESS §4):
- **Anaconda ortamı:** `ecoizge` (Python 3.11, git, poppler).
- **Depo:** `C:\Users\mevog\Documents\ecoizge`.

Güncellemek ya da yeniden kurmak için `C:\Users\mevog\Documents\ecoizge\tools\windows\kurulum.bat` dosyasına çift tıkla. Pencere bitince sonucu yazar; ayrıntı aynı klasördeki `kurulum.log`'dadır.

> Dosya Gezgini'nin sol menüsündeki "Documents" kısayolu bu bilgisayarda başka bir klasörü (OneDrive) gösteriyor. Depoyu orada arama; adres çubuğundaki yol `C:\Users\mevog\Documents` olmalı.

Rapor PDF'leri `C:\Users\mevog\Documents\ecoizge-raporlar` klasöründe; arayüz onları kendiliğinden bulur.

## 2. Arayüzü açma (U-02)

`C:\Users\mevog\Documents\ecoizge\tools\windows\arayuz.bat` dosyasına çift tıkla.
- Siyah bir pencere açılır; arayüz çalıştığı sürece **o pencereyi kapatma**.
- Birkaç saniye sonra tarayıcıda `http://localhost:8501` açılır. Açılmazsa adresi elle yaz.
- İşin bitince siyah pencereyi kapat.
- Güncellemeden sonra (ya da ekran garip davranırsa) `arayuz.bat`'a yeniden çift tıkla: açık olan eski arayüzü kapatıp yenisini açar.

Elle açmak istersen Anaconda Prompt'ta:
```
conda activate ecoizge
cd %USERPROFILE%\Documents\ecoizge
streamlit run services/review-ui/app.py
```

**Başlangıç** ekranında:
1. Sol menüdeki kutuya **adını soyadını** yaz (ör. `Mehmet Güneş`). Ad bir kez yazılınca diğer ekranlarda da dolu gelir.
2. "Hazırlık denetimi"nde dört satırın hepsi ✅ olmalı:
   - pilot örneklemi (50 paragraf);
   - pilot raporlarının birimleri (4 rapor);
   - PDF klasörü;
   - ad.

   ⚠️ olan satır varsa ne yazdığını bana gönder.

## 3. Çıkarım kontrolü (U-03)

Amaç: PDF'ten çıkarılan metnin doğru olup olmadığını ölçmek. Bu sayı tezde "çıkarım hata oranı" olarak raporlanır (R-PDF-02).

1. Sol menüden **1 · Çıkarım kontrolü**.
2. Sol menüden **rapor** seç (4 rapor), sonra **sayfa** seç (her raporda 5 sayfa).
   - Kaydedilen sayfanın yanında ✓ çıkar.
   - Üstteki çubuk toplam ilerlemeyi gösterir (20 sayfa).
3. Ekranın solunda PDF sayfasının görüntüsü, sağında o sayfadan çıkarılan birimler (paragraf ve tablolar) var. İkisini karşılaştır.
4. Gördüğün hataları işaretle:

   | İşaret | Ne zaman |
   |---|---|
   | Eksik metin | PDF'te okunabilir bir paragraf ya da tablo var, sağda yok |
   | Fazla metin | Sağda sayfada olmayan ya da iki kez geçen metin var |
   | Kırık tablo | Tablo hücreleri kaymış, satırlar ya da sütunlar karışmış |
   | Sütun karışması | İki sütunlu sayfada iki sütunun cümleleri iç içe geçmiş |
   | Yanlış bölüm başlığı | Birimin "başlık" alanı sayfadaki bölüm başlığıyla uyuşmuyor |
   | Türkçe harf kaybı | ş, ı, ğ, İ yerine `·`, boşluk ya da başka harf |
   | Üst/alt bilgi kalmış | Sayfa numarası, rapor adı gibi tekrar eden satırlar birimin içinde |
   | Bölünmüş ya da birleşmiş paragraf | Tek paragraf ikiye bölünmüş ya da iki paragraf birleşmiş |

5. Hata işaretlediysen **Not** kutusuna ne gördüğünü bir cümleyle yaz (zorunlu). Örnek: "Tablonun 3. sütunu bir sonraki satıra kaymış."
6. Hata yoksa hiçbir şey işaretlemeden **Kaydet**.

**Özel durumlar:**
- **"Bu sayfadan çıkarılan birim yok"** uyarısı çıkarsa:
  - PDF sayfasında okunabilir metin varsa **Eksik metin** işaretle ve not yaz;
  - sayfa yalnızca görsel, kapak ya da boşsa hiçbir şey işaretleme.
- **Tablo sayfa sonunda bölünmüşse** (ikinci yarısı sonraki sayfada, başlıksız): bu bilinen bir hatadır (KL-02). Yine de **Kırık tablo** işaretle; ölçüm için önemli.
- Kararsız kaldığın sayfada işaretle ve notta "emin değilim" yaz.

Fikrini değiştirirsen sayfaya geri dön, düzelt ve tekrar **Kaydet**. Önceki kayıt değişir, yeni satır eklenmez.

## 4. Kör etiketleme (U-04)

Amaç: 50 paragrafın her birinin hangi TSRS/VSME maddesini ne ölçüde karşıladığını, **modelin önerisini görmeden** belirlemek. Senin etiketlerin ile modelin önerileri karşılaştırılıp uyum (κ) ölçülür (R-ETK-01). Bu yüzden:
- **Etiketleme bitene kadar "3 · Etiket onayı" ekranına girme.** Ekran pilot önerilerini zaten gizler; yine de girme.
- Etiket dosyasını başka programda açma ve elle düzenleme. Excel'de açık kalırsa kayıt reddedilir ve uyarı çıkar (KL-11).

**Adımlar** (her paragraf için aynı sıra; kılavuz §3–3c):
1. Sol menüden **2 · Kör etiketleme**. İlk açılışta "Nasıl karar veririm?" kutusu açık gelir; bir kez oku.
2. Paragraf **numaralı cümleler** hâlinde görünür ([1], [2] …; tabloda her satır bir numara). Üstte rapor, sayfa, bölüm ve tür yazar.
3. **Beyan türü:** paragraf ne söylüyor? Politika, hedef, gerçekleşen sonuç, yöntem, risk/fırsat, yönetişim ya da genel bilgi. Birden çok seçebilirsin; en az biri zorunlu.
   - Örnek: "2024'te %12 azalttık, 2030 hedefimiz %40" → gerçekleşen sonuç + hedef.
4. **Maddeler:** "Bu paragraf hangi maddeleri karşılıyor?" listesinden seç.
   - Listeyi **Standart**, **Bölüm** ya da **Ara** kutusuyla daraltabilirsin (ör. "gözetim", "kapsam 1", "iklim"). Filtre seçimini silmez.
   - Bir paragraf birden çok maddeyi karşılayabilir; hepsini seç.
5. **Düzey:** her madde için seç. Varsayılan seçili değildir.
   - **2 · Tam:** istenen unsurların tamamı var, şirkete özgü ve somut. Sayısal maddede değer + birim + dönem.
   - **1 · Kısmi:** konuya değiniyor ama unsur eksik ya da ifade genel ("düzenli olarak bilgilendirilir").
   - **U · Uygulanamaz:** rapor, maddenin uygulanmadığını gerekçesiyle söylüyor. U için gerekçe zorunlu.
6. **Kanıt cümlesi:** 2 ya da 1 verdiğin her madde için o maddeyi karşılayan cümle numaralarını seç. Kural: yalnızca o cümleleri okusan da aynı düzeyi verirdin.
7. **Emin değilim:** kararından emin değilsen işaretle ve nedenini seç (neden seçmek de "emin değilim" sayılır):
   - eksik bağlam;
   - çıkarım hatası;
   - birden fazla anlam;
   - kılavuz belirsiz;
   - yetersiz kanıt.

   Tahminini yine ver (çoğunlukla 1).
8. Hiçbir maddeyle ilgisi yoksa madde seçme; düğme **"Kaydet: NONE"** olur, bu da bir karardır. Beyan türü yine seçilir (çoğunlukla "genel bilgi").
9. Çıkarım bozuksa (kırık tablo, anlamsız metin) madde seçme. Nedenlerden **Çıkarım hatası**'nı seç ve NONE kaydet; beyan türünü boş bırakabilirsin.
10. **Kaydet**. Eksik bir alan varsa ekran kırmızı kutuyla söyler. Kayıttan sonra sıradaki paragrafa geçilir. Ekran paragraf başına süreyi kendisi tutar (yalnızca o paragraf ekrandayken); acele etme, ara verirken paragrafı açık bırakman da sorun değil.

Geri dönüp düzeltmek için sol menüdeki **Paragraf sırası** kutusuna numarayı yaz. Önceki seçimlerin gelir; değiştirip yeniden kaydedersin.

**Kılavuz:** ayrıntılı kurallar ve örnekler [../labeling/etiket_kilavuzu_v0.md](../labeling/etiket_kilavuzu_v0.md)'dedir (v0.1). En sık karışanlar:
- "Şirketimiz iklim konularında yönetim kurulunu düzenli olarak bilgilendirmektedir" en fazla **1**'dir: yöntem ve sıklık yok. Beyan türü: yönetişim.
- Dönemsiz sayı en fazla **1**'dir. Yıl bölüm başlığında geçiyorsa (ör. "2024 Performans Göstergeleri") dönem var sayılır.
- "Ayrıntılar için bkz. s. 40" gibi atıf paragrafı **NONE**'dur.
- Kılavuzun çözemediği durumda en iyi tahminini ver, **Emin değilim** + **Kılavuz belirsiz** seç. Bu kayıtlar kılavuz v1'in girdisidir.

**İlerlemeyi görmek:** **4 · Analiz** ekranı şunları gösterir:
- çıkarım hata türleri;
- düzey, beyan türü ve belirsizlik dağılımları;
- rapor bazında sayılar;
- medyan süre.

Paragraf tablosunu CSV olarak indirebilirsin (Excel'de çift tıklayınca sütunlara ayrılır). Analiz ekranı, kutusuna yazılan adın kayıtlarını gösterir; ad diğer ekranlardan kendiliğinden gelmez. Arayüzde kimlik doğrulama yoktur: aynı bilgisayarı ikinci bir etiketleyici kullanacaksa önce bana haber ver (KL-12).

**Uyum (κ) ve kilit:** pilot bitip model önerileri üretilince κ bu ekranda görünür. κ ya da model önerisi **bir kez gösterilince kör etiketlerin donar**; ekran değişikliğe izin vermez. Bu yüzden "bitti" demeden önce düzeltmek istediğin paragraf varsa düzelt.

## 5. Bitince

Sol menüde "Pilot bitti" yazısı çıkınca bana **"bitti"** yaz. İki dosyanı bilgisayarındaki depodan okurum, ayrıca bir şey göndermen gerekmez:
- `C:\Users\mevog\Documents\ecoizge\data\labels\blind\mehmet-gunes\pilot_v0.csv`
- `C:\Users\mevog\Documents\ecoizge\data\labels\blind\mehmet-gunes\pilot_v0.paragraf.jsonl`
- `C:\Users\mevog\Documents\ecoizge\reports\experiments\extraction-qa-elle.csv`

İstersen depoya da gönder:
```
git add data/labels/blind reports/experiments/extraction-qa-elle.csv
git commit -m "Pilot: kör etiketler ve çıkarım kontrolü" -m "Refs: S04.T4, S05.T3"
git push
```

Sonra ben şunları yaparım:
1. Modelin önerilerini (senin etiketlerini görmeden) üretirim.
2. κ'yı ve anlaşmazlık listesini çıkarırım.
3. Kılavuz v1 önerisini sana onaya getiririm.

## 6. Sorun giderme

| Belirti | Çözüm |
|---|---|
| `arayuz.bat` açılıp hemen kapanıyor | `tools\windows\kurulum.bat`'ı çalıştır; sonuç TAMAM değilse `kurulum.log`'u bana gönder |
| `conda` ya da `streamlit` tanınmıyor | Komutları **Anaconda Prompt**'ta, `conda activate ecoizge`'den sonra çalıştır |
| "PDF bulunamadı" | PDF'ler başka klasördeyse Anaconda Prompt'ta `set ECOIZGE_RAPOR_DIR=C:\yol\ecoizge-raporlar`, sonra `streamlit run …` |
| "… başka bir programda açık (Excel?)" | Dosyayı Excel'de kapat, **Kaydet**'e yeniden bas. Kaydın kaybolmaz |
| "Pilot örneklem değişmiş" | Hiçbir şeye dokunma, bana yaz. Örneklem etiketleme başladıktan sonra değiştirilmez |
| Sayfa kırmızı hata kutusu gösteriyor | Kutudaki metnin ekran görüntüsünü bana gönder |
| `git pull` sonrası ekran değişti | Normal: düzeltme gelmiştir. Kayıtların dosyada durur |
