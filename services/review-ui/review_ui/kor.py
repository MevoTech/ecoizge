"""Kör etiketleme mantığı (S05, R-ETK-01). Streamlit olmadan test edilir.

Akış: data/labels/pilot/orneklem.jsonl → insan, modelin etiketini GÖRMEDEN etiketler →
      data/labels/blind/<etiketleyen>/pilot_v0.csv (etiket şablonu biçimi, kaynak = insan).

Körleme kuralları:
- Bu modül öneri dosyalarını (data/labels/proposals/) ve onay günlüğünü okumaz.
- annotation-assistant, data/labels/blind/** dizinini okuyamaz (.claude/hooks/write_scopes.json).
- κ yalnızca iki taraf da bitirdikten sonra hesaplanır (agreement-kappa skill'i).
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from review_ui import ortak
from review_ui.logic import LABEL_HEADER, read_rows, write_rows

SEMA_YOLU = Path(__file__).resolve().parents[3] / "data" / "labels" / "etiket_semasi.json"
SEMA = json.loads(SEMA_YOLU.read_text(encoding="utf-8"))  # ADR-013: paragraf alanlarının tek kaynağı
SEMA_SURUMU: str = SEMA["sema_surumu"]
BEYAN_TURLERI: dict[str, str] = SEMA["beyan_turleri"]
BELIRSIZLIK_NEDENLERI: dict[str, str] = SEMA["belirsizlik_nedenleri"]
SEVIYELER = ["2", "1", "U"]  # NONE ayrı: hiçbir madde seçilmezse yazılır
SEVIYE_ADI = {"2": "2 · Tam", "1": "1 · Kısmi / yüzeysel", "U": "U · Uygulanamaz (gerekçeli)"}
ORNEKLEM_SURUMU = "pilot_v0"


def ad_kimligi(ad: str) -> str:
    """'Mehmet Güneş' → 'mehmet-gunes' (dizin adı için)."""
    s = ortak.tr_kucuk(ad)
    s = s.translate(str.maketrans("çğıöşü", "cgiosu"))
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


@dataclass(frozen=True)
class KorYollar:
    data: Path

    @property
    def orneklem(self) -> Path:
        return self.data / "labels" / "pilot" / "orneklem.jsonl"

    def cikti(self, etiketleyen: str) -> Path:
        kimlik = ad_kimligi(etiketleyen)
        if not kimlik:
            raise ValueError("etiketleyen adı zorunlu ve en az bir harf ya da rakam içermeli")
        return self.data / "labels" / "blind" / kimlik / f"{ORNEKLEM_SURUMU}.csv"


def orneklem_oku(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def yapilanlar(cikti: Path) -> dict[str, list[dict[str, str]]]:
    """paragraf_id → o paragraf için yazılmış satırlar."""
    out: dict[str, list[dict[str, str]]] = {}
    for r in read_rows(cikti):
        out.setdefault(r["paragraf_id"], []).append(r)
    return out


_CUMLE_SONU = re.compile(r"(?<=[^\d\s.][.!?…])\s+(?=[\"“(•A-ZÇĞİÖŞÜ0-9])")
_KISALTMA = re.compile(r"(?:\b[A-ZÇĞİÖŞÜ]\.)+$|\b(?:vb|vs|bkz|örn|Dr|Prof|No|Şti|Tic|San)\.$")


def cumlelere_bol(metin: str, tur: str) -> list[str]:
    """Birimi kanıt seçimi için numaralanacak parçalara böler.

    Tablo satır satır bölünür. Paragrafta cümle sonu: nokta, ünlem ya da soru işaretinden sonra boşluk
    ve büyük harf/rakam. Rakamdan sonraki nokta ("Tablo 1. Sera", "2. sırada") ve kısaltmalar
    ("A.Ş.", "bkz.") bölmez. Basit bir kuraldır; yanlış bölme kanıt seçimini zorlaştırır ama
    etiketi bozmaz (seçilen numaralar metinle birlikte saklanır).
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


def paragraf_yolu(cikti: Path) -> Path:
    """Paragraf düzeyi kayıtlar (beyan türü, kanıt, belirsizlik, süre) çekirdek CSV'nin yanında."""
    return cikti.with_suffix(".paragraf.jsonl")


def paragraf_kayitlari(cikti: Path) -> dict[str, dict]:
    yol = paragraf_yolu(cikti)
    if not yol.exists():
        return {}
    with yol.open(encoding="utf-8-sig") as fh:
        kayitlar = [json.loads(s) for s in fh if s.strip()]
    return {k["paragraf_id"]: k for k in kayitlar}


