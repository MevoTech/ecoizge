"""Türkçe sayı, ölçek, yüzde ve birim ayrıştırma; kaynak değerle ε eşlemesi (R-VER-01, B9).

Projede sayı ayrıştırmanın tek kaynağı budur (`.claude/rules/python.md`).

Biçim kuralları:
- Hem '.' hem ',' varsa: '.' binlik, ',' ondalık → "12.450,5" = 12450.5
- Yalnızca ',' varsa: ondalık → "1,5" = 1.5
- Yalnızca '.' varsa: noktadan sonraki gruplar 3 haneliyse binlik ("1.234" = 1234),
  değilse ondalık ("12.5" = 12.5). "1.234" belirsizdir; Türkçe metin varsayımıyla binlik sayılır.
- 1900–2100 arası, ayraçsız, birimsiz, ölçeksiz tam sayı yıl kabul edilir.
- Para birimleri (TL, EUR, USD) birim olarak tanınır; farklı para birimleri ve fiziksel birimler
  birbiriyle eşlenmez (ADR-014). Kur çevrimi yapılmaz.

Tablo hücresi (`hucre_degeri`) ve başlık birimi (`birim_bul`) da buradadır (R-TAB-02): hücre tek bir
sayı (ve birim, yüzde, dipnot işareti) içeriyorsa sayısal sayılır; artı işareti atılır; eksi işareti (-, −, –) ve muhasebe
ayracı "(1.234)" eksi değerdir; "-", "—", "n/a", "yok" eksik değerdir (sıfır değil).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SCALES = {"bin": 1e3, "milyon": 1e6, "milyar": 1e9}

# birim yazımı (küçük harf, boşluksuz) → (taban birim, çarpan)
UNITS: dict[str, tuple[str, float]] = {
    "tco2e": ("tCO2e", 1.0),
    "tonco2e": ("tCO2e", 1.0),
    "tonco2": ("tCO2e", 1.0),
    "ktco2": ("tCO2e", 1e3),
    "mtco2": ("tCO2e", 1e6),
    "tco2": ("tCO2e", 1.0),
    "ktco2e": ("tCO2e", 1e3),
    "mtco2e": ("tCO2e", 1e6),
    "kwh": ("kWh", 1.0),
    "mwh": ("kWh", 1e3),
    "gwh": ("kWh", 1e6),
    "m3": ("m3", 1.0),
    "m³": ("m3", 1.0),
    "ton": ("t", 1.0),
    "t": ("t", 1.0),
    "kg": ("t", 1e-3),
    "%": ("%", 1.0),
    "tl": ("TL", 1.0),
    "₺": ("TL", 1.0),
    "eur": ("EUR", 1.0),
    "euro": ("EUR", 1.0),
    "avro": ("EUR", 1.0),
    "€": ("EUR", 1.0),
    "usd": ("USD", 1.0),
    "dolar": ("USD", 1.0),
    "$": ("USD", 1.0),
}

PARA_BIRIMLERI = {"TL", "EUR", "USD"}
_NUM = r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+,\d+|\d+(?:\.\d+)?"
_UNIT = (
    r"(?:k|M)?t\s?CO\s?[₂2](?:\s?e\b)?|ton\s?CO\s?[₂2](?:\s?e\b)?|[kMG]Wh|m[³3]"  # "CO 2 e": ayrı alt simge  # tCO2e, MWh, m³ …
    r"|TL\b|₺|EUR\b|euro\b|avro\b|€|USD\b|dolar\b|\$"  # para birimi (ADR-014)
    r"|ton\b|kg\b|t\b"
)
_PARA_ON = r"(?:(?<![^\W\d_])(?P<cur_pre>(?:TL|USD|EUR)\s+|[₺€$]\s?))?"  # "TL 805.299", "€ 16.000"
_PATTERN = re.compile(
    rf"{_PARA_ON}(?P<pct_pre>%|yüzde\s+)?(?P<num>{_NUM})"
    rf"(?:\s+(?P<scale>bin|milyon|milyar|B[İI]N|M[İI]LYON|M[İI]LYAR)\b)?"
    rf"(?:\s?(?P<pct_post>%)|\s?(?P<unit>{_UNIT}))?",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str | None  # taban birim; yoksa None
    raw: str
    start: int
    end: int
    is_year: bool = False

    @property
    def is_percent(self) -> bool:
        return self.unit == "%"


def parse_tr_number(text: str) -> float:
    """Türkçe yazılmış sayıyı float'a çevirir. Geçersizse ValueError."""
    s = text.strip()
    if not re.fullmatch(r"[\d.,]+", s) or not re.search(r"\d", s):
        raise ValueError(f"sayı değil: {text!r}")
    if "." in s and "," in s:
        if s.rfind(",") < s.rfind("."):
            raise ValueError(f"belirsiz ayraç sırası: {text!r}")
        return float(s.replace(".", "").replace(",", "."))
    if "," in s:
        if s.count(",") > 1:
            raise ValueError(f"birden çok ondalık ayraç: {text!r}")
        return float(s.replace(",", "."))
    if "." in s:
        head, *groups = s.split(".")
        if groups and all(len(g) == 3 for g in groups) and 1 <= len(head) <= 3:
            return float(s.replace(".", ""))
        if len(groups) == 1:
            return float(s)
        raise ValueError(f"geçersiz nokta kullanımı: {text!r}")
    return float(s)


