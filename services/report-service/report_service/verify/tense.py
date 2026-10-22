"""Gerçekleşmiş / tahmin kip denetimi (R-VER-03, Sunum S-19 düzey 4, B10).

Kural tabanlıdır ve bilinçli olarak dar tutulmuştur: yalnızca resmî rapor dilinde sık geçen
kalıpları tanır. Tanımadığı bir cümleyi "geçti" saymaz; tahmin cümlesinde öngörü işareti
bulamazsa hata verir (güvenli taraf). Bilinen sınır: yan cümle ve alıntı içeren karmaşık
cümlelerde yanlış alarm verebilir; bu durum için test vakası eklenip kural genişletilir.
"""

from __future__ import annotations

import re

FORECAST = re.compile(
    r"öngörülmektedir|öngörülüyor|beklenmektedir|beklenmekte|beklenen|tahmin edilmektedir|"
    r"tahmin ediliyor|öngörülen|tahmini|planlanmaktadır|"
    r"\b\w+(?:acak|ecek)(?:tır|tir)?\b",
    flags=re.IGNORECASE,
)
PAST = re.compile(
    r"gerçekleşmiştir|gerçekleşti\b|gerçekleşen|ölçülmüştür|kaydedilmiştir|olmuştur|oldu\b|"
    r"\b\w+(?:mıştır|miştir|muştur|müştür)\b",
    flags=re.IGNORECASE,
)


def check_sentence(sentence: str, kind: str) -> str | None:
    """`kind` ∈ {"tahmin", "gerceklesmis"}. Hata varsa açıklama, yoksa None döndürür."""
    has_future = FORECAST.search(sentence) is not None
    has_past = PAST.search(sentence) is not None
    if kind == "tahmin":
        if has_past:
            return "tahmin değeri geçmiş/gerçekleşmiş kipiyle yazılmış"
        if not has_future:
            return "tahmin değeri öngörü kipi taşımıyor (ör. 'öngörülmektedir')"
    elif kind == "gerceklesmis":
        if has_future and not has_past:
            return "gerçekleşmiş değer öngörü kipiyle yazılmış"
    else:
        raise ValueError(f"bilinmeyen tür: {kind!r}")
    return None
