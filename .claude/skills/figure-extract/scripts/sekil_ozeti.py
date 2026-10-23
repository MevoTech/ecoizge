#!/usr/bin/env python3
"""Şekil ve grafik çıkarımının özeti ve elle kontrol listesi (figure-extract skill'i, S28).

    python .claude/skills/figure-extract/scripts/sekil_ozeti.py <cikti_dizini>/figures.jsonl [--pdf rapor.pdf]

Veri durumuna göre sayım, verisi okunan grafiklerin listesi (insan PDF'le karşılaştırır) ve `--pdf` verilirse
"Grafik N / Şekil N" başlığı geçen ama şekil kaydı olmayan sayfalar.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

BASLIK_RE = re.compile(r"^\s*(Grafik|Şekil|Sekil|Figür|Figure|Chart)\s*\d+", re.IGNORECASE)
DURUM_ACIKLAMA = {
    "vektor_etiket": "veri grafikteki yazılı etiketlerden okundu (kesin değer)",
    "yalniz_etiket": "sayısal etiketler var ama çubuk/dilim eşlemesi yapılamadı; veri okunmadı",
    "goruntu_veri_yok": "görüntü (raster) ya da yazısı çizime çevrilmiş grafik; veri okunmadı",
    "veri_yok": "başlıklı şekil (akış şeması, diyagram); veri beklenmez",
}


def oku(yol: Path) -> list[dict]:
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def baslikli_sayfalar(pdf: Path) -> list[int]:
    import pymupdf

    return [
        i
        for i, p in enumerate(pymupdf.open(pdf), start=1)
        if any(BASLIK_RE.match(b[4]) for b in p.get_text("blocks"))
    ]


def ozet(sekiller: list[dict], baslikli: list[int] | None = None) -> str:
    satir = [
        "# Şekil ve grafik çıkarımı özeti",
        "",
        f"- Kayıt: {len(sekiller)} · tür: {dict(Counter(s['tur'] for s in sekiller))}",
    ]
    for durum, n in sorted(Counter(s["veri_durumu"] for s in sekiller).items()):
        satir.append(f"- `{durum}`: {n} ({DURUM_ACIKLAMA[durum]})")
    if baslikli is not None:
        kapsanan = {s["sayfa"] for s in sekiller}
        satir.append(
            f"- Başlıklı sayfa: {len(baslikli)} · şekil kaydı olmayan: {[p for p in baslikli if p not in kapsanan] or 'yok'}"
        )
    veri = [s for s in sekiller if s["veri"]]
    satir += ["", "## Verisi okunan grafikler (PDF ile karşılaştır)", "",
              "| sekil_id | sayfa | başlık | değer sayısı | eşleşmeyen etiket | ilk değerler | doğru mu? |",
              "|---|---|---|---|---|---|---|"]  # fmt: skip
    for s in veri:
        ilk = "; ".join(
            f"{v['kategori'] or '?'}{'/' + v['seri'] if v['seri'] else ''}={v['ham']}" for v in s["veri"][:4]
        )
        satir.append(f"| {s['sekil_id']} | {s['sayfa']} | {s['baslik'][:40].replace('|', '/')} | {len(s['veri'])} | "
                     f"{s['eslesmeyen_etiket']} | {ilk.replace('|', '/')} | |")  # fmt: skip
    return "\n".join(satir) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("figures", type=Path)
    ap.add_argument("--pdf", type=Path)
    a = ap.parse_args(argv)
    if not a.figures.exists():
        print(f"dosya yok: {a.figures}", file=sys.stderr)
        return 1
    print(ozet(oku(a.figures), baslikli_sayfalar(a.pdf) if a.pdf else None), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
