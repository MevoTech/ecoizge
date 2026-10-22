#!/usr/bin/env python3
"""Boşluk analizi taban çizgisi: TF-IDF benzerlik öznitelikleri + lojistik regresyon (R-GAP-02, deney a).

    python .claude/skills/gap-baseline/scripts/baseline.py --labels data/labels/reviewed/*.csv \
        --catalog data/catalog/catalog_v0.csv --seed 43 --out metrikler.json

Problem tanımı: her (paragraf, madde) çifti için düzey ∈ {0 (NONE), 1 (kısmi), 2 (tam)}.
Onaylı etiket dosyasında bir paragraf için yazılmamış madde → 0. `U` çiftleri değerlendirme dışıdır.

Öznitelikler (çift başına): kelime TF-IDF kosinüsü, karakter 3–5 gram TF-IDF kosinüsü, paragrafın
sayısal yoğunluğu (rakam/sözcük), birim varlığı (tCO2e, MWh, %, m³), log uzunluk.
Model: standartlaştırma + çok sınıflı lojistik regresyon, `class_weight="balanced"`.

Doğrulama: rapor bazında GroupKFold. TF-IDF her katta yalnızca eğitim paragraflarıyla
(+ madde metinleri, sızıntı değil) öğrenilir. Eşikler τ1 ve τ2 eğitim katında, beklenen düzey skoru
s = (P1 + 2·P2)/2 üzerinden F1'i en yüksek yapacak biçimde seçilir ve test katına sabit uygulanır.
Bağımlılık: scikit-learn (requirements-train.txt).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

UNIT_RE = re.compile(r"tco2e?|mwh|kwh|gwh|%|m³|m3|ton\b", re.IGNORECASE)
LEVEL = {"NONE": 0, "1": 1, "2": 2}


def tr_lower(text: str) -> str:
    return text.replace("I", "ı").replace("İ", "i").lower()


def load_pairs(label_files: list[Path], catalog: Path) -> tuple[list[dict], dict[str, str]]:
    with catalog.open(encoding="utf-8", newline="") as fh:
        items = {r["madde_id"]: f"{r['baslik']} {r['gereklilik_ozeti']}" for r in csv.DictReader(fh)}
    paragraphs: dict[str, dict] = {}
    labels: dict[tuple[str, str], str] = {}
    for f in label_files:
        with f.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if r["tur"] != "paragraf":
                    continue
                paragraphs[r["paragraf_id"]] = {"rapor_id": r["rapor_id"], "metin": r["metin"]}
                if r["madde_id"] != "NONE":
                    labels[(r["paragraf_id"], r["madde_id"])] = r["karsilama"]
    pairs = []
    for pid, p in paragraphs.items():
        for mid in items:
            lab = labels.get((pid, mid), "NONE")
            if lab == "U":
                continue
            pairs.append(
                {
                    "paragraf_id": pid,
                    "madde_id": mid,
                    "rapor_id": p["rapor_id"],
                    "metin": p["metin"],
                    "y": LEVEL[lab],
                }
            )
    return pairs, items


def _surface(text: str) -> list[float]:
    words = max(len(text.split()), 1)
    digits = len(re.findall(r"\d+", text))
    return [digits / words, 1.0 if UNIT_RE.search(text) else 0.0, math.log1p(words)]


def featurize(pairs, items, train_texts, seed):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    word = TfidfVectorizer(preprocessor=tr_lower, ngram_range=(1, 2), min_df=1)
    char = TfidfVectorizer(preprocessor=tr_lower, analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    corpus = list(train_texts) + list(items.values())
    word.fit(corpus)
    char.fit(corpus)
    mids = list(items)
    iw, ic = word.transform([items[m] for m in mids]), char.transform([items[m] for m in mids])
    pos = {m: i for i, m in enumerate(mids)}
    texts = sorted({p["metin"] for p in pairs})
    tw, tc = word.transform(texts), char.transform(texts)
    sw, sc = cosine_similarity(tw, iw), cosine_similarity(tc, ic)
    tpos = {t: i for i, t in enumerate(texts)}
    return [
        [
            sw[tpos[p["metin"]], pos[p["madde_id"]]],
            sc[tpos[p["metin"]], pos[p["madde_id"]]],
            *_surface(p["metin"]),
        ]
        for p in pairs
    ]


def best_threshold(scores: list[float], positive: list[bool]) -> float:
    from sklearn.metrics import f1_score

    cands = sorted(set(round(s, 3) for s in scores)) or [0.5]
    return max(cands, key=lambda t: (f1_score(positive, [s >= t for s in scores], zero_division=0), -t))


def run(pairs, items, seed: int = 43, n_splits: int = 5) -> dict:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    groups = [p["rapor_id"] for p in pairs]
    k = min(n_splits, len(set(groups)))
    if k < 2:
        raise ValueError("gruplu doğrulama için en az 2 rapor gerekli")
    y = [p["y"] for p in pairs]
    folds, y_true, y_pred = [], [], []
    for fold, (tr, te) in enumerate(GroupKFold(n_splits=k).split(pairs, y, groups)):
        train_reports = {groups[i] for i in tr}
        test_reports = {groups[i] for i in te}
        assert not train_reports & test_reports, "rapor sızıntısı"
        train_texts = {pairs[i]["metin"] for i in tr}
        X = featurize(pairs, items, train_texts, seed)
        # Ölçekleme zorunlu: ölçeksiz öznitelikte log-uzunluk benzerliği bastırır ve uzun bir paragrafın
        # bütün madde çiftleri "karşılandı" çıkar (tests/skills ile yakalandı, 2026-10-22).
        clf = make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed)
        )
        clf.fit([X[i] for i in tr], [y[i] for i in tr])
        classes = list(clf.classes_)

        def score(rows, clf=clf, classes=classes):
            probs = clf.predict_proba(rows)
            p1 = [r[classes.index(1)] if 1 in classes else 0.0 for r in probs]
            p2 = [r[classes.index(2)] if 2 in classes else 0.0 for r in probs]
            return [(a + 2 * b) / 2 for a, b in zip(p1, p2, strict=True)]

        s_tr = score([X[i] for i in tr])
        tau1 = best_threshold(s_tr, [y[i] >= 1 for i in tr])
        tau2 = max(tau1, best_threshold(s_tr, [y[i] == 2 for i in tr]))
        s_te = score([X[i] for i in te])
        pred = [0 if s < tau1 else (1 if s < tau2 else 2) for s in s_te]
        truth = [y[i] for i in te]
        y_true += truth
        y_pred += pred
        folds.append(
            {
                "kat": fold,
                "test_raporlari": sorted(test_reports),
                "tau1": round(tau1, 3),
                "tau2": round(tau2, 3),
                "f1_makro": round(
                    f1_score(truth, pred, average="macro", labels=[0, 1, 2], zero_division=0), 4
                ),
                "f1_karsilanan": round(
                    f1_score([t >= 1 for t in truth], [p >= 1 for p in pred], zero_division=0), 4
                ),
            }
        )
    return {
        "model": "tfidf-benzerlik+lr",
        "tohum": seed,
        "kat_sayisi": k,
        "cift_sayisi": len(pairs),
        "pozitif_cift": sum(v >= 1 for v in y),
        "f1_makro": round(f1_score(y_true, y_pred, average="macro", labels=[0, 1, 2], zero_division=0), 4),
        "f1_karsilanan": round(
            f1_score([t >= 1 for t in y_true], [p >= 1 for p in y_pred], zero_division=0), 4
        ),
        "katlar": folds,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", type=Path, nargs="+", required=True)
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    pairs, items = load_pairs(args.labels, args.catalog)
    res = run(pairs, items, args.seed, args.folds)
    args.out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"F1 makro {res['f1_makro']} · F1 karşılanan {res['f1_karsilanan']} · {res['kat_sayisi']} kat → {args.out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
