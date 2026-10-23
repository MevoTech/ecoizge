#!/usr/bin/env python3
"""Katalog ve etiket CSV doğrulayıcısı (R-KAT-01, R-ETK-01).

Kullanım:
    python tools/validate_data.py                 # data/catalog ve data/labels altındaki tüm CSV'ler
    python tools/validate_data.py <dosya> [...]   # yalnızca verilen dosyalar

Dosya türü başlık satırından anlaşılır. Hata varsa her hatayı yazar ve 1 ile çıkar.
İzin verilen değerler etiketleme kılavuzu (§3) ve katalog şemasıyla aynıdır.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATALOG_HEADER = [
    "madde_id", "standart", "bolum", "madde_ref", "baslik", "gereklilik_ozeti",
    "zorunluluk", "veri_turu", "profil", "not", "dogrulama",
]  # fmt: skip
LABEL_HEADER = [
    "etiket_id", "tur", "rapor_id", "sirket", "yil", "paragraf_id", "sayfa", "bolum_basligi",
    "metin", "madde_id", "karsilama", "guven", "gerekce", "etiketleyen", "kaynak", "tarih",
]  # fmt: skip

CATALOG_HEADER_V1 = [*CATALOG_HEADER, "ust_madde"]  # katalog v1: alt unsurlar (ADR-008)
STANDARTLAR = {"TSRS 1", "TSRS 2", "VSME", "GRI"}
ZORUNLULUK = {"zorunlu", "koşullu", "isteğe bağlı"}
VERI_TURU = {"anlatı", "sayısal", "tablo", "karma", "evet/hayır"}
PROFIL = {"TSRS1", "TSRS2", "VSME-Temel", "VSME-Kapsamlı", "GRI"}
DOGRULAMA_RE = re.compile(r"^resmi_metin_\d{4}-\d{2}-\d{2}$")

TUR = {"paragraf", "rapor_duzeyi"}
KARSILAMA = {"paragraf": {"2", "1", "U", "NONE"}, "rapor_duzeyi": {"0"}}
KAYNAK = {"insan", "model_onerisi", "insan_onayli"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        return [], []
    header, body = rows[0], rows[1:]
    errors_rows = [dict(zip(header, r, strict=False)) | {"__len__": str(len(r))} for r in body]
    return header, errors_rows


def latest_catalog_ids(root: Path = ROOT) -> set[str]:
    files = sorted((root / "data" / "catalog").glob("catalog_v*.csv"))
    if not files:
        return set()
    _, rows = read_csv(files[-1])
    return {r["madde_id"] for r in rows}


def validate_catalog(path: Path, header: list[str], rows: list[dict[str, str]]) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    for i, r in enumerate(rows, start=2):
        loc = f"{path.name}:{i}"
        if int(r["__len__"]) != len(header):
            errs.append(f"{loc}: {r['__len__']} sütun, beklenen {len(header)}")
            continue
        mid = r["madde_id"]
        if not mid:
            errs.append(f"{loc}: madde_id boş")
        elif mid in seen:
            errs.append(f"{loc}: yinelenen madde_id {mid}")
        seen.add(mid)
        for col in ("baslik", "gereklilik_ozeti", "madde_ref", "bolum"):
            if not r[col].strip():
                errs.append(f"{loc}: {col} boş")
        checks = [
            ("standart", STANDARTLAR),
            ("zorunluluk", ZORUNLULUK),
            ("veri_turu", VERI_TURU),
            ("profil", PROFIL),
        ]
        for col, allowed in checks:
            if r[col] not in allowed:
                errs.append(f"{loc}: {col}={r[col]!r} izinli değil {sorted(allowed)}")
        if not DOGRULAMA_RE.match(r["dogrulama"]):
            errs.append(f"{loc}: dogrulama={r['dogrulama']!r} 'resmi_metin_YYYY-AA-GG' değil")
    ids = {r["madde_id"] for r in rows}
    for i, r in enumerate(rows, start=2):
        parent = r.get("ust_madde", "")
        if parent and (parent not in ids or parent == r["madde_id"]):
            errs.append(f"{path.name}:{i}: ust_madde={parent!r} bu katalogda yok ya da kendisi")
    return errs


def validate_labels(
    path: Path, header: list[str], rows: list[dict[str, str]], catalog_ids: set[str]
) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    for i, r in enumerate(rows, start=2):
        loc = f"{path.name}:{i}"
        if int(r["__len__"]) != len(header):
            errs.append(f"{loc}: {r['__len__']} sütun, beklenen {len(header)}")
            continue
        eid = r["etiket_id"]
        if not eid:
            errs.append(f"{loc}: etiket_id boş")
        elif eid in seen:
            errs.append(f"{loc}: yinelenen etiket_id {eid}")
        seen.add(eid)
        tur = r["tur"]
        if tur not in TUR:
            errs.append(f"{loc}: tur={tur!r} izinli değil {sorted(TUR)}")
            continue
        if r["karsilama"] not in KARSILAMA[tur]:
            allowed = sorted(KARSILAMA[tur])
            errs.append(f"{loc}: {tur} için karsilama={r['karsilama']!r} izinli değil {allowed}")
        mid = r["madde_id"]
        if mid == "NONE":
            if r["karsilama"] != "NONE":
                errs.append(f"{loc}: madde_id=NONE ise karsilama=NONE olmalı")
        elif catalog_ids and mid not in catalog_ids:
            errs.append(f"{loc}: madde_id {mid!r} katalogda yok")
        if tur == "paragraf" and not r["paragraf_id"]:
            errs.append(f"{loc}: paragraf satırında paragraf_id boş")
        if r["kaynak"] not in KAYNAK:
            errs.append(f"{loc}: kaynak={r['kaynak']!r} izinli değil {sorted(KAYNAK)}")
        if r["guven"]:
            try:
                g = float(r["guven"])
                if not 0.0 <= g <= 1.0:
                    raise ValueError
            except ValueError:
                errs.append(f"{loc}: guven={r['guven']!r} [0,1] aralığında sayı değil")
        if r["kaynak"] == "model_onerisi":
            if not r["guven"]:
                errs.append(f"{loc}: model önerisinde guven zorunlu")
            if not r["gerekce"].strip():
                errs.append(f"{loc}: model önerisinde gerekce zorunlu")
        if not r["etiketleyen"]:
            errs.append(f"{loc}: etiketleyen boş")
        try:
            date.fromisoformat(r["tarih"])
        except ValueError:
            errs.append(f"{loc}: tarih={r['tarih']!r} YYYY-AA-GG değil")
    return errs


def validate_paragraph_records(path: Path, catalog_ids: set[str] | None = None) -> list[str]:
    """Kör etiketlemenin paragraf kayıtları (`*.paragraf.jsonl`, ADR-013).

    Kurallar `tools/etiket_kurallari.py`'dan gelir; kör etiketleme ekranı da aynı fonksiyonu kullanır.
    Ayrıca yanındaki çekirdek CSV ile çapraz denetim:
    - CSV olmalı;
    - CSV'deki her paragrafın kaydı olmalı ve tersi;
    - rapor_id ve etiketleyen aynı olmalı;
    - kanıt metni, CSV'deki metnin aynı kuralla bölünmüş hâliyle eşleşmeli.
    """
    import etiket_kurallari as ek

    sema = ek.sema_oku()
    errs: list[str] = []
    core = path.with_name(path.name.replace(".paragraf.jsonl", ".csv"))
    if not core.exists():
        return [f"{path}: çekirdek CSV yok ({core.name}); paragraf kaydı tek başına geçerli değil"]
    _, rows = read_csv(core)
    levels: dict[str, dict[str, str]] = {}
    core_rows: dict[str, dict[str, str]] = {}
    for r in rows:
        levels.setdefault(r["paragraf_id"], {})
        core_rows.setdefault(r["paragraf_id"], r)
        if r["madde_id"] != "NONE":
            levels[r["paragraf_id"]][r["madde_id"]] = r["karsilama"]
    seen: set[str] = set()
    with path.open(encoding="utf-8-sig") as fh:
        lines = [ln for ln in fh if ln.strip()]
    for i, line in enumerate(lines, start=1):
        where = f"{path}:{i}"
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            errs.append(f"{where}: geçersiz JSON ({exc.msg})")
            continue
        if not isinstance(rec, dict):
            errs.append(f"{where}: kayıt bir JSON nesnesi olmalı")
            continue
        missing = ek.ALANLAR - rec.keys()
        if missing:
            errs.append(f"{where}: eksik alan {sorted(missing)}")
            continue
        pid = rec["paragraf_id"]
        if pid in seen:
            errs.append(f"{where}: yinelenen paragraf_id {pid}")
        seen.add(pid)
        if rec["sema_surumu"] != sema["sema_surumu"]:
            errs.append(f"{where}: şema sürümü {rec['sema_surumu']} ≠ {sema['sema_surumu']}")
        if not isinstance(rec["cumle_sayisi"], int) or isinstance(rec["cumle_sayisi"], bool):
            errs.append(f"{where}: cumle_sayisi tam sayı olmalı")
            continue
        if pid not in levels:
            errs.append(f"{where}: {pid} çekirdek CSV'de yok")
            continue
        errs += [
            f"{where}: {h}"
            for h in ek.kural_hatalari(
                levels[pid], rec["beyan_turleri"], rec["kanit"], rec["belirsizlik"], rec["emin"],
                rec["cumle_sayisi"], sema,
            )
        ]  # fmt: skip
        satir = core_rows[pid]
        for alan in ("rapor_id", "etiketleyen"):
            if rec[alan] != satir[alan]:
                errs.append(f"{where}: {alan} çekirdek CSV ile farklı ({rec[alan]!r} ≠ {satir[alan]!r})")
        if isinstance(rec["kanit"], dict) and isinstance(rec["kanit_metni"], dict):
            cumleler = ek.cumlelere_bol(satir["metin"], rec["birim_turu"])
            for madde, idx in rec["kanit"].items():
                metinler = rec["kanit_metni"].get(madde)
                if not isinstance(metinler, list) or len(metinler) != len(idx):
                    errs.append(f"{where}: {madde} kanıt metni ile numaraları uyuşmuyor")
                elif rec["bolme_surumu"] == ek.BOLME_SURUMU and any(
                    not isinstance(j, int) or not 1 <= j <= len(cumleler) or cumleler[j - 1] != m
                    for j, m in zip(idx, metinler, strict=True)
                ):
                    errs.append(f"{where}: {madde} kanıt metni paragraftaki cümleyle eşleşmiyor")
    for pid in sorted(levels.keys() - seen):
        errs.append(f"{path}: {pid} için paragraf kaydı yok (çekirdek CSV'de var)")
    return errs


def validate_file(path: Path, catalog_ids: set[str] | None = None) -> list[str]:
    if path.name.endswith(".paragraf.jsonl"):
        return validate_paragraph_records(path, catalog_ids)
    header, rows = read_csv(path)
    if header in (CATALOG_HEADER, CATALOG_HEADER_V1):
        return validate_catalog(path, header, rows)
    if header == LABEL_HEADER:
        ids = latest_catalog_ids() if catalog_ids is None else catalog_ids
        return validate_labels(path, header, rows, ids)
    from rapor_derlemi import ALANLAR, denetle  # derlem manifesti (S03)

    if header == ALANLAR:
        return [f"{path}: {h}" for h in denetle(rows)]
    return [f"{path}: tanınmayan başlık {header[:4]}…"]


def default_files(root: Path = ROOT) -> list[Path]:
    files = sorted((root / "data" / "catalog").glob("*.csv"))
    files += sorted((root / "data" / "labels").rglob("*.csv"))
    files += sorted((root / "data" / "labels").rglob("*.paragraf.jsonl"))
    files += sorted((root / "data" / "raw" / "public").glob("KAYNAKLAR.csv"))
    return files


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv] if argv else default_files()
    all_errs: list[str] = []
    for f in files:
        errs = validate_file(f)
        all_errs += errs
        print(f"{'OK  ' if not errs else 'HATA'} {f} ({len(errs)} hata)")
    for e in all_errs:
        print("  -", e)
    return 1 if all_errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
