# Karar Kayıtları (ADR)

Biçim: `adr` skill'i. Eski kayıt silinmez; yerine yenisi gelirse "yerini aldı" diye işaretlenir.

## ADR-001 · Tek ana ajan: engineering-orchestrator
Tarih: 2026-10-22 · Durum: kabul · Karar sahibi: Mehmet Güneş
Bağlam: Kullanıcı kuralı 1; v0'da orkestratör yalnızca CLAUDE.md'de tanımlıydı (Denetim Ç1).
Seçenekler: (A) CLAUDE.md'de tarif · (B) `.claude/agents/engineering-orchestrator.md` + `settings.json` `"agent"` ile ana oturum ajanı.
Karar: B.
Sonuçlar: Ana oturum bu ajan olarak açılır. Geri alma: `settings.json`'dan `agent` anahtarını kaldırmak.

## ADR-002 · Koordinasyon yalnızca orkestratör üzerinden
Tarih: 2026-10-22 · Durum: kabul · Karar sahibi: Mehmet Güneş
Bağlam: Claude Code'da alt ajanlar varsayılan olarak alt ajan başlatabiliyor (Subagents belgesi, "Nesting rules"); kullanıcı kuralı 9.
Karar: Hiçbir alt ajanın `tools` listesinde `Agent` yok; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`.
Sonuçlar: Alt ajanlar ihtiyaçlarını raporla orkestratöre bildirir. `tools/check_consistency.py` denetler.

## ADR-003 · Yazma alanları kanca ile zorlanır
Tarih: 2026-10-22 · Durum: kabul · Karar sahibi: Mehmet Güneş
Bağlam: Talimat tek başına yetmez (kural 5, master prompt §9). Kanca girdisinde `agent_type` var (Hooks belgesi).
Karar: `.claude/hooks/write_scopes.json` tek kaynak. `guard.py`, PreToolUse aşamasında yazma, okuma ve Bash çağrılarını denetler. Alanlar ajanlar arasında ayrık.
Sonuçlar: Bash ile alan aşımı tam engellenemez (Denetim §4.1). Dengeleyici kontroller: manifest, CI ve inceleme.

## ADR-004 · Sayılar yer tutucuyla üretilir
Tarih: 2026-10-22 · Durum: kabul · Karar sahibi: Mehmet Güneş (onay 2026-10-22)
Bağlam: B10. Dil modeli rakam uydurabilir; Türkçe kip tespiti kırılgan.
Seçenekler: (A) serbest üretim + sonradan doğrulama · (B) yer tutucu `{{KPI:kpi:yil:tur}}` + deterministik doldurma.
Karar: B, üretimde varsayılan. A deneylerde karşılaştırma kolu olarak tutulur (deney b ve c'ye üçüncü kol).
Sonuçlar: `report_service/generation/placeholders.py` [uygulandı, testli]. Dil modeli entegrasyonu S17'de yapılacak.

## ADR-005 · Eğitim Colab'da, koşu kaydı run.json
Tarih: 2026-10-22 · Durum: kabul · Karar sahibi: Mehmet Güneş
Bağlam: Kullanıcı kararı (Colab); B20.
Karar: Defterler `notebooks/colab/` altında. Kullanıcı çalıştırır. `runs/<run_id>/run.json` repoya, model dosyası Drive'a.
Sonuçlar: Ajanların Colab erişimi yok. Koşu kabulü onay arayüzünden geçer.

## ADR-006 · Onay arayüzü: yerel Streamlit
Tarih: 2026-10-22 · Durum: kabul · Karar sahibi: Mehmet Güneş
Bağlam: İnsan onaylı akış (R-HIL-01). Kullanıcı Streamlit'i kabul etti.
Seçenekler: (A) Label Studio · (B) Streamlit, repodaki dosyaları okur ve yazar.
Karar: B. Kılavuz biçimine birebir uyar, veritabanı gerektirmez.
Sonuçlar: `services/review-ui/` [kısmi: etiket kuyruğu var; koşu ve taslak kuyrukları S07/S17'de].

## ADR-007 · Türkçe spesifiklik skoru
Tarih: 2026-10-22 · Durum: **önerildi**, Mehmet'in onayını bekliyor · Karar sahibi: Mehmet Güneş
Bağlam: B1. `s_spec` İngilizce ClimateBERT'e dayanıyor.
Seçenekler: (A) ClimateBERT'i olduğu gibi kullanmak · (B) 2/1 etiketlerinden Türkçe spesifiklik başlığı eğitmek, taban olarak sayısal yoğunluk sezgiseli · (C) `s_spec`'i formülden çıkarmak.
Karar (öneri): B; ablasyonla (`s_spec` açık/kapalı) katkısı ölçülür.
Sonuçlar: S16, deney (a).

## ADR-008 · Üretim kipleri ve unsur kapsama
Tarih: 2026-10-22 · Durum: **önerildi** · Karar sahibi: Mehmet Güneş
Bağlam: B3 (Kısmi maddeler sahipsiz) ve B4 (`max` çok unsurlu maddeleri yakalamıyor).
Karar (öneri): `yaz` (C < τ₁) ve `tamamla` (τ₁ ≤ C < τ₂) kipleri. Madde kararı, alt unsurların her birinin en az bir paragrafta karşılanmasına göre verilir; çok unsurlu maddeler katalog v1'de bölünür.
Sonuçlar: S02, S14, S17.

## ADR-009 · Maskeleme ile üretim değerlendirmesi
Tarih: 2026-10-22 · Durum: **önerildi** · Karar sahibi: Mehmet Güneş
Bağlam: B7. Eksik maddenin referans metni yok.
Karar (öneri): Tam karşılanan gerçek paragraflar rapordan çıkarılır, sistem yeniden yazar, çıktı orijinalle karşılaştırılır (ROUGE-L, çok dilli modelle BERTScore).
Sonuçlar: S19, R-EVL-02.

## ADR-010 · Standart kapsamı (MVP)
Tarih: 2026-10-22 · Durum: **önerildi** · Karar sahibi: Mehmet Güneş
Bağlam: B13. Sunum TSRS 1, TSRS 2, GRI ve ESRS gösteriyor; katalogda TSRS 2 + VSME var.
Karar (öneri): MVP TSRS 2 + VSME + TSRS 1 çekirdek; ikinci aşama GRI 302/305; ESRS "gelecek çalışma".
Sonuçlar: S02. Sunum ekranları (S-21) buna göre güncellenmeli.

## ADR-011 · Veri sınıfları ve harici dil modeli
Tarih: 2026-10-22 · Durum: **önerildi** · Karar sahibi: Mehmet Güneş
Bağlam: B18. Pilot veri ticari açıdan hassas (G2 §5).
Karar (öneri): Kamu ve kamudan türetilmiş iç veri harici API'ye gidebilir. Pilot firma verisi yalnızca anonimleştirilmiş hâlde ya da yerel modelle işlenir; ajanlar okuyamaz (guard).
Sonuçlar: `.claude/rules/security.md` veri sınıfları tablosu. LLM seçimi S17.

## ADR-012 · İkinci insan etiketleyici ve İngilizce veri setleri
Tarih: 2026-10-22 · Durum: **önerildi** · Karar sahibi: Mehmet Güneş
Bağlam: B6 (insan–model κ ile insan–insan κ ayrımı), B12 (ClimateBERT/ClimaText'in rolü tanımsız). Kullanıcı 2026-10-22'de danışmana götürülmemesini istedi.
Karar (öneri): 30–50 paragraflık bir alt kümeyi Zemzem ikinci insan olarak etiketler; iki κ ayrı raporlanır. İngilizce veri setleri yalnızca katkıları ayrı bir deneyle ölçülürse kullanılır, aksi hâlde kapsam dışı.
Sonuçlar: S05, S16.

## ADR-013 · Etiket şeması 0.1: çekirdek + paragraf alanları + analiz ekranı
Tarih: 2026-10-23 · Durum: kabul · Karar sahibi: Mehmet Güneş (seçim 2026-10-23, üç seçenek arasından)
Bağlam: Kullanıcı pilot başlamadan, etiketleme sisteminin yetersiz ve analiz edilemez olduğunu söyledi. Gerekçe olarak genel bir RAG/ESG etiketleme önerisi paylaştı. Mevcut şema paragraf × madde × düzeydi (2/1/U/NONE) ve tek bir serbest gerekçe alanı vardı. Bu yapıda belirsizlik sayılamıyordu. Hedef ile gerçekleşen sonuç ayrılmıyordu (R-VER-03). Kanıt kaynağı işaretlenmiyordu (R-GEN-03). Analiz ekranı da yoktu.
Seçenekler:
- (A) Çekirdek korunur; paragraf alanları eklenir (beyan türü, madde başına kanıt cümlesi, seçmeli belirsizlik nedeni, emin değilim, süre) ve bir analiz ekranı açılır. Tahmini pilot süresi ~3–4 saat.
- (B) A'ya ek olarak değer, birim, dönem ve hedef yılı elle girilir. ~5–6 saat; elle hata riski yüksek; bu alanlar zaten `verify.numbers` ile otomatik çıkarılıyor.
- (C) Şema aynı kalır, yalnızca analiz ekranı ve belirsizlik nedeni eklenir.
Karar: A.
- Çekirdek CSV başlığı (`etiket_sablonu.csv`) değişmedi; κ ve doğrulayıcı aynı kalır.
- Yeni alanlar yanda `*.paragraf.jsonl` dosyasında tutulur.
- Sözlük tek kaynaktan gelir: `data/labels/etiket_semasi.json`, sürüm `etiket-0.1`.
Sonuçlar:
- Kılavuz v0.1 (§3a–3c).
- `services/review-ui`: kör etiketleme ekranında yeni alanlar, "4 · Analiz" ekranı.
- `tools/validate_data.py` paragraf kayıtlarını ve çekirdekle tutarlılığı denetler.
- Model önerisinin aynı alanları üretmesi S05.T8'dir.
- Geri alma: yan dosya yok sayılırsa sistem şema 0'a döner; çekirdek etiketler etkilenmez.
- Bağımsız inceleme (2026-10-23, [audits/S05-S07-inceleme-2026-10-23-sema.md](audits/S05-S07-inceleme-2026-10-23-sema.md)) sonrası eklenenler:
  - Kurallar ve cümle bölme tek modülde: `tools/etiket_kurallari.py`.
  - İki dosya birlikte yazılır, ya hepsi ya hiçbiri.
  - Körleme kilidi: model önerisi ya da κ gösterilince kör etiketler donar.
  - Süre etkin süredir.
Kanıt: PROGRESS §4 (2026-10-23, ADR-013 kaydı).

## ADR-014 · Tablo ve grafik: hücre ızgarası, olgu ve iki motor
Tarih: 2026-10-23 · Durum: kabul (motor varsayılanı S28.T7 ölçümüne kadar geçici) · Karar sahibi: orkestratör, kullanıcı isteğiyle (2026-10-23, "tablolar ve içindeki veriler ayrışıyor mu … bu yapıyı kurduğundan emin ol")
Bağlam: `pipelines/extract.py` tabloyu "a | b" satırlarından oluşan tek bir metin birimi olarak veriyordu. Hücre konumu, birleşik hücre, başlık rolü, birim, dönem ve koordinat yoktu. Kenarlıksız tablolar kaçıyordu (Klimasan 2025: "Tablo N" başlıklı 34 sayfanın 13'ünde tablo yok). Bölünen tablolar birleşmiyordu (KL-02). Grafiklerden hiçbir şey okunmuyordu. Taslaktaki sayıyı doğrulamak (ADR-004, R-VER-01) için "12.450"nin hangi satır, sütun, yıl ve birime ait olduğu bilinmeli.
Seçenekler:
- (A) PyMuPDF üzerine kendi ızgara, başlık, birleştirme ve olgu katmanımız; hafif, CI'da koşar, kenarlıksız tabloda sezgisel.
- (B) Docling (MIT, yerel, TableFormer modeli): kenarlıksız ve karmaşık tablolarda daha iyi (4 raporun başlıklı sayfalarında deneme: Klimasan s. 37 ve s. 51'i doğru ayırdı); torch ve model indirmesi gerektirir, CPU'da sayfa başına ~1–5 sn.
- (C) PaddleOCR PP-StructureV3 (Apache-2.0): tablo hücre koordinatı ve grafik → tablo (PP-Chart2Table) var; Paddle çerçevesi ek bağımlılık; resmî ajan skill'i bulut API'si ve erişim belirteci ister (yeni harici servis).
- (D) Azure Document Intelligence: bulut servisi; pilot verisi gönderilemez (ADR-011), yeni harici servis ve hesap gerekir.
Karar:
- Kayıt biçimi motordan bağımsızdır: `tablo-0.1`, `olgu-0.1`, `sekil-0.1` (`tools/tablo_kurallari.py`). Hücre alanları docling-core `TableCell` ile aynı anlamda; ızgara bütünlüğü (her konum tam bir hücre) doğrulanır.
- A varsayılan motordur, B isteğe bağlı ikinci motordur (`--motor docling`, `requirements-extract.txt`). C ve D kullanılmaz (C: ek çerçeve ve bulut skill'i; D: harici servis). Varsayılan, S28.T7'de altın kümede ölçülerek yeniden kararlaştırılır.
- `paragraphs.jsonl` değişmez (pilot örneklemi ve kör etiketler ona bağlı). Yeni çıktılar ayrı dosyalardır: `tables.jsonl`, `facts.jsonl`, `figures.jsonl`.
- Olgu: değer `verify.numbers` ile; birim önceliği hücre > sütun başlığı > satır başlığı > tablo başlığı; iki farklı birim anan ya da sayısal veri içeren başlıktan birim alınmaz; bir öğede birden çok yıl varsa dönem boş kalır; yıl hücresine birim verilmez; "-", "—", "n/a" eksik değerdir.
- `verify.numbers`'a para birimi (TL, EUR, USD) eklendi: farklı para birimleri ve fiziksel birimler birbiriyle eşlenmez; kur çevrimi yapılmaz.
- Grafik: değer yalnızca grafikte yazılı etiketten okunur; çubuk boyundan tahmin ve görüntüden veri üretimi yapılmaz (KL-14). Okunamayan grafik `veri_durumu` ile açıkça işaretlenir.
- Ölçüm: tespit, GriTS_Con/GriTS_Top (Smock vd. 2023) ve olgu P/R/F1; insan altın kümesi (U-16).
Sonuçlar:
- Yeni: `pipelines/tables.py`, `figures.py`, `structure.py`; `tools/tablo_kurallari.py`, `tablo_olcum.py`; skill'ler `table-extract`, `figure-extract`, `table-eval`; R-TAB-01…05; S28.
- Olgular S13'te retrieval birimi, S18'de sayı doğrulamanın kaynağı olur (PROGRESS §5).
- Geri alma: yeni dosyalar yok sayılır; `paragraphs.jsonl` ve etiketler etkilenmez.
Kanıt: PROGRESS §4 S28; araştırma notu [research/tablo-grafik-cikarimi.md](research/tablo-grafik-cikarimi.md).

---

## Açık kararlar (D-xx)

Kullanıcının vermesi gereken ya da henüz ADR'ye dönüşmemiş kararlar. Kapanan karar, ilgili ADR'nin durumu `kabul` olunca "kapandı" diye işaretlenir; satır silinmez. Kullanıcı eylemleri: [PROGRESS.md](PROGRESS.md) §2.1.

| D | Konu | Kayıt | Engellediği | Durum |
|---|---|---|---|---|
| D-01 | Türkçe spesifiklik skoru | ADR-007 | S16 | açık (U-05) |
| D-02 | `yaz`/`tamamla` kipleri ve unsur kapsama | ADR-008 | S02, S14, S17 | açık (U-05) |
| D-03 | Maskeleme ile üretim değerlendirmesi | ADR-009 | S19 | açık (U-05) |
| D-04 | MVP standart kapsamı | ADR-010 | S02 | açık (U-05) |
| D-05 | Veri sınıfları ve harici dil modeli | ADR-011 | S17 | açık (U-05) |
| D-06 | İkinci insan etiketleyici, İngilizce veri setleri | ADR-012 | S05.T7, S16 | açık (U-05) |
| D-07 | PDF kütüphanesi: PyMuPDF mi, pdfplumber mı | — (ölçüm S04.T6) | S04 kapanışı | açık |
| D-09 | Varsayılan tablo motoru: PyMuPDF (+ sezgi) mi, Docling mi | ADR-014 | S28.T7 (altın küme U-16'dan sonra) | açık |
| D-08 | `data/labels/blind/**` korumalı yollara eklensin mi | — (`code-reviewer`, 2026-10-23) | — | kapandı: eklendi (Mehmet'in genel onayı, 2026-10-23) |

## Çelişki kaydı (C-xx)

Belgeler arası ya da belge ile kod arası çelişkiler ve çözümleri. Çözülmemiş çelişki açık kalır ve [PROGRESS.md](PROGRESS.md) §3'te risk olarak izlenir.

| C | Çelişki | Çözüm | Durum |
|---|---|---|---|
| C-01 | Geliştirme 2'deki web arayüzü (React iskeleti, veri giriş formları, boşluk matrisi, taslak editörü, panel) görev listesinde yoktu | Plana S25, S26, S27 eklendi (2026-10-23) | çözüldü |
| C-02 | `label-propose` skill'i pilot örneklemi `data/labels/proposals/` altına yazdırıyor; kör etiketleme ekranı `data/labels/pilot/orneklem.jsonl` okuyor | Kanonik yol `data/labels/pilot/orneklem.jsonl`; skill ve ekran eşitlendi, aynı kimlik kümesi testle zorlanıyor | çözüldü |
| C-03 | Geliştirme 2 §4 KOBİ raporu sayısı istiyor; derlem çoğunlukla büyük şirket raporları | S03.T5: ölçek kaynakla sınıflandırılır; KOBİ az çıkarsa tezde açıkça yazılır | açık |
| C-04 | Görev durumları hem `tasks/` dosyalarında hem PROGRESS'te tutuluyordu | Tek plan ([DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)) ve tek durum kaynağı (PROGRESS §1); `tasks/` kaldırıldı | çözüldü |
