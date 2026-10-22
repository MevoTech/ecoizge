"""Altın küme dondurma/doğrulama testleri (R-ETK-02)."""

from gold_manifest import main


def _gold(tmp_path):
    g = tmp_path / "data" / "gold"
    g.mkdir(parents=True)
    (g / "test.csv").write_text("a\n1\n", encoding="utf-8")
    return g


def test_r_etk_02_no_gold_yet_is_ok(tmp_path):
    assert main(["verify", "--root", str(tmp_path)]) == 0


def test_r_etk_02_unfrozen_files_fail(tmp_path):
    _gold(tmp_path)
    assert main(["verify", "--root", str(tmp_path)]) == 1


def test_r_etk_02_freeze_then_verify_then_tamper(tmp_path):
    g = _gold(tmp_path)
    assert main(["freeze", "--by", "Mehmet Güneş", "--root", str(tmp_path)]) == 0
    assert main(["verify", "--root", str(tmp_path)]) == 0
    (g / "test.csv").write_text("a\n2\n", encoding="utf-8")
    assert main(["verify", "--root", str(tmp_path)]) == 1


def test_r_etk_02_added_file_fails(tmp_path):
    g = _gold(tmp_path)
    main(["freeze", "--by", "x", "--root", str(tmp_path)])
    (g / "extra.csv").write_text("b\n", encoding="utf-8")
    assert main(["verify", "--root", str(tmp_path)]) == 1