def normalize_unit(unit: str) -> tuple[str, float]:
    key = re.sub(r"\s+", "", unit).replace("₂", "2").lower()  # "ton CO 2 e" → "tonco2e"
    if key not in UNITS:
        raise ValueError(f"bilinmeyen birim: {unit!r}")
    return UNITS[key]


def extract_numbers(text: str) -> list[Quantity]:
    """Metindeki sayısal ifadeleri taban birime çevrilmiş olarak döndürür."""
    out: list[Quantity] = []
    for m in _PATTERN.finditer(text):
        raw_num = m.group("num")
        # sözcük içindeki rakamları (ör. "CO2", "S-03") atla
        if m.start("num") > 0 and (text[m.start("num") - 1].isalpha() or text[m.start("num") - 1] in "-_"):
            continue
        try:
            value = parse_tr_number(raw_num)
        except ValueError:
            continue
        unit: str | None = None
        start, end = m.start(), m.end()
        if m.group("scale"):
            value *= SCALES[_tr_kucuk(m.group("scale")).replace("ı", "i")]  # "MİLYON", "MILYON"
        if m.group("pct_pre") or m.group("pct_post"):
            unit = "%"
        elif m.group("unit"):
            unit, factor = normalize_unit(m.group("unit"))
            value *= factor
        elif m.group("cur_pre"):
            unit, _ = normalize_unit(m.group("cur_pre"))
        yil_bicimi = (
            not m.group("scale")
            and re.fullmatch(r"\d{4}", raw_num) is not None
            and 1900 <= int(raw_num) <= 2100
        )
        if yil_bicimi and m.group("unit") and unit in PARA_BIRIMLERI and m.group("unit")[0].isalpha():
            # "2025 Avro Bölgesi", "2024 TL'si" gibi: yıl + para birimi adı tutar değildir
            unit, value, start, end = None, float(raw_num), m.start("num"), m.end("num")
        is_year = unit is None and yil_bicimi and not m.group("cur_pre")
        out.append(Quantity(value, unit, text[start:end].strip(), start, end, is_year))
    return out


def relative_error(a: float, b: float) -> float:
    if b == 0:
        return 0.0 if a == 0 else float("inf")
    return abs(a - b) / abs(b)


def match(q: Quantity, candidates: list[Quantity], eps: float = 0.005) -> Quantity | None:
    """Aynı taban birimde ve göreli hatası ≤ eps olan ilk adayı döndürür (S-15 adım 5)."""
    for c in candidates:
        if c.unit == q.unit and relative_error(q.value, c.value) <= eps:
            return c
    return None