def paragraf_kaydi_denetle(
    secimler: dict[str, str | None],
    beyan_turleri: list[str],
    kanit: dict[str, list[int]],
    belirsizlik: list[str],
    emin: bool,
    cumle_sayisi: int,
) -> None:
    """Kılavuz §3a–3c. Hata varsa ValueError (ekranda gösterilir); hiçbir dosya yazılmaz."""
    if not beyan_turleri or set(beyan_turleri) - BEYAN_TURLERI.keys():
        raise ValueError("En az bir beyan türü seç (kılavuz §3a); bilinmeyen beyan türü kabul edilmez")
    bilinmeyen = set(belirsizlik) - BELIRSIZLIK_NEDENLERI.keys()
    if bilinmeyen:
        raise ValueError(f"bilinmeyen belirsizlik nedeni: {sorted(bilinmeyen)}")
    if not emin and not belirsizlik:
        raise ValueError("'Emin değilim' işaretlendiyse en az bir belirsizlik nedeni seç (kılavuz §3c)")
    if "cikarim_hatasi" in belirsizlik and secimler:
        raise ValueError("Çıkarım hatasında madde seçilmez; NONE kaydet (kılavuz §5, durum 6)")
    if set(kanit) - set(secimler):
        raise ValueError("Kanıt cümlesi yalnızca seçili maddeler için verilir")
    for madde, seviye in secimler.items():
        cumleler = kanit.get(madde, [])
        if seviye in ("2", "1") and not cumleler:
            raise ValueError(f"{madde}: 2 ya da 1 için en az bir kanıt cümlesi seç (kılavuz §3b)")
        if any(not (isinstance(i, int) and 1 <= i <= cumle_sayisi) for i in cumleler):
            raise ValueError(f"{madde}: kanıt cümlesi numarası 1–{cumle_sayisi} arasında olmalı")


def ilerleme(orneklem: list[dict], yapilan: dict) -> tuple[int, int, list[str]]:
    """(örneklemden etiketlenen, örneklem büyüklüğü, örneklemde olmayan paragraf kimlikleri)."""
    kimlikler = {u["paragraf_id"] for u in orneklem}
    return len(kimlikler & yapilan.keys()), len(kimlikler), sorted(yapilan.keys() - kimlikler)


