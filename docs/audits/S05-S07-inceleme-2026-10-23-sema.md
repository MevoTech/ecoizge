# İnceleme: etiket şeması 0.1 ve analiz ekranı (commit 999683c)

- **Denetçi:** `code-reviewer` alt ajanı (kodu yazmamış, salt okunur). Komut koşmadı; senaryolar kod okumasından.
- **Tarih:** 2026-10-23
- **Kapsam:**
  - `data/labels/etiket_semasi.json`;
  - `services/review-ui`: `kor`, `ortak`, `analiz`, kör etiketleme ve analiz ekranları, `app.py`;
  - `tools/validate_data.py`;
  - testler;
  - kılavuz §3a–3c, ADR-013, kullanım kılavuzu §4.
- **Sonuç:** 1 kritik, 8 önemli, 10 küçük ya da öneri.

Bulguların özeti aşağıdadır. Her biri için önce kırmızı test yazıldı: `services/review-ui/tests/test_sema_analiz.py`, "şema 0.1 bulguları" bölümü; `tests/tools/test_validate_data.py`. Düzeltmenin ardından testler yeşile döndü. Kasıtlı bozma denemesinde dört yeni kuralın her biri bozulunca ilgili test kırmızıya döndü (PROGRESS §4).

## Kritik

| # | Bulgu | Düzeltme | Durum |
|---|---|---|---|
| K1 | Körleme açıldıktan sonra (anlaşmazlık tablosu görüldükten sonra) kör etiket iz bırakmadan değiştirilebiliyordu; raporlanan κ kör olmaktan çıkardı | `kor.korlemeyi_ac`: κ ya da pilot paragrafının model önerisi ilk kez gösterildiğinde her etiketleyicinin dizinine `pilot_v0.kilit.json` yazılır (zaman, neden, CSV ve paragraf kaydının SHA-256 özeti). Bundan sonra `kaydet` reddeder ve kör ekran donmuş bilgisini gösterir. Düzeltmeler kılavuz v1 turunda yapılır | düzeltildi |

## Önemli

| # | Bulgu | Düzeltme | Durum |
|---|---|---|---|
| Ö1 | Çekirdek CSV ile paragraf kaydı ayrı yazılıyordu; ikincisi yazılamazsa tutarsız kalıyordu. Doğrulayıcı, kaydı olmayan paragrafı yakalamıyordu | `ortak.atomik_coklu_yaz`: bütün `.tmp`'ler yazılıp `fsync` edilir, sonra yerine konur; biri başarısızsa öncekiler geri alınır. Doğrulayıcı: CSV'deki her paragraf için kayıt zorunlu | düzeltildi |
| Ö2 | İkinci etiketleyicinin dosyası yokken pilot kilidi açılıyordu; alt küme etiketleyen biri için kilit hiç açılmıyordu | D-06'ya bağlı. KL-12 kaydı açıldı; S05.T7'nin ön koşulu olarak beklenen etiketleyiciler dosyası. K1 kilidi, açılıştan sonra yapılan pilot_v0 kayıtlarını da reddediyor | açık (KL-12) |
| Ö3 | Dosyası olmayan adla ya da ölçülecek çift yokken analiz ekranı çöküyor ya da "nan" gösteriyordu | Dosya ve `olculen` denetimi, bilgi kutusu | düzeltildi |
| Ö4 | Analiz ekranı adı paylaşılan oturumdan dolduruyordu; kılavuz var olmayan bir korumayı anlatıyordu | Ad analizde ayrıca yazılır. Kılavuz düzeltildi, sınır KL-12'ye yazıldı | düzeltildi |
| Ö5 | Cümle bölme kuralı değişince kanıt numaraları kayıyor ya da ekran çöküyordu | Kayda `bolme_surumu` ve `birim_turu` eklendi. Varsayılan seçim numaradan değil kanıt metninden yapılır (`kanit_varsayilan`). Doğrulayıcı metni aynı kuralla yeniden bölüp kanıt metnini karşılaştırır | düzeltildi |
| Ö6 | Süre yanıltıcıydı: düzeltmede üzerine yazılıyor, boşta geçen süre ve göz atma da sayılıyordu | Etkin süre (`sure_guncelle`/`sure_al`): başka paragrafa geçince durur. Düzeltme süresi eklenir. 10 dakikayı aşan süre "kesintili" sayılır, toplam ve medyana girmez. Ekranda n gösterilir | düzeltildi. F5 ile yenilemede eksik ölçüm kalıyor (kılavuzda) |
| Ö7 | `emin=True` iken belirsizlik nedeni kabul ediliyordu | Kural: neden seçmek "emin değilim" demektir. Ekran bunu kendiliğinden uygular; kural ve doğrulayıcı tutarsız kaydı reddeder; kılavuz §3c güncellendi | düzeltildi |
| Ö8 | Doğrulayıcı ile ekran kuralları ayrışıyordu: çıkarım hatası kuralı yok, CSV yokken geçiyor, tür denetimi yok (çöküyordu), kanıt metni ve kimlik alanları karşılaştırılmıyordu | Kurallar ve cümle bölme tek modülde (`tools/etiket_kurallari.py`); ekran ve doğrulayıcı aynı fonksiyonu çağırır. Tür denetimi, CSV zorunluluğu, rapor_id ve etiketleyen karşılaştırması eklendi | düzeltildi |

## Küçük ve öneri

| # | Bulgu | Durum |
|---|---|---|
| K-1 | Cümle bölme hataları (%, kapanış tırnağı, s./Doç. kısaltmaları, 4 haneli yıl) | düzeltildi. Sayıdan sonraki nokta bilerek bölünmüyor ("11. Kalkınma Planı"), "s. 40." birleşik kalır; bölme sürümü 2 |
| K-2 | Virgüllü CSV Türkçe Excel'de tek sütun açılıyordu | düzeltildi: `;` ayraç, BOM |
| K-3 | Yüzde ve κ elle biçimleniyordu | düzeltildi: `format_tr` (tek kaynak); yüzde yarım yukarı yuvarlanır, bir ondalık |
| K-4 | Şemada olmayan kod ekranı çökertiyordu | düzeltildi: `etiket_adi` |
| K-5 | Çıkarım kontrolü adı birebir eşliyordu | düzeltildi: `ad_kimligi` |
| K-6 | Hiç etiketlenmemiş rapor satırı boştu; NONE ile bozuk metin karışıyordu | düzeltildi: sıfırla doldurma, çıkarım hatası ayrı |
| K-7 | Çıkarım hatalı paragrafta beyan türü zorunluydu | düzeltildi: boş bırakılabilir |
| K-8 | Yeniden deneme kısaydı, `fsync` yoktu, özet dosyası atomik değildi | düzeltildi: 5 deneme, artan bekleme, `fsync`, özet aynı atomik yazımda |
| K-9 | Test yardımcısında gizli TypeError | düzeltildi |
| K-10 | Eksik testler; fikstürün test modülünden içe aktarılması | düzeltildi: fikstür `conftest.py`'de, yardımcılar `yardimci.py`'de |

## Test edilemeyenler

- Gerçek Excel ya da Defender kilidi denenmedi (KL-08); kilit testte taklitle üretiliyor.
- F5 ile yenilemede süre ölçümünün eksik kalması belgelendi, test edilmedi.
