"""Paragraf düzeyi etiket kurallarının TEK uygulaması (ADR-013, kılavuz §3a–3c).

Hem kör etiketleme ekranı (`services/review-ui/review_ui/kor.py`, kayıttan önce) hem doğrulayıcı
(`tools/validate_data.py`, dosyadan) bu fonksiyonları kullanır; kurallar iki yerde ayrışmaz
(.claude/rules/data.md). Yalnızca standart kütüphane.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SEMA_YOLU = Path(__file__).resolve().parent.parent / "data" / "labels" / "etiket_semasi.json"
ALANLAR = {
    "paragraf_id", "rapor_id", "beyan_turleri", "kanit", "kanit_metni", "belirsizlik", "emin",
    "sure_sn", "cumle_sayisi", "bolme_surumu", "birim_turu", "etiketleyen", "tarih", "sema_surumu",
}  # fmt: skip
BOLME_SURUMU = "2"


_CUMLE_SONU = re.compile(
    r"(?:(?<=[^\d\s.][.!?…])|(?<=\d{4}\.)|(?<=[.!?…][”\"’)]))"  # harf + nokta, 4 haneli yıl + nokta, nokta + kapanış
    r"\s+(?=[\"“‘'(•%A-ZÇĞİÖŞÜ0-9])"
)
_KISALTMA = re.compile(
    r"(?:\b[A-ZÇĞİÖŞÜ]\.)+$|\b(?:vb|vs|bkz|örn|Dr|Doç|Prof|No|Şti|Tic|San|Ltd|Md|s|sf|vd)\.$"
)


def cumlelere_bol(metin: str, tur: str) -> list[str]:
    """Birimi kanıt seçimi için numaralanacak parçalara böler.

    Tablo satır satır bölünür. Paragrafta cümle sonu: nokta, ünlem ya da soru işaretinden sonra boşluk
    ve büyük harf, rakam, %, tırnak ya da ayraç. Sayıdan sonraki nokta bölmez ("Tablo 1. Sera",
    "11. Kalkınma Planı", "s. 40. Komite"); yalnızca 4 haneli yıl bölünür ("2030. Bunun"). Kısaltmalar
    ("A.Ş.", "bkz.", "s.", "Doç.") bölmez. Basit bir kuraldır (BOLME_SURUMU); yanlış bölme kanıt seçimini
    zorlaştırır ama etiketi bozmaz: kanıt metniyle birlikte saklanır ve metinden yeniden eşlenir.
    """
    if tur == "tablo":
        return [s.strip() for s in metin.split("\n") if s.strip()] or [metin.strip()]
    parcalar: list[str] = []
    for aday in _CUMLE_SONU.split(" ".join(metin.split())):
        if parcalar and _KISALTMA.search(parcalar[-1]):
            parcalar[-1] += " " + aday
        else:
            parcalar.append(aday)
    return [p for p in parcalar if p] or [metin.strip()]


def sema_oku(yol: Path = SEMA_YOLU) -> dict:
    return json.loads(yol.read_text(encoding="utf-8"))


def kural_hatalari(
    seviyeler: dict[str, str | None],
    beyan_turleri: object,
    kanit: object,
    belirsizlik: object,
    emin: object,
    cumle_sayisi: int,
    sema: dict,
) -> list[str]:
    """Bir paragrafın kararı için kural ihlalleri (kullanıcıya gösterilecek Türkçe mesajlar).

    `seviyeler`: madde → karşılama ("2", "1", "U"); NONE paragrafta boş sözlük.
    """
    hatalar: list[str] = []
    if not isinstance(beyan_turleri, list) or not all(isinstance(b, str) for b in beyan_turleri):
        return ["beyan_turleri liste olmalı"]
    if not isinstance(belirsizlik, list) or not all(isinstance(b, str) for b in belirsizlik):
        return ["belirsizlik liste olmalı"]
    if not isinstance(kanit, dict) or not all(isinstance(v, list) for v in kanit.values()):
        return ["kanit, madde → cümle numaraları listesi sözlüğü olmalı"]
    if not isinstance(emin, bool):
        return ["emin true ya da false olmalı"]

    cikarim = "cikarim_hatasi" in belirsizlik
    if set(beyan_turleri) - sema["beyan_turleri"].keys():
        hatalar.append(f"bilinmeyen beyan türü: {sorted(set(beyan_turleri) - sema['beyan_turleri'].keys())}")
    elif not beyan_turleri and not cikarim:
        hatalar.append("En az bir beyan türü seç (kılavuz §3a); çıkarım hatasında boş bırakılabilir")
    bilinmeyen = set(belirsizlik) - sema["belirsizlik_nedenleri"].keys()
    if bilinmeyen:
        hatalar.append(f"bilinmeyen belirsizlik nedeni: {sorted(bilinmeyen)}")
    if not emin and not belirsizlik:
        hatalar.append("'Emin değilim' işaretlendiyse en az bir belirsizlik nedeni seç (kılavuz §3c)")
    if emin and belirsizlik:
        hatalar.append("Belirsizlik nedeni seçildiyse 'Emin değilim' de işaretli olmalı (kılavuz §3c)")
    if cikarim and seviyeler:
        hatalar.append("Çıkarım hatasında madde seçilmez; NONE kaydet (kılavuz §5, durum 6)")
    puanli = {m for m, s in seviyeler.items() if s in ("2", "1")}
    if set(kanit) - puanli:
        hatalar.append(
            f"Kanıt cümlesi yalnızca 2 ya da 1 verilen maddeler için verilir: {sorted(set(kanit) - puanli)}"
        )
    for madde in sorted(puanli):
        if not kanit.get(madde):
            hatalar.append(f"{madde}: 2 ya da 1 için en az bir kanıt cümlesi seç (kılavuz §3b)")
    for madde, idx in sorted(kanit.items()):
        if any(not isinstance(i, int) or isinstance(i, bool) or not 1 <= i <= cumle_sayisi for i in idx):
            hatalar.append(f"{madde}: kanıt cümlesi numarası 1–{cumle_sayisi} arasında olmalı")
    return hatalar