def orneklem_ozeti(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ozet_yolu(cikti: Path) -> Path:
    return cikti.with_suffix(".orneklem.sha256")


def ozet_denetle(cikti: Path, ozet: str) -> str | None:
    """Etiket dosyası başka bir örneklemle başlatıldıysa hata mesajı döner (κ karışmasın)."""
    yol = _ozet_yolu(cikti)
    if not yol.exists():
        return None
    eski = yol.read_text(encoding="utf-8").strip()
    if eski == ozet:
        return None
    return (
        "Pilot örneklem değişmiş: bu etiket dosyası başka bir örneklemle başlatılmış "
        f"({eski[:12]}…, şimdiki {ozet[:12]}…). Kayıt durduruldu; orkestratöre bildir."
    )


def pilot_kimlikleri(data: Path) -> set[str]:
    yol = KorYollar(data).orneklem
    return {u["paragraf_id"] for u in orneklem_oku(yol)} if yol.exists() else set()


def pilot_kilitli(data: Path) -> bool:
    """Kör etiketleme sürüyor mu? Hiç kör dosya yoksa ya da biri örneklemi bitirmediyse evet.

    Kilitliyken onay ekranı pilot paragraflarının model önerilerini göstermez (R-ETK-01).
    """
    kimlikler = pilot_kimlikleri(data)
    if not kimlikler:
        return False
    dosyalar = sorted((data / "labels" / "blind").glob(f"*/{ORNEKLEM_SURUMU}.csv"))
    if not dosyalar:
        return True
    return any(not kimlikler <= yapilanlar(f).keys() for f in dosyalar)


def madde_filtrele(katalog: dict[str, dict], standart: str, bolum: str, arama: str) -> set[str]:
    """Standart, bölüm ve serbest aramaya uyan madde kimlikleri (Türkçe büyük/küçük harf duyarsız)."""
    arama = ortak.tr_kucuk(arama.strip())
    out = set()
    for mid, m in katalog.items():
        if standart != "Tümü" and m["standart"] != standart:
            continue
        if bolum != "Tümü" and m["bolum"] != bolum:
            continue
        if arama and arama not in ortak.tr_kucuk(f"{mid} {m['baslik']} {m['gereklilik_ozeti']}"):
            continue
        out.add(mid)
    return out


def sonraki_sira(orneklem: list[dict], yapilan: dict) -> int | None:
    """İlk etiketlenmemiş paragrafın sırası; hepsi bittiyse None."""
    for i, u in enumerate(orneklem):
        if u["paragraf_id"] not in yapilan:
            return i
    return None


def _sirket_yil(rapor_id: str) -> tuple[str, str]:
    """'sirket-akbank-2025' → ('akbank', '2025')."""
    m = re.fullmatch(r"(?:sirket|kap)-(.+)-(\d{4})", rapor_id)
    return (m.group(1), m.group(2)) if m else ("", "")


def kaydet(
    cikti: Path,
    birim: dict,
    secimler: dict[str, str],
    etiketleyen: str,
    katalog_kimlikleri: set[str],
    gerekce: str = "",
    bugun: date | None = None,
    orneklem_ozeti: str | None = None,
    *,
    beyan_turleri: list[str] | None = None,
    kanit: dict[str, list[int]] | None = None,
    belirsizlik: list[str] | None = None,
    emin: bool = True,
    sure_sn: int | None = None,
) -> list[dict[str, str]]:
    """Bir paragrafın kararını yazar; aynı paragrafın önceki kararını değiştirir.

    `secimler` boşsa paragraf hiçbir maddeyle ilgili değildir ve tek NONE satırı yazılır.
    `beyan_turleri` verilirse (şema 0.1, ADR-013) paragraf kaydı da yazılır: beyan türü, madde
    başına kanıt cümlesi, belirsizlik nedeni, emin değilim, süre. Kör etiketleme ekranı hep verir.
    """
    if not etiketleyen.strip():
        raise ValueError("etiketleyen adı zorunlu")
    for madde, seviye in secimler.items():
        if seviye is None:
            raise ValueError(f"{madde}: karşılama düzeyini seç (2, 1 ya da U)")
        if seviye not in SEVIYELER:
            raise ValueError(f"{madde}: karşılama {seviye!r} geçersiz, {SEVIYELER} olmalı")
        if madde not in katalog_kimlikleri:
            raise ValueError(f"{madde} katalogda yok")
    if "U" in secimler.values() and not gerekce.strip():
        raise ValueError("U (uygulanamaz) için gerekçe zorunlu (kılavuz §3)")
    cumleler = cumlelere_bol(birim["metin"], birim.get("tur", "paragraf"))
    if beyan_turleri is not None:
        paragraf_kaydi_denetle(secimler, beyan_turleri, kanit or {}, belirsizlik or [], emin, len(cumleler))

    sirket, yil = _sirket_yil(birim["rapor_id"])
    temel = dict.fromkeys(LABEL_HEADER, "") | {
        "tur": "paragraf",
        "rapor_id": birim["rapor_id"],
        "sirket": sirket,
        "yil": yil,
        "paragraf_id": birim["paragraf_id"],
        "sayfa": str(birim["sayfa"]),
        "bolum_basligi": birim.get("bolum_basligi", ""),
        "metin": birim["metin"],
        "gerekce": gerekce.strip(),
        "etiketleyen": etiketleyen.strip(),
        "kaynak": "insan",
        "tarih": (bugun or date.today()).isoformat(),
    }
    yeni = [
        temel | {"etiket_id": f"{birim['paragraf_id']}:{m}", "madde_id": m, "karsilama": s}
        for m, s in sorted(secimler.items())
    ] or [temel | {"etiket_id": f"{birim['paragraf_id']}:NONE", "madde_id": "NONE", "karsilama": "NONE"}]

    kalan = [r for r in read_rows(cikti) if r["paragraf_id"] != birim["paragraf_id"]]
    write_rows(cikti, kalan + yeni)
    if beyan_turleri is not None:
        kayit = {
            "paragraf_id": birim["paragraf_id"],
            "rapor_id": birim["rapor_id"],
            "beyan_turleri": list(beyan_turleri),
            "kanit": {m: sorted(set(v)) for m, v in sorted((kanit or {}).items())},
            "kanit_metni": {
                m: [cumleler[i - 1] for i in sorted(set(v))] for m, v in sorted((kanit or {}).items())
            },
            "belirsizlik": list(belirsizlik or []),
            "emin": bool(emin),
            "sure_sn": sure_sn,
            "cumle_sayisi": len(cumleler),
            "etiketleyen": etiketleyen.strip(),
            "tarih": (bugun or date.today()).isoformat(),
            "sema_surumu": SEMA_SURUMU,
        }
        diger = [k for pid, k in paragraf_kayitlari(cikti).items() if pid != birim["paragraf_id"]]
        ortak.atomik_metin_yaz(
            paragraf_yolu(cikti), "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in [*diger, kayit])
        )
    if orneklem_ozeti and not _ozet_yolu(cikti).exists():
        _ozet_yolu(cikti).write_text(orneklem_ozeti + "\n", encoding="utf-8")
    return yeni
