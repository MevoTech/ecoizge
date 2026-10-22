# Anlaşmazlıkları yorumlama

| Tür | Tanım | Örnek | Kılavuza etkisi |
|---|---|---|---|
| Ölçek kayması | Aynı madde, farklı düzey (2↔1) | Biri "düzenli olarak" ifadesini sıklık saydı, diğeri saymadı | §4'e eşik örneği ekle |
| Madde seçimi | Biri bir madde buldu, diğeri NONE dedi | Risk entegrasyonu cümlesi `TSRS2-RSK-25c` sayıldı ya da sayılmadı | Maddenin `gereklilik_ozeti`'ni netleştir; katalogda gerekirse alt maddeye böl (`catalog-update`) |
| Kardeş madde karışması | Aynı paragraf farklı alt maddelere atandı | `TSRS2-YON-06a` ile `TSRS2-YON-06a-iii` | İki maddenin farkını bir örnek çiftiyle göster |
| Sınır durum | Kılavuz §5'teki açık sorular | Muafiyet beyanı, "planımız yok" | Açık soruyu karara bağla (ADR veya kılavuz sürüm notu) |
| Çıkarım hatası | Metin bozuk olduğu için farklı okundu | "12 450 ." | Etiketten çıkar; `pdf-extract` QA'ya bildir |
| Dikkat hatası | Kılavuz açık, biri kaçırmış | — | Kılavuz değişmez; yalnızca düzeltilir |

Önceliklendirme: sayıca en çok olan ve tez metriklerini en çok etkileyen tür önce ele alınır. Ölçek kayması P/R'yi doğrudan etkiler; madde seçimi recall'u.

Kılavuz sürüm notu biçimi: `- v1 (YYYY-AA-GG): <değişiklik> · gerekçe: kappa raporu <dosya>, <n> anlaşmazlık`.
