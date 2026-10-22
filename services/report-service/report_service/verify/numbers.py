"""Türkçe sayı, ölçek, yüzde ve birim ayrıştırma; kaynak değerle ε eşlemesi (R-VER-01, B9).

Projede sayı ayrıştırmanın tek kaynağı budur (`.claude/rules/python.md`).

Biçim kuralları:
- Hem '.' hem ',' varsa: '.' binlik, ',' ondalık → "12.450,5" = 12450.5
- Yalnızca ',' varsa: ondalık → "1,5" = 1.5
- Yalnızca '.' varsa: noktadan sonraki gruplar 3 haneliyse binlik ("1.234" = 1234),
  değilse ondalık ("12.5" = 12.5). "1.234" belirsizdir; Türkçe metin varsayımıyla binlik sayılır.
- 1900–2100 arası, ayraçsız, birimsiz, ölçeksiz tam sayı yıl kabul edilir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SCALES = {"bin": 1e3, "milyon": 1e6, "milyar": 1e9}

# birim yazımı (küçük harf, boşluksuz) → (taban birim, çarpan)
UNITS: dict[str, tuple[str, float]] = {
    "tco2e": ("tCO2e", 1.0),
    "tonco2e": ("tCO2e", 1.0),
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
}

_NUM = r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+,\d+|\d+(?:\.\d+)?"
_UNIT = r"(?:k|M)?t\s?CO[₂2]\s?e?|ton\s?CO[₂2]\s?e?|[kMG]Wh|m[³3]|ton\b|kg\b|t\b"  # tCO2e, MWh, m³ …
_PATTERN = re.compile(
    rf"(?P<pct_pre>%|yüzde\s+)?(?P<num>{_NUM})"
    rf"(?:\s+(?P<scale>bin|milyon|milyar)\b)?"
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
    key = re.sub(r"\s+", "", unit).replace("₂", "2").lower()
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
        if m.group("scale"):
            value *= SCALES[m.group("scale").lower()]
        if m.group("pct_pre") or m.group("pct_post"):
            unit = "%"
        elif m.group("unit"):
            unit, factor = normalize_unit(m.group("unit"))
            value *= factor
        is_year = (
            unit is None
            and not m.group("scale")
            and re.fullmatch(r"\d{4}", raw_num) is not None
            and 1900 <= int(raw_num) <= 2100
        )
        out.append(Quantity(value, unit, m.group(0).strip(), m.start(), m.end(), is_year))
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
