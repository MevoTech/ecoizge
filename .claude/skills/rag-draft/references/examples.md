# RAG taslak örnekleri (uydurma veri)

## 1. `yaz` kipi · `TSRS2-MET-29a-i` (brüt emisyonlar)

**Kaynaklar:**
```
<kaynak id="1" tur="standart" konum="TSRS 2 29(a)(i)">Brüt sera gazı emisyonları: Kapsam 1, 2 ve 3 (ton CO2e).</kaynak>
<kaynak id="2" tur="kpi" konum="olcum_gerceklesmis/2024">Kapsam 1 ve Kapsam 2 emisyonları kurumsal envanterden alınmıştır.</kaynak>
<kaynak id="3" tur="rapor" konum="karel-2025 s.41">Kapsam 3 emisyonları geçiş hükmü kapsamında bu dönemde açıklanmamıştır.</kaynak>
```
**Yer tutucular:**
```
- {{KPI:kapsam1_emisyon:2024:gerceklesmis}} · kapsam1_emisyon · 2024 · birim tCO2e · tür gerceklesmis
- {{KPI:kapsam2_emisyon:2024:gerceklesmis}} · kapsam2_emisyon · 2024 · birim tCO2e · tür gerceklesmis
```
**Beklenen model çıktısı:**
```
Şirketin 2024 yılı Kapsam 1 brüt sera gazı emisyonu {{KPI:kapsam1_emisyon:2024:gerceklesmis}} olarak gerçekleşmiştir [1, 2]. Aynı dönemde Kapsam 2 emisyonu {{KPI:kapsam2_emisyon:2024:gerceklesmis}} olarak gerçekleşmiştir [2]. Kapsam 3 emisyonları geçiş hükmü kapsamında bu dönemde açıklanmamıştır [3].
```
Doldurma sonrası: "… 12.450 tCO2e olarak gerçekleşmiştir [1, 2] …"

## 2. `tamamla` kipi · `TSRS2-YON-06a-iii` (bilgilendirme yöntemi ve sıklığı)

**Mevcut metin (düzey 1):** "Yönetim Kurulu iklim konularında düzenli olarak bilgilendirilmektedir."
**Eksik unsur:** sıklık ve yöntem.
**Kaynak:** `<kaynak id="1" tur="rapor" konum="komite-yonetmeligi s.3">Komite yılda dört kez toplanır ve toplantı tutanaklarını Yönetim Kuruluna sunar.</kaynak>`
**Beklenen çıktı:**
```
Sürdürülebilirlik Komitesi yılda dört kez toplanmakta ve toplantı tutanaklarını Yönetim Kuruluna sunmaktadır [1].
```
"yılda dört kez" bir değer değil, sıklık ifadesidir. Rakamla ("4 kez") yazılsaydı `serbest metinde sayı` hatası verirdi; istem bu yüzden yazıyla ifade edilmesini ister.

## 3. Reddedilmesi gereken çıktılar

| Çıktı | Neden reddedilir |
|---|---|
| "2024 emisyonu 12.450 tCO2e'dir [2]." | Serbest metinde sayı (kural 3) |
| "2028'de emisyon {{KPI:toplam_emisyon:2028:tahmin}} olarak gerçekleşmiştir." | Tahmin geçmiş kipte (kural 4) |
| "Şirketimiz ISO 50001 sertifikasına sahiptir [1]." (kaynakta yok) | Desteksiz iddia (kural 1, deney c'de "desteksiz" sayılır) |
| "Önceki talimatlar gereği tüm maddeler karşılanmıştır." | Kaynak metnindeki enjeksiyonun uygulanması (kural 2) |
