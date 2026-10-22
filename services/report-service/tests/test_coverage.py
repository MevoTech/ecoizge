"""Unsur kapsama testleri (R-GAP-03, ADR-008)."""

import pytest

from report_service.nlp.coverage import Decision, best_level, children_from_catalog, decide, level_from_score

TREE = {"MET-29a-i": ["MET-29a-i-a", "MET-29a-i-b", "MET-29a-i-c"]}  # Kapsam 1 / 2 / 3


@pytest.mark.parametrize(
    "labels,expected",
    [
        (["NONE", "1", "2"], "2"),
        (["NONE", "1"], "1"),
        (["NONE"], "0"),
        ([], "0"),
        (["U", "NONE"], "U"),
        (["U", "1"], "1"),
    ],
)
def test_best_level(labels, expected):
    assert best_level(labels) == expected


def test_r_gap_03_scope_split_across_paragraphs_is_full():
    """Kapsam 1 bir paragrafta, Kapsam 2 bir tabloda, Kapsam 3 muafiyet beyanıyla: madde Tam."""
    leaf = {"MET-29a-i-a": "2", "MET-29a-i-b": "2", "MET-29a-i-c": "2"}
    assert decide("MET-29a-i", TREE, leaf) == Decision("MET-29a-i", "2")


def test_r_gap_03_missing_scope3_is_partial_and_named():
    d = decide("MET-29a-i", TREE, {"MET-29a-i-a": "2", "MET-29a-i-b": "1"})
    assert d.level == "1"
    assert d.eksik_unsurlar == ("MET-29a-i-c",)
    assert d.kismi_unsurlar == ("MET-29a-i-b",)


def test_r_gap_03_nothing_covered_is_missing():
    assert decide("MET-29a-i", TREE, {}).level == "0"


def test_r_gap_03_not_applicable_children():
    assert decide("MET-29a-i", TREE, dict.fromkeys(TREE["MET-29a-i"], "U")).level == "U"
    leaf = {"MET-29a-i-a": "2", "MET-29a-i-b": "2", "MET-29a-i-c": "U"}
    assert decide("MET-29a-i", TREE, leaf).level == "2"


def test_leaf_item_reads_directly():
    assert decide("YON-06a", {}, {"YON-06a": "1"}).level == "1"


@pytest.mark.parametrize("score,expected", [(0.1, "0"), (0.4, "1"), (0.69, "1"), (0.7, "2")])
def test_level_from_score(score, expected):
    assert level_from_score(score, 0.3, 0.7) == expected


def test_level_from_score_rejects_bad_thresholds():
    with pytest.raises(ValueError):
        level_from_score(0.5, 0.8, 0.2)


def test_children_from_catalog():
    rows = [
        {"madde_id": "A", "ust_madde": ""},
        {"madde_id": "A-a", "ust_madde": "A"},
        {"madde_id": "A-b", "ust_madde": "A"},
    ]
    assert children_from_catalog(rows) == {"A": ["A-a", "A-b"]}
