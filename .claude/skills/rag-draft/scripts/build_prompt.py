#!/usr/bin/env python3
"""RAG taslak istemini (system + user) kurar (R-GEN-01/02/03, R-SEC-01, ADR-004, ADR-008).

    python .claude/skills/rag-draft/scripts/build_prompt.py --madde TSRS2-MET-29a-i \
        --catalog data/catalog/catalog_v0.csv --kip yaz --kaynaklar baglam.jsonl --kayitlar kayitlar.json \
        [--mevcut mevcut_paragraf.txt] --out istem.json

`baglam.jsonl` (retrieval çıktısı, company_id ile filtrelenmiş olmalı):
    {"id": "k1", "tur": "standart|rapor|kpi|tahmin", "kaynak": "karel-2025 s.12", "metin": "..."}
`kayitlar.json`: KPI/tahmin kayıtları (forecast_record şeması). **Değerler isteme konmaz**; yalnızca
yer tutucu, birim ve tür listelenir. Böylece model sayıyı göremez ve kopyalayamaz.

Güvenlik: kaynak metnindeki `<`/`>` köşeli tırnağa (‹ ›), `{{`/`}}` ise ⦃ ⦄ işaretine çevrilir. Böylece
belge içinden sahte `</kaynak>` kapatma ya da sahte yer tutucu enjekte edilemez.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "references"
KIPLER = {"yaz", "tamamla"}


def sanitize(text: str) -> str:
    return text.replace("<", "‹").replace(">", "›").replace("{{", "⦃").replace("}}", "⦄")


def placeholder(rec: dict) -> str:
    return f"{{{{KPI:{rec['kpi']}:{rec['yil']}:{rec['veri_turu']}}}}}"


def build(madde: dict, kip: str, sources: list[dict], records: list[dict], mevcut: str = "") -> dict:
    if kip not in KIPLER:
        raise ValueError(f"kip {kip!r} geçersiz; {sorted(KIPLER)}")
    if kip == "tamamla" and not mevcut.strip():
        raise ValueError("tamamla kipinde mevcut metin zorunlu")
    if kip == "yaz" and mevcut.strip():
        raise ValueError("yaz kipinde mevcut metin verilmez (madde eksik)")
    blocks = [
        f'<kaynak id="{i}" tur="{sanitize(s["tur"])}" konum="{sanitize(s.get("kaynak", ""))}">\n{sanitize(s["metin"])}\n</kaynak>'
        for i, s in enumerate(sources, start=1)
    ]
    ph = [
        f"- {placeholder(r)} · {r['kpi']} · {r['yil']} · birim {r['birim']} · tür {r['veri_turu']}"
        + (f" · model {r['model_id']} · senaryo {r['senaryo_id']}" if r["veri_turu"] == "tahmin" else "")
        for r in records
    ]
    user = (REF / "user_prompt.md").read_text(encoding="utf-8")
    fields = {
        "{KIP}": kip,
        "{MADDE_ID}": sanitize(madde["madde_id"]),
        "{STANDART}": sanitize(madde["standart"]),
        "{MADDE_REF}": sanitize(madde["madde_ref"]),
        "{BASLIK}": sanitize(madde["baslik"]),
        "{GEREKLILIK}": sanitize(madde["gereklilik_ozeti"]),
        "{KAYNAKLAR}": "\n\n".join(blocks) or "(kaynak yok)",
        "{YER_TUTUCULAR}": "\n".join(ph) or "(yer tutucu yok: sayısal değer yazma)",
        "{MEVCUT}": sanitize(mevcut) or "(yok)",
    }
    for k, v in fields.items():
        user = user.replace(k, v)
    return {
        "system": (REF / "system_prompt.md").read_text(encoding="utf-8"),
        "user": user,
        "kaynak_sayisi": len(sources),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--madde", required=True)
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--kip", required=True, choices=sorted(KIPLER))
    ap.add_argument("--kaynaklar", type=Path, required=True)
    ap.add_argument("--kayitlar", type=Path, required=True)
    ap.add_argument("--mevcut", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    with args.catalog.open(encoding="utf-8", newline="") as fh:
        madde = next((r for r in csv.DictReader(fh) if r["madde_id"] == args.madde), None)
    if madde is None:
        print(f"HATA: {args.madde} katalogda yok")
        return 1
    with args.kaynaklar.open(encoding="utf-8") as fh:
        sources = [json.loads(x) for x in fh if x.strip()]
    records = json.loads(args.kayitlar.read_text(encoding="utf-8"))
    mevcut = args.mevcut.read_text(encoding="utf-8") if args.mevcut else ""
    out = build(madde, args.kip, sources, records, mevcut)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"istem yazıldı: {len(sources)} kaynak, {len(records)} yer tutucu → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
