"""Ağırlıklı Cohen's κ testleri (R-ETK-01). Referans değerler scikit-learn
`cohen_kappa_score` ile bağımsız olarak hesaplandı (2026-10-22) ve sabitlendi."""

import csv
from pathlib import Path

import pytest

from kappa import compare, weighted_kappa

A = [0, 0, 1, 1, 2, 2, 0, 2, 1, 0]
B = [0, 1, 1, 2, 2, 2, 0, 1, 1, 0]


@pytest.mark.parametrize(
    "weights,expected",
    [("quadratic", 0.7692307692), ("linear", 0.6590909091), ("none", 0.552238806)],
)
def test_r_etk_01_matches_reference(weights, expected):
    assert weighted_kappa(A, B, 3, weights) == pytest.approx(expected, abs=1e-9)


def test_perfect_agreement_is_one():
    assert weighted_kappa([0, 1, 2], [0, 1, 2], 3) == pytest.approx(1.0)


def test_rejects_unequal_lengths():
    with pytest.raises(ValueError):
        weighted_kappa([0, 1], [0], 3)


HEADER = [
    "etiket_id",
    "tur",
    "rapor_id",
    "sirket",
    "yil",
    "paragraf_id",
    "sayfa",
    "bolum_basligi",
    "metin",
    "madde_id",
    "karsilama",
    "guven",
    "gerekce",
    "etiketleyen",
    "kaynak",
    "tarih",
]


def _write(path: Path, rows: list[tuple[str, str, str]]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        for i, (pid, mid, k) in enumerate(rows):
            w.writerow(
                dict.fromkeys(HEADER, "")
                | {"etiket_id": f"e{i}", "tur": "paragraf", "paragraf_id": pid, "madde_id": mid}
                | {"karsilama": k, "etiketleyen": "x", "kaynak": "insan", "tarih": "2026-10-22"}
            )
    return path


def test_r_etk_01_missing_pair_counts_as_none_and_u_is_separate(tmp_path):
    a = _write(tmp_path / "a.csv", [("p1", "M1", "2"), ("p2", "M1", "U"), ("p3", "NONE", "NONE")])
    b = _write(tmp_path / "b.csv", [("p1", "M1", "1"), ("p2", "M1", "U"), ("p3", "M2", "1")])
    res = compare(a, b, "quadratic")
    assert res["paragraf_ortak"] == 3
    assert res["u_cift"] == 1
    assert res["olculen"] == 2  # (p1,M1): 2 vs 1 ; (p3,M2): NONE vs 1
    assert {(k, va, vb) for k, va, vb in res["anlasmazlik"]} == {
        (("p1", "M1"), "2", "1"),
        (("p3", "M2"), "NONE", "1"),
    }
