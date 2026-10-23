#!/usr/bin/env python3
"""PDF → yapısal tablolar, olgular ve şekiller (R-TAB-01…04, S28; ADR-014).

    python pipelines/structure.py <rapor.pdf> --rapor-id karel-2025 --out-dir data/processed/karel-2025 \
        [--motor pymupdf|docling] [--paragraflar data/processed/karel-2025/paragraphs.jsonl]

Çıktılar (`--out-dir` altında, satır başına bir kayıt; şema `tools/tablo_kurallari.py`):
- `tables.jsonl`  : tablo ızgaraları (hücre konumu, kapsamı, başlık rolü, sayfa, koordinat)
- `facts.jsonl`   : olgular (değer, birim, satır/sütun yolu, dönem, kaynak hücre)
- `figures.jsonl` : şekil ve grafikler (vektör grafikte etiketten okunan veri; görüntüde veri yok)

`paragraphs.jsonl` değişmez (pilot örneklemi ve kör etiketler ona bağlıdır). `--paragraflar` verilirse
her tablo, aynı sayfadaki `tur=tablo` birimine `paragraf_id` ile bağlanır.

`docling` motoru isteğe bağlıdır (`requirements-extract.txt`; yerel çalışır, belge dışarı gönderilmez).
Kurulu değilse açık bir hata verir; sessizce başka motora geçmez.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_KOK = Path(__file__).resolve().parent.parent
for _yol in (_KOK / "tools", _KOK / "services" / "report-service", _KOK / "pipelines"):
    if str(_yol) not in sys.path:
        sys.path.insert(0, str(_yol))

import figures as fg  # noqa: E402
import tables as tb  # noqa: E402

CHART_SINIFLARI = {"bar_chart", "line_chart", "pie_chart", "stacked_bar_chart", "flow_chart", "scatter_chart",
                   "heatmap", "area_chart", "chart"}  # fmt: skip
VERI_GRAFIKLERI = CHART_SINIFLARI - {"flow_chart"}


def _bitis(metin: str) -> str:
    return " ".join(metin.split())


def paragraflara_bagla(tablolar: list[dict], birimler: list[dict]) -> None:
    """Her tabloyu, ilk sayfasındaki `tur=tablo` birimlerinden metnini içerene bağlar (yerinde).

    Bire birdir: bir paragraf birimi en çok bir tabloya bağlanır. İpucu, başlık ve ilk dolu hücrelerdir;
    `extract.py` ile bu modül başlığı farklı seçebildiği için başlık tutmazsa yalnızca hücrelerle denenir.
    """
    kullanilan: set[str] = set()
    for t in tablolar:
        adaylar = [u for u in birimler if u["tur"] == "tablo" and u["sayfa"] == t["sayfalar"][0]]
        hucreler = [_bitis(h["metin"]) for h in t["hucreler"] if h["metin"].strip()][:3]
        denemeler = ([[_bitis(t["baslik"]), *hucreler[:1]]] if t["baslik"] else []) + [hucreler[:2]]
        for ipucu in denemeler:
            u = next(
                (
                    u
                    for u in adaylar
                    if u["paragraf_id"] not in kullanilan
                    and ipucu
                    and all(i in _bitis(u["metin"]) for i in ipucu)
                ),
                None,
            )
            if u is not None:
                t["paragraf_id"] = u["paragraf_id"]
                kullanilan.add(u["paragraf_id"])
                break


def _docling_tablolari_ve_resimleri(pdf: Path, rapor_id: str):  # pragma: no cover - isteğe bağlı bağımlılık
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling_core.types.doc import PictureItem, TableItem
    except ImportError as e:
        raise SystemExit(
            f"docling kurulu değil ({e}); `pip install -r requirements-extract.txt` (ADR-014)"
        ) from e
    opt = PdfPipelineOptions(do_table_structure=True, do_ocr=False, do_picture_classification=True)
    opt.table_structure_options.mode = TableFormerMode.ACCURATE
    opt.table_structure_options.do_cell_matching = True
    conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opt)})
    doc = conv.convert(pdf).document
    tablolar, resimler, sira = [], [], Counter()
    for item, _ in doc.iterate_items():
        if not item.prov:
            continue
        pr = item.prov[0]
        h = doc.pages[pr.page_no].size.height
        bbox = list(pr.bbox.to_top_left_origin(h).as_tuple())
        if isinstance(item, TableItem):
            t = tb.docling_tablosu(
                item.data.model_dump(), rapor_id, sayfa=pr.page_no, sira=sira[pr.page_no] + 1, bbox=bbox,
                baslik=item.caption_text(doc), sayfa_yuksekligi=h,
            )  # fmt: skip
            if t is None:
                continue
            sira[pr.page_no] += 1  # boş tablo sırayı tüketmez
            tablolar.append(t)
        elif isinstance(item, PictureItem):
            sinif = None
            meta = getattr(item, "meta", None)
            if meta is not None and getattr(meta, "classification", None) is not None:
                p = meta.classification.predictions[0]
                sinif = {"ad": p.class_name, "guven": round(float(p.confidence), 3)}
            resimler.append(
                {"sayfa": pr.page_no, "bbox": bbox, "baslik": item.caption_text(doc), "sinif": sinif}
            )
    return tablolar, resimler


def _cakisma(a, b) -> float:
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    kesisim = (x1 - x0) * (y1 - y0)
    return kesisim / min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))


def resimleri_ekle(sekiller: list[dict], resimler: list[dict], rapor_id: str) -> list[dict]:
    """Docling resim sınıflarını şekillere ekler; PyMuPDF'in bulmadığı grafik resimleri yeni kayıt olur."""
    for r in resimler:
        sinif = r["sinif"]
        es = [s for s in sekiller if s["sayfa"] == r["sayfa"] and _cakisma(s["bbox"], r["bbox"]) >= 0.5]
        if es:
            for s in es:
                s["sinif"] = sinif
            continue
        if not sinif or sinif["ad"] not in CHART_SINIFLARI:
            continue  # fotoğraf, logo, simge: şekil kaydı açılmaz
        tur = "grafik" if sinif["ad"] in VERI_GRAFIKLERI else "sekil"
        s = fg._kayit(rapor_id, r["sayfa"], 0, r["bbox"], tur, r["baslik"], "", [], "goruntu_veri_yok", 0, "docling",
                      ["goruntu_veri_cikarilmadi"])  # fmt: skip
        s["sinif"] = sinif
        sekiller.append(s)
    sekiller.sort(key=lambda s: (s["sayfa"], s["bbox"][1], s["bbox"][0]))
    sayac: Counter[int] = Counter()
    for s in sekiller:
        sayac[s["sayfa"]] += 1
        s["sekil_id"] = f"{rapor_id}-g{s['sayfa']:03d}-{sayac[s['sayfa']]:02d}"
    return sekiller


