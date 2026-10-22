#!/usr/bin/env python3
"""Kamu rapor derlemini yerleştirir ve doğrular (S03, R-PDF-01).

Derlem iki adımda oluşur:

1. Tarayıcı, `KAYNAKLAR.csv` içindeki her `url`'yi `dosya_adi` adıyla indirir
   (indirilenler klasörüne düşer).
2. Bu betik indirilen dosyaları kategori klasörüne taşır ve doğrular:
   `%PDF` imzası, SHA-256, boyut, sayfa sayısı ve dil (Türkçe mi).

    python tools/rapor_derlemi.py yerlestir --kaynak ~/Downloads \\
        --hedef ~/Documents/ecoizge-raporlar --manifest ~/Documents/ecoizge-raporlar/KAYNAKLAR.csv
    python tools/rapor_derlemi.py ozet --manifest .../KAYNAKLAR.csv

Yalnızca standart kütüphane kullanır; kullanıcının makinesinde (Python 3.10) de koşar.
Sayfa sayısı ve dil için `pdfinfo` / `pdftotext` (poppler) varsa kullanılır, yoksa boş kalır.
PDF'ler git'e girmez; repoya yalnızca manifest girer (`data/raw/public/KAYNAKLAR.csv`).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

ALANLAR = [
    "rapor_id",
    "kategori",
    "kurum",
    "yil",
    "tur",
    "kaynak_liste",
    "url",
    "dosya_adi",
    "beklenen_boyut",
    "erisim_tarihi",
    "durum",
    "sha256",
    "boyut",
    "sayfa",
    "dil",
    "notlar",
]
KATEGORILER = ("sirket", "kap", "bist", "kidr")
DURUMLAR = ("planlandi", "indirildi", "dogrulandi", "hata", "atlandi")

# Türkçe büyük/küçük harf: Python'un str.lower() "I" → "i" yapar; Türkçede "I" → "ı", "İ" → "i".
_TR_KUCUK = str.maketrans({"I": "ı", "İ": "i"})
_ASCII = str.maketrans(
    {"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u", "â": "a", "î": "i", "û": "u"}
)

TR_ISLEV = frozenset(
    [
        "ve",
        "bir",
        "bu",
        "ile",
        "için",
        "olarak",
        "da",
        "de",
        "olan",
        "gibi",
        "daha",
        "en",
        "çok",
        "her",
        "ise",
        "kadar",
        "sonra",
        "göre",
        "ayrıca",
        "tarafından",
        "üzerinde",
        "yıl",
        "şirket",
        "şirketimiz",
        "kapsamında",
        "ilgili",
        "yönelik",
    ]
)
EN_ISLEV = frozenset(
    [
        "the",
        "and",
        "of",
        "to",
        "in",
        "for",
        "is",
        "are",
        "with",
        "on",
        "by",
        "as",
        "our",
        "that",
        "this",
        "from",
        "be",
        "at",
        "which",
        "we",
        "has",
        "have",
    ]
)


def tr_kucuk(metin: str) -> str:
    """Türkçe kurallarına göre küçük harfe çevirir (I → ı, İ → i)."""
    return metin.translate(_TR_KUCUK).lower()


def slug(metin: str) -> str:
    """Dosya ve kimlik için ASCII, küçük harfli, tireli ad: 'Batıcım TSRS 25' → 'baticim-tsrs-25'."""
    s = tr_kucuk(metin).translate(_ASCII)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def pdf_mi(yol: Path) -> bool:
    """PDF imzası ilk 1024 baytta mı? Okuyucular da öyle arar; bazı KGK dosyalarının başında
    27 baytlık önek var (Kardemir, Klimasan 2025)."""
    with open(yol, "rb") as f:
        return b"%PDF-" in f.read(1024)


def sha256(yol: Path) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def dil_tahmini(metin: str, en_az_sozcuk: int = 50) -> str:
    """İşlev sözcüğü oranıyla dil tahmini: 'tr', 'en', 'karisik' ya da 'belirsiz'.

    Taranmış (metinsiz) PDF'lerde sözcük azdır; bu durumda 'belirsiz' döner ve OCR gerekir.
    """
    sozcukler = re.findall(r"[a-zçğıöşüâîû]+", tr_kucuk(metin))
    if len(sozcukler) < en_az_sozcuk:
        return "belirsiz"
    tr = sum(1 for s in sozcukler if s in TR_ISLEV)
    en = sum(1 for s in sozcukler if s in EN_ISLEV)
    if tr == 0 and en == 0:
        return "belirsiz"
    oran = tr / (tr + en)
    if oran >= 0.8:
        return "tr"
    if oran <= 0.2:
        return "en"
    return "karisik"


def _komut(cmd: list[str]) -> str | None:
    if shutil.which(cmd[0]) is None:
        return None
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def sayfa_sayisi(yol: Path) -> str:
    cikti = _komut(["pdfinfo", str(yol)])
    m = re.search(r"^Pages:\s+(\d+)", cikti or "", re.M)
    return m.group(1) if m else ""


def ilk_sayfalar_metni(yol: Path, son_sayfa: int = 8) -> str | None:
    return _komut(["pdftotext", "-f", "1", "-l", str(son_sayfa), "-enc", "UTF-8", str(yol), "-"])


HATA_ON = "HATA: "


def not_ekle(notlar: str, hata: str) -> str:
    """Kaynak notunu korur, önceki hata notunu yenisiyle değiştirir (boş hata: yalnızca temizler)."""
    taban = notlar.split("; " + HATA_ON)[0]
    taban = "" if taban.startswith(HATA_ON) else taban
    if not hata:
        return taban
    return f"{taban}; {HATA_ON}{hata}" if taban else HATA_ON + hata


def dogrula(yol: Path, satir: dict) -> dict:
    """Bir dosyayı doğrular ve manifest satırının doğrulama alanlarını döndürür."""
    sonuc = {"boyut": str(yol.stat().st_size), "sha256": "", "sayfa": "", "dil": "", "durum": "hata"}
    if not pdf_mi(yol):
        sonuc["notlar"] = not_ekle(
            satir.get("notlar", ""), "PDF imzası yok (hata sayfası indirilmiş olabilir)"
        )
        return sonuc
    sonuc["sha256"] = sha256(yol)
    sonuc["sayfa"] = sayfa_sayisi(yol)
    metin = ilk_sayfalar_metni(yol)
    sonuc["dil"] = dil_tahmini(metin) if metin is not None else ""
    beklenen = satir.get("beklenen_boyut", "")
    if beklenen and beklenen != sonuc["boyut"]:
        sonuc["notlar"] = not_ekle(
            satir.get("notlar", ""), f"boyut farklı: beklenen {beklenen}, gelen {sonuc['boyut']}"
        )
        return sonuc
    sonuc["durum"] = "dogrulandi"
    sonuc["notlar"] = not_ekle(satir.get("notlar", ""), "")
    sonuc["erisim_tarihi"] = satir.get("erisim_tarihi") or date.today().isoformat()
    return sonuc


def oku(manifest: Path) -> list[dict]:
    with open(manifest, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def yaz(manifest: Path, satirlar: list[dict]) -> None:
    gecici = manifest.with_suffix(".tmp")
    with open(gecici, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ALANLAR, extrasaction="ignore")
        w.writeheader()
        for s in satirlar:
            w.writerow({k: s.get(k, "") for k in ALANLAR})
    gecici.replace(manifest)


def denetle(satirlar: list[dict]) -> list[str]:
    """Manifest kurallarını denetler; hata iletilerini döndürür."""
    hatalar = []
    gorulen: dict[str, int] = {}
    for i, s in enumerate(satirlar, start=2):
        for alan in ("rapor_id", "kategori", "url", "dosya_adi", "durum"):
            if not s.get(alan):
                hatalar.append(f"satır {i}: '{alan}' boş")
        if s.get("kategori") and s["kategori"] not in KATEGORILER:
            hatalar.append(f"satır {i}: kategori '{s['kategori']}' geçersiz")
        if s.get("durum") and s["durum"] not in DURUMLAR:
            hatalar.append(f"satır {i}: durum '{s['durum']}' geçersiz")
        if s.get("url") and not s["url"].startswith("https://"):
            hatalar.append(f"satır {i}: url https değil")
        if s.get("durum") == "dogrulandi" and not re.fullmatch(r"[0-9a-f]{64}", s.get("sha256", "")):
            hatalar.append(f"satır {i}: doğrulanmış satırda sha256 yok")
        rid = s.get("rapor_id", "")
        if rid in gorulen:
            hatalar.append(f"satır {i}: rapor_id '{rid}' satır {gorulen[rid]} ile yinelenmiş")
        gorulen[rid] = i
    return hatalar


def yerlestir(kaynak: Path, hedef: Path, manifest: Path, tasima: bool = True) -> Counter:
    satirlar = oku(manifest)
    sayac: Counter = Counter()
    for s in satirlar:
        if s["durum"] == "dogrulandi":
            sayac["zaten doğrulanmış"] += 1
            continue
        hedef_yol = hedef / s["kategori"] / s["dosya_adi"]
        aday = kaynak / s["dosya_adi"]
        if not hedef_yol.exists():
            if not aday.exists():
                sayac["indirilmemiş"] += 1
                continue
            hedef_yol.parent.mkdir(parents=True, exist_ok=True)
            (shutil.move if tasima else shutil.copy2)(str(aday), str(hedef_yol))
        s.update(dogrula(hedef_yol, s))
        sayac[s["durum"]] += 1
    yaz(manifest, satirlar)
    return sayac


BUYUK_DOSYA = 50_000_000
UA = "Mozilla/5.0 (EcoIzge bitirme projesi; kamu raporu derlemi)"


def _indir_url(url: str, hedef: Path, zaman_asimi: int = 120) -> None:
    """URL'yi `hedef`e yazar. HTTPS_PROXY ve SSL_CERT_FILE ortam değişkenlerine uyar (urllib)."""
    from urllib.request import Request, urlopen

    with (
        urlopen(Request(url, headers={"User-Agent": UA}), timeout=zaman_asimi) as yanit,
        open(hedef, "wb") as f,
    ):
        shutil.copyfileobj(yanit, f, 1 << 20)