def format_tr(value: float, decimals: int = 0) -> str:
    """12450.5 → '12.450,5' (Türkçe biçim)."""
    s = f"{value:,.{decimals}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


# ---------- tablo hücresi ve başlık birimi (R-TAB-02, ADR-014) ----------

_EKSIK = {"-", "–", "—", "--", "n/a", "na", "n.a.", "yok", "mevcut değil", "uygulanamaz", "hesaplanmadı"}
_DIPNOT = re.compile(r"\s*(\*+|\(\d{1,2}\)|[¹²³⁴⁵⁶⁷⁸⁹⁰]+)$")
_EKSI = "-−–"
_HARF = "A-Za-zÇĞİÖŞÜçğıöşü"
_BIRIM_ARAMA = re.compile(
    rf"(?<![{_HARF}\d])(?:(?P<scale>bin|milyon|milyar)\s+)?(?P<unit>{_UNIT})(?![{_HARF}])",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class HucreDegeri:
    deger: float | None  # taban birimde; eksik değerde None
    birim: str | None
    ham: str
    eksik: bool = False
    dipnot: tuple[str, ...] = ()
    yil: bool = False


def _tr_kucuk(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()


def hucre_degeri(metin: str) -> HucreDegeri | None:
    """Tablo hücresinin sayısal değeri; hücre sayısal değilse None.

    Hücre yalnızca tek bir sayısal ifade (birim, yüzde ve ölçekle) ve isteğe bağlı dipnot işaretleri
    ("*", "(1)", "¹") içeriyorsa sayısaldır. "Kapsam 1", "12.450 ve 3.200" sayısal değildir.
    """
    s = " ".join(metin.split())
    dipnot: list[str] = []
    while (m := _DIPNOT.search(s)) and m.start() > 0:
        if m.group(1)[0] in "¹²³⁴⁵⁶⁷⁸⁹⁰" and s[m.start() - 1].isalpha():
            break  # "m³", "m²": birimin parçası, dipnot değil
        dipnot.insert(0, m.group(1))
        s = s[: m.start()].rstrip()
    if not s:
        return None
    if _tr_kucuk(s) in _EKSIK:
        return HucreDegeri(None, None, metin, eksik=True, dipnot=tuple(dipnot))
    eksi = False
    if s.startswith("(") and s.endswith(")"):
        s, eksi = s[1:-1].strip(), True
    if s[:1] in _EKSI and len(s) > 1:
        s, eksi = s[1:].lstrip(), not eksi
    elif s[:1] == "+" and len(s) > 1:
        s = s[1:].lstrip()
    s = re.sub(r"^%\s+", "%", s)
    qs = extract_numbers(s)
    if len(qs) != 1 or qs[0].start != 0 or qs[0].end != len(s):
        return None
    q = qs[0]
    return HucreDegeri(
        -q.value if eksi else q.value,
        q.unit,
        metin,
        dipnot=tuple(dipnot),
        yil=q.is_year and not eksi,
    )


def birimler_bul(metin: str) -> list[tuple[str, float]]:
    """Metindeki bütün birim anışları (sırasıyla): "Enerji (MWh) ve emisyon (tCO2e)" → iki birim."""
    out: list[tuple[str, float]] = []
    if "%" in metin:
        out.append(("%", 1.0))
    for m in _BIRIM_ARAMA.finditer(metin):
        try:
            taban, carpan = normalize_unit(m.group("unit"))
        except ValueError:
            continue
        if m.group("scale"):
            carpan *= SCALES[_tr_kucuk(m.group("scale"))]
        out.append((taban, carpan))
    return out


def birim_bul(metin: str) -> tuple[str, float] | None:
    """Sütun başlığı ya da tablo başlığındaki birim: "(Bin TL)" → ("TL", 1000.0); yoksa None."""
    bulunan = birimler_bul(metin)
    return bulunan[0] if bulunan else None
