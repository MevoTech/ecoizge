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
import importlib.util
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from review_ui import ortak
from review_ui.logic import LABEL_HEADER, read_rows

REPO = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("etiket_kurallari", REPO / "tools" / "etiket_kurallari.py")
kurallar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kurallar)  # paragraf kurallarının tek uygulaması; doğrulayıcı da kullanır
SEMA = kurallar.sema_oku()  # ADR-013: paragraf alanlarının tek kaynağı (data/labels/etiket_semasi.json)
SEMA_SURUMU: str = SEMA["sema_surumu"]
BEYAN_TURLERI: dict[str, str] = SEMA["beyan_turleri"]
BELIRSIZLIK_NEDENLERI: dict[str, str] = SEMA["belirsizlik_nedenleri"]
SEVIYELER = ["2", "1", "U"]  # NONE ayrı: hiçbir madde seçilmezse yazılır
SEVIYE_ADI = {"2": "2 · Tam", "1": "1 · Kısmi / yüzeysel", "U": "U · Uygulanamaz (gerekçeli)"}
ORNEKLEM_SURUMU = "pilot_v0"
BOLME_SURUMU = (
    kurallar.BOLME_SURUMU
)  # cumlelere_bol kuralı değişirse artırılır; kanıt metinden yeniden eşlenir
KESINTI_ESIGI_SN = 600  # bu süreyi aşan paragraf "kesintili" sayılır, toplam ve medyana girmez


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


cumlelere_bol = kurallar.cumlelere_bol  # tek kaynak: tools/etiket_kurallari.py


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
    """Kılavuz §3a–3c (`tools/etiket_kurallari.py`). Hata varsa ValueError; hiçbir dosya yazılmaz."""
    hatalar = kurallar.kural_hatalari(secimler, beyan_turleri, kanit, belirsizlik, emin, cumle_sayisi, SEMA)
    if hatalar:
        raise ValueError(hatalar[0])


def kanit_varsayilan(kayit: dict, madde: str, cumleler: list[str]) -> list[int]:
    """Kaydedilmiş kanıtın bugünkü cümle numaraları. Numara değil metin esas alınır (Ö5): bölme kuralı
    değişse de doğru cümle seçili gelir; metni bulunamayan kanıt seçilmez."""
    metinler = set(kayit.get("kanit_metni", {}).get(madde, []))
    return [i for i, c in enumerate(cumleler, start=1) if c in metinler]


def sure_guncelle(durum: dict, pid: str, simdi: float) -> None:
    """Ekrandaki etkin paragrafı izler; paragraf değişince öncekinin süresi biriktirilir (Ö6)."""
    if durum.get("aktif") != pid:
        if durum.get("aktif") is not None:
            birikim = durum.setdefault("birikim", {})
            birikim[durum["aktif"]] = birikim.get(durum["aktif"], 0.0) + simdi - durum["basla"]
        durum["aktif"], durum["basla"] = pid, simdi


def sure_al(durum: dict, pid: str, simdi: float) -> int:
    """Paragrafın ekranda etkin kaldığı toplam süre (saniye)."""
    toplam = durum.get("birikim", {}).get(pid, 0.0)
    if durum.get("aktif") == pid:
        toplam += simdi - durum["basla"]
    return int(round(toplam))


def sure_sifirla(durum: dict, pid: str, simdi: float) -> None:
    """Kayıttan sonra: aynı paragrafın sonraki düzeltmesi yalnızca yeni süreyi sayar."""
    durum.setdefault("birikim", {}).pop(pid, None)
    if durum.get("aktif") == pid:
        durum["basla"] = simdi


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


def _kilit_yolu(blind_dizini: Path, kimlik: str) -> Path:
    return blind_dizini / kimlik / f"{ORNEKLEM_SURUMU}.kilit.json"


def korleme_acildi(data: Path) -> bool:
    """Model önerisi ya da uyum (κ) bir kez gösterildiyse True: kör etiketler donmuştur (K1)."""
    return any((data / "labels" / "blind").glob(f"*/{ORNEKLEM_SURUMU}.kilit.json"))


def korlemeyi_ac(data: Path, neden: str) -> None:
    """Körlemenin açıldığı anı kaydeder ve kör etiketleri dondurur. Var olan kilit değiştirilmez.

    Her etiketleyicinin dizinine `pilot_v0.kilit.json`: zaman, neden ve o anki CSV ile paragraf
    kaydının SHA-256 özetleri. Sonradan değişiklik bu özetlerle fark edilir; düzeltmeler kılavuz v1
    turunda (`pilot_v1`) yapılır.
    """
    blind = data / "labels" / "blind"
    for csv_yolu in sorted(blind.glob(f"*/{ORNEKLEM_SURUMU}.csv")):
        kilit = _kilit_yolu(blind, csv_yolu.parent.name)
        if kilit.exists():
            continue
        yan = paragraf_yolu(csv_yolu)
        icerik = {
            "zaman": datetime.now(UTC).isoformat(timespec="seconds"),
            "neden": neden,
            "csv_sha256": hashlib.sha256(csv_yolu.read_bytes()).hexdigest(),
            "paragraf_sha256": hashlib.sha256(yan.read_bytes()).hexdigest() if yan.exists() else None,
        }
        ortak.atomik_metin_yaz(kilit, json.dumps(icerik, ensure_ascii=False, indent=1) + "\n")


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
    if any(cikti.parent.parent.glob(f"*/{ORNEKLEM_SURUMU}.kilit.json")):
        raise ValueError(
            "Körleme açıldı (model önerisi ya da κ gösterildi); kör etiketler artık değiştirilemez. "
            "Düzeltmeler kılavuz v1 turunda yapılır."
        )
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
    yazilacak = [(cikti, ortak.csv_metni(LABEL_HEADER, kalan + yeni))]
    if beyan_turleri is not None:
        onceki = paragraf_kayitlari(cikti).get(birim["paragraf_id"], {})
        if isinstance(sure_sn, int) and isinstance(onceki.get("sure_sn"), int):
            sure_sn += onceki["sure_sn"]  # düzeltme süresi ilk etiketleme süresine eklenir (Ö6)
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
            "bolme_surumu": BOLME_SURUMU,
            "birim_turu": birim.get("tur", "paragraf"),
            "etiketleyen": etiketleyen.strip(),
            "tarih": (bugun or date.today()).isoformat(),
            "sema_surumu": SEMA_SURUMU,
        }
        diger = [k for pid, k in paragraf_kayitlari(cikti).items() if pid != birim["paragraf_id"]]
        yazilacak.append(
            (paragraf_yolu(cikti), "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in [*diger, kayit]))
        )
    if orneklem_ozeti and not _ozet_yolu(cikti).exists():
        yazilacak.append((_ozet_yolu(cikti), orneklem_ozeti + "\n"))
    ortak.atomik_coklu_yaz(yazilacak)  # ya hepsi ya hiçbiri (Ö1)
    return yeni