def indir(
    hedef: Path, manifest: Path, kategoriler=KATEGORILER, buyuk: bool = False, sinir: int = 0
) -> Counter:
    """Planlanan ya da hatalı satırları doğrudan hedef klasöre indirir ve doğrular.

    Ağ izni gerekir (kgk.gov.tr, storage.fintables.com, borsaistanbul.com, mis.yokak.gov.tr).
    Her dosyadan sonra manifest yazılır; yarıda kesilirse kaldığı yerden devam eder.
    """
    satirlar = oku(manifest)
    sayac: Counter = Counter()
    # Önce hiç denenmemiş satırlar, sonra hatalılar: tekrar tekrar düşen büyük bir dosya kuyruğu tıkamasın.
    for s in sorted(satirlar, key=lambda r: r["durum"] == "hata"):
        if s["durum"] == "dogrulandi" or s["kategori"] not in kategoriler:
            continue
        if not buyuk and s.get("beklenen_boyut") and int(s["beklenen_boyut"]) > BUYUK_DOSYA:
            sayac["büyük, atlandı"] += 1
            continue
        if sinir and sum(sayac[d] for d in ("dogrulandi", "hata")) >= sinir:
            break
        yol = hedef / s["kategori"] / s["dosya_adi"]
        yol.parent.mkdir(parents=True, exist_ok=True)
        try:
            if yol.exists():
                s.update(dogrula(yol, s))
            if s["durum"] != "dogrulandi":
                # Önce .part'a indir ve doğrula; yalnızca sağlam dosya kalıcı ada geçer.
                # Silme izni gerekmez: bozuk .part sonraki denemede, yarım kalmış kalıcı dosya
                # da içeriği üzerine yazılarak düzelir.
                gecici = yol.with_name(yol.name + ".part")
                _indir_url(s["url"], gecici)
                s.update(dogrula(gecici, s))
                if s["durum"] == "dogrulandi":
                    if yol.exists():
                        shutil.copyfile(gecici, yol)
                    else:
                        gecici.replace(yol)
        except OSError as e:  # URLError, HTTPError, zaman aşımı OSError alt sınıflarıdır
            s.update(durum="hata", notlar=not_ekle(s.get("notlar", ""), f"indirilemedi: {e}"))
        sayac[s["durum"]] += 1
        yaz(manifest, satirlar)
    yaz(manifest, satirlar)
    return sayac