def calistir(pdf: Path, rapor_id: str, motor: str = "pymupdf", paragraflar: Path | None = None) -> dict:
    import pymupdf

    doc = pymupdf.open(pdf)
    yukseklik = {i: p.rect.height for i, p in enumerate(doc, start=1)}
    resimler: list[dict] = []
    if motor == "docling":
        tablolar, resimler = _docling_tablolari_ve_resimleri(pdf, rapor_id)
        tablolar = [tb.denetle(t, len(doc)) for t in tb.sayfalari_birlestir(tablolar, yukseklik)]
    elif motor == "pymupdf":
        tablolar = tb.cikar(pdf, rapor_id)
    else:
        raise ValueError(f"bilinmeyen motor: {motor}")
    if paragraflar is not None:
        birimler = [json.loads(s) for s in paragraflar.read_text(encoding="utf-8").splitlines() if s.strip()]
        paragraflara_bagla(tablolar, birimler)
    alanlar: dict[int, list[list[float]]] = {}
    for t in tablolar:
        for p in t["parcalar"]:
            alanlar.setdefault(p["sayfa"], []).append(p["bbox"])
    sekiller = resimleri_ekle(fg.cikar(pdf, rapor_id, alanlar), resimler, rapor_id)
    return {
        "tablolar": tablolar,
        "olgular": [o for t in tablolar for o in tb.olgular(t)],
        "sekiller": sekiller,
    }


def yaz(sonuc: dict, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    yollar = {
        "tablolar": out_dir / "tables.jsonl",
        "olgular": out_dir / "facts.jsonl",
        "sekiller": out_dir / "figures.jsonl",
    }
    for anahtar, yol in yollar.items():
        tmp = yol.with_suffix(".jsonl.tmp")
        with tmp.open("w", encoding="utf-8", newline="\n") as fh:
            for kayit in sonuc[anahtar]:
                fh.write(json.dumps(kayit, ensure_ascii=False) + "\n")
        tmp.replace(yol)
    return yollar


def _utf8_cikti() -> None:
    """Windows'ta yönlendirilen çıktı cp1254 olabilir; '→', '₂' yazarken çökmesin (inceleme bulgu 15)."""
    for akim in (sys.stdout, sys.stderr):
        if hasattr(akim, "reconfigure"):
            akim.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str]) -> int:
    _utf8_cikti()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--rapor-id", required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--motor", choices=["pymupdf", "docling"], default="pymupdf")
    ap.add_argument("--paragraflar", type=Path)
    args = ap.parse_args(argv)
    sonuc = calistir(args.pdf, args.rapor_id, args.motor, args.paragraflar)
    yollar = yaz(sonuc, args.out_dir)
    t, o, s = sonuc["tablolar"], sonuc["olgular"], sonuc["sekiller"]
    print(
        f"{len(t)} tablo ({dict(Counter(x['motor'] for x in t))}, birleşik {sum(len(x['sayfalar']) > 1 for x in t)}, "
        f"uyarılı {sum(bool(x['uyarilar']) for x in t)}), {len(o)} olgu (birimli {sum(x['birim'] is not None for x in o)}, "
        f"dönemli {sum(x['donem'] is not None for x in o)}), {len(s)} şekil "
        f"({dict(Counter(x['veri_durumu'] for x in s))}) → {yollar['tablolar'].parent}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
