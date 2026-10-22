#!/usr/bin/env python3
"""PDF → paragraf/tablo çıkarımı (R-PDF-01, S04). Bağımlılık: PyMuPDF (requirements-train.txt).

    python pipelines/extract.py <rapor.pdf> --rapor-id karel-2025 --out data/processed/karel-2025/paragraphs.jsonl

Çıktı (her satır bir birim; `pdf-extract` skill'indeki şema):
    {"paragraf_id", "rapor_id", "sayfa", "bolum_basligi", "tur": "paragraf"|"tablo", "metin", "kaynak": "metin"}

Yapılanlar, sırasıyla:
1. Tablolar `page.find_tables()` ile bulunur; tablo + hemen üstündeki kısa başlık tek birim olur (kılavuz §2).
2. Tablo alanına düşen metin blokları paragraf olarak tekrar yazılmaz.
3. Sayfaların üst/alt %8'lik bandında, sayfaların ≥ yarısında tekrarlanan metin (rakamlar
   normalleştirilerek) üst bilgi / alt bilgi sayılıp atılır.
4. Gövde yazı boyutu (karakter ağırlıklı en sık boyut) bulunur; ≥ 1.15 katı, kısa ve nokta ile
   bitmeyen bloklar başlık sayılır ve sonraki birimlerin `bolum_basligi` alanına yazılır.
5. Satır sonu tirelemesi birleştirilir ("sürdürüle-" + "bilirlik" → "sürdürülebilirlik").
6. Metin katmanı olmayan sayfalar `ocr_gerekli` listesine yazılır (computer vision gerekir).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

BAND = 0.08  # üst/alt bilgi bandı (sayfa yüksekliğinin oranı)
HEADING_RATIO = 1.15
MIN_CHARS = 3


@dataclass
class Result:
    units: list[dict] = field(default_factory=list)
    ocr_gerekli: list[int] = field(default_factory=list)
    atilan_ust_alt: int = 0


def _norm(text: str) -> str:
    return re.sub(r"\d+", "#", re.sub(r"\s+", " ", text)).strip().lower()


def join_lines(lines: list[str]) -> str:
    """Satırları birleştirir; satır sonu tirelemesini (küçük harfle devam) kaldırır."""
    out = ""
    for line in (s.strip() for s in lines):
        if not line:
            continue
        if out.endswith("-") and line[:1].islower():
            out = out[:-1] + line
        else:
            out = f"{out} {line}" if out else line
    return out


def _blocks(page) -> list[dict]:
    data = page.get_text("dict")
    blocks = []
    for b in data["blocks"]:
        if b.get("type") != 0:
            continue
        lines, sizes = [], Counter()
        for ln in b["lines"]:
            text = "".join(sp["text"] for sp in ln["spans"])
            lines.append(text)
            for sp in ln["spans"]:
                sizes[round(sp["size"], 1)] += len(sp["text"].strip())
        text = join_lines(lines)
        if len(text) >= MIN_CHARS:
            size = sizes.most_common(1)[0][0] if sizes else 0.0
            blocks.append({"bbox": b["bbox"], "text": text, "size": size, "chars": sizes})
    return blocks


def _inside(bbox, rect) -> bool:
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return rect[0] <= cx <= rect[2] and rect[1] <= cy <= rect[3]


def _table_text(page, table) -> str:
    """Hücre metnini hücre alanından okur.

    `table.extract()` kullanılmaz: Türkçe binlik ayracını bozar ("12.450" → "12 450 .";
    tests/pipelines/test_extract.py ile yakalandı, 2026-10-22).
    """
    import pymupdf

    out = []
    for row in table.rows:
        cells = []
        for bbox in row.cells:
            text = page.get_text("text", clip=pymupdf.Rect(bbox)) if bbox else ""
            cells.append(re.sub(r"\s+", " ", text).strip())
        if any(cells):
            out.append(" | ".join(cells))
    return "\n".join(out)


def extract(pdf_path: Path, rapor_id: str) -> Result:
    import pymupdf  # isteğe bağlı bağımlılık; yalnızca çıkarımda gerekir

    doc = pymupdf.open(pdf_path)
    pages = []
    for page in doc:
        tables = [t for t in page.find_tables().tables]
        pages.append({"page": page, "blocks": _blocks(page), "tables": tables, "h": page.rect.height})

    # 3. tekrarlanan üst/alt bilgi
    band_counts: Counter[str] = Counter()
    for p in pages:
        seen = {_norm(b["text"]) for b in p["blocks"] if _in_band(b["bbox"], p["h"])}
        band_counts.update(seen)
    repeated = {t for t, c in band_counts.items() if len(pages) >= 2 and c >= max(2, len(pages) / 2)}

    # 4. gövde yazı boyutu
    body_sizes: Counter[float] = Counter()
    for p in pages:
        for b in p["blocks"]:
            body_sizes.update(b["chars"])
    body = body_sizes.most_common(1)[0][0] if body_sizes else 0.0

    res = Result()
    heading = ""
    for pno, p in enumerate(pages, start=1):
        if not p["blocks"] and not p["tables"]:
            if p["page"].get_images():
                res.ocr_gerekli.append(pno)
            continue
        rects = [tuple(t.bbox) for t in p["tables"]]
        items: list[tuple[float, str, dict]] = []
        captions: set[int] = set()
        for t in p["tables"]:
            cap = ""
            above = [
                (i, b)
                for i, b in enumerate(p["blocks"])
                if b["bbox"][3] <= t.bbox[1] + 1 and t.bbox[1] - b["bbox"][3] < 30 and len(b["text"]) < 120
            ]
            if above:
                i, b = max(above, key=lambda x: x[1]["bbox"][3])
                cap, _ = b["text"], captions.add(i)
            text = _table_text(p["page"], t)
            items.append((t.bbox[1], "tablo", {"metin": f"{cap}\n{text}".strip()}))
        for i, b in enumerate(p["blocks"]):
            if i in captions or any(_inside(b["bbox"], r) for r in rects):
                continue
            if _in_band(b["bbox"], p["h"]) and _norm(b["text"]) in repeated:
                res.atilan_ust_alt += 1
                continue
            if re.fullmatch(r"\d{1,4}", b["text"]):  # yalnız sayfa numarası
                res.atilan_ust_alt += 1
                continue
            is_heading = (
                body > 0
                and b["size"] >= body * HEADING_RATIO
                and len(b["text"]) < 120
                and not b["text"].endswith(".")
            )
            items.append((b["bbox"][1], "baslik" if is_heading else "paragraf", {"metin": b["text"]}))
        n = 0
        for _, kind, d in sorted(items, key=lambda x: x[0]):
            if kind == "baslik":
                heading = d["metin"]
                continue
            n += 1
            res.units.append(
                {
                    "paragraf_id": f"{rapor_id}-p{pno:03d}-{n:02d}",
                    "rapor_id": rapor_id,
                    "sayfa": pno,
                    "bolum_basligi": heading,
                    "tur": kind,
                    "metin": d["metin"],
                    "kaynak": "metin",
                }
            )
    return res


def _in_band(bbox, height: float) -> bool:
    return bbox[1] < height * BAND or bbox[3] > height * (1 - BAND)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--rapor-id", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    res = extract(args.pdf, args.rapor_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for u in res.units:
            fh.write(json.dumps(u, ensure_ascii=False) + "\n")
    kinds = Counter(u["tur"] for u in res.units)
    print(
        f"{len(res.units)} birim ({dict(kinds)}), atılan üst/alt bilgi: {res.atilan_ust_alt}, "
        f"OCR gereken sayfalar: {res.ocr_gerekli or 'yok'} → {args.out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