def ozet(manifest: Path) -> str:
    satirlar = oku(manifest)
    tablo = Counter((s["kategori"], s["durum"]) for s in satirlar)
    diller = Counter(s["dil"] or "—" for s in satirlar if s["durum"] == "dogrulandi")
    satir_metni = [f"{k:<8} {d:<11} {n:>4}" for (k, d), n in sorted(tablo.items())]
    satir_metni.append("diller (doğrulanmış): " + ", ".join(f"{d}={n}" for d, n in diller.most_common()))
    return "\n".join(satir_metni)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    alt = ap.add_subparsers(dest="komut", required=True)
    y = alt.add_parser("yerlestir", help="indirilenleri taşı ve doğrula")
    y.add_argument("--kaynak", type=Path, required=True)
    y.add_argument("--hedef", type=Path, required=True)
    y.add_argument("--manifest", type=Path, required=True)
    y.add_argument("--kopyala", action="store_true", help="taşımak yerine kopyala")
    i = alt.add_parser("indir", help="ağ izni varsa doğrudan hedef klasöre indir ve doğrula")
    i.add_argument("--hedef", type=Path, required=True)
    i.add_argument("--manifest", type=Path, required=True)
    i.add_argument("--kategori", nargs="*", default=list(KATEGORILER), choices=KATEGORILER)
    i.add_argument("--buyuk", action="store_true", help=f"{BUYUK_DOSYA // 1_000_000} MB üstünü de indir")
    i.add_argument("--sinir", type=int, default=0, help="en fazla bu kadar dosya (0: sınırsız)")
    for ad in ("ozet", "denetle"):
        p = alt.add_parser(ad)
        p.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args(argv)

    if a.komut in ("yerlestir", "indir"):
        if a.komut == "yerlestir":
            sayac = yerlestir(
                a.kaynak.expanduser(), a.hedef.expanduser(), a.manifest.expanduser(), not a.kopyala
            )
        else:
            sayac = indir(a.hedef.expanduser(), a.manifest.expanduser(), tuple(a.kategori), a.buyuk, a.sinir)
        print(", ".join(f"{k}: {v}" for k, v in sayac.most_common()))
        return 1 if sayac["hata"] else 0
    if a.komut == "ozet":
        print(ozet(a.manifest.expanduser()))
        return 0
    hatalar = denetle(oku(a.manifest.expanduser()))
    for h in hatalar:
        print(h)
    print(f"{len(hatalar)} hata")
    return 1 if hatalar else 0


if __name__ == "__main__":
    sys.exit(main())
