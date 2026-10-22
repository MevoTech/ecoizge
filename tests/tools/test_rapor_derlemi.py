"""Rapor derlemi yerleştirme ve doğrulama testleri (S03, R-PDF-01)."""

import csv
import hashlib
from pathlib import Path

import pytest
import rapor_derlemi as rd

PDF = b"%PDF-1.4\n% sahte ama imzasi dogru\n%%EOF\n"
HTML = b"<html><body>404</body></html>"

TR_METIN = (
    "Şirketimiz 2025 yılı için sera gazı emisyonlarını kapsam 1 ve kapsam 2 olarak raporlamaktadır. "
    "Bu rapor TSRS 2 ile uyumlu olarak hazırlanmış olup iklimle ilgili riskler ve fırsatlar için "
    "yönetim kurulu tarafından gözetim sağlanmaktadır. Ayrıca enerji tüketimi ve su kullanımı da "
    "her yıl ölçülmekte ve hedeflere göre izlenmektedir. "
) * 3
EN_METIN = (
    "The company reports its scope 1 and scope 2 greenhouse gas emissions for the year. "
    "This report is prepared in accordance with IFRS S2 and the board of directors has oversight of "
    "climate-related risks and opportunities. We measure energy and water use, which is tracked "
    "against our targets that are set by the board. "
) * 3


def test_tr_kucuk_turkce_i_kurali():
    assert rd.tr_kucuk("IĞDIR İZMİR") == "ığdır izmir"


@pytest.mark.parametrize(
    "girdi,beklenen",
    [
        ("Batıcım TSRS 25", "baticim-tsrs-25"),
        ("ARÇELİK 2024 TSRS Uyumlu", "arcelik-2024-tsrs-uyumlu"),
        ("Ziraat Bankası_2025  Raporu .pdf", "ziraat-bankasi-2025-raporu-pdf"),
        ("KİLİS 7 ARALIK ÜNİVERSİTESİ", "kilis-7-aralik-universitesi"),
    ],
)
def test_slug_turkce_ascii(girdi, beklenen):
    assert rd.slug(girdi) == beklenen


def test_dil_tahmini():
    assert rd.dil_tahmini(TR_METIN) == "tr"
    assert rd.dil_tahmini(EN_METIN) == "en"
    assert rd.dil_tahmini(TR_METIN + EN_METIN) == "karisik"
    assert rd.dil_tahmini("12 34 56") == "belirsiz"  # taranmış PDF: metin yok


def _satir(**k):
    s = {a: "" for a in rd.ALANLAR}
    s.update(
        rapor_id="sirket-ornek-2025",
        kategori="sirket",
        url="https://ornek.gov.tr/a.pdf",
        dosya_adi="ecoizge__sirket-ornek-2025.pdf",
        durum="planlandi",
    )
    s.update(k)
    return s


def _manifest(tmp_path: Path, satirlar) -> Path:
    m = tmp_path / "KAYNAKLAR.csv"
    rd.yaz(m, satirlar)
    return m


@pytest.fixture
def poppler_yok(monkeypatch):
    monkeypatch.setattr(rd, "sayfa_sayisi", lambda yol: "3")
    monkeypatch.setattr(rd, "ilk_sayfalar_metni", lambda yol: TR_METIN)


def test_yerlestir_tasir_ve_dogrular(tmp_path, poppler_yok):
    indir = tmp_path / "Downloads"
    hedef = tmp_path / "derlem"
    indir.mkdir()
    (indir / "ecoizge__sirket-ornek-2025.pdf").write_bytes(PDF)
    m = _manifest(
        tmp_path,
        [_satir(beklenen_boyut=str(len(PDF))), _satir(rapor_id="sirket-yok-2025", dosya_adi="yok.pdf")],
    )

    sayac = rd.yerlestir(indir, hedef, m)

    assert sayac == {"dogrulandi": 1, "indirilmemiş": 1}
    assert not (indir / "ecoizge__sirket-ornek-2025.pdf").exists()
    tasinan = hedef / "sirket" / "ecoizge__sirket-ornek-2025.pdf"
    assert tasinan.read_bytes() == PDF
    s = rd.oku(m)[0]
    assert s["durum"] == "dogrulandi"
    assert s["sha256"] == hashlib.sha256(PDF).hexdigest()
    assert (s["sayfa"], s["dil"], s["boyut"]) == ("3", "tr", str(len(PDF)))
    assert s["erisim_tarihi"]
    assert rd.denetle(rd.oku(m)) == []


def test_html_hata_sayfasi_reddedilir(tmp_path, poppler_yok):
    indir = tmp_path / "d"
    indir.mkdir()
    (indir / "ecoizge__sirket-ornek-2025.pdf").write_bytes(HTML)
    m = _manifest(tmp_path, [_satir()])
    assert rd.yerlestir(indir, tmp_path / "h", m)["hata"] == 1
    s = rd.oku(m)[0]
    assert s["durum"] == "hata" and "PDF imzası" in s["notlar"] and s["sha256"] == ""


def test_boyut_farki_hata(tmp_path, poppler_yok):
    indir = tmp_path / "d"
    indir.mkdir()
    (indir / "ecoizge__sirket-ornek-2025.pdf").write_bytes(PDF)
    m = _manifest(tmp_path, [_satir(beklenen_boyut="999999")])
    rd.yerlestir(indir, tmp_path / "h", m)
    assert rd.oku(m)[0]["durum"] == "hata"


def test_dogrulanmis_satira_dokunulmaz(tmp_path, poppler_yok):
    s = _satir(durum="dogrulandi", sha256="a" * 64)
    m = _manifest(tmp_path, [s])
    assert rd.yerlestir(tmp_path, tmp_path, m) == {"zaten doğrulanmış": 1}


def test_denetle_hatalari_yakalar():
    satirlar = [
        _satir(),
        _satir(kategori="diger"),  # yinelenen kimlik + geçersiz kategori
        _satir(rapor_id="b", url="http://x", durum="dogrulandi"),
    ]
    hatalar = "\n".join(rd.denetle(satirlar))
    assert "yinelenmiş" in hatalar
    assert "kategori 'diger'" in hatalar
    assert "https değil" in hatalar
    assert "sha256 yok" in hatalar


def test_gercek_poppler_ile(tmp_path):
    """Container'da poppler varsa gerçek bir PDF üret ve sayfa sayısını oku."""
    pytest.importorskip("fitz")
    import fitz

    yol = tmp_path / "a.pdf"
    doc = fitz.open()
    for _ in range(2):
        # Base-14 Helvetica ş/ı glifini taşımaz; metin yalnızca bu yazı tipinin kapsadığı harflerle.
        doc.new_page().insert_text((72, 72), "Rapor için veriler toplandı ve gözden geçirildi.")
    doc.save(yol)
    if not rd.sayfa_sayisi(yol):
        pytest.skip("pdfinfo yok")
    assert rd.sayfa_sayisi(yol) == "2"
    assert "gözden geçirildi" in (rd.ilk_sayfalar_metni(yol) or "")


def test_manifest_basligi_sabit(tmp_path):
    m = _manifest(tmp_path, [])
    with open(m, encoding="utf-8") as f:
        assert next(csv.reader(f)) == rd.ALANLAR


def test_indir_kaldigi_yerden_devam_eder(tmp_path, poppler_yok, monkeypatch):
    istenen = []

    def sahte(url, hedef):
        istenen.append(url)
        if "kirik" in url:
            raise OSError("HTTP Error 404")
        hedef.write_bytes(PDF)

    monkeypatch.setattr(rd, "_indir_url", sahte)
    m = _manifest(
        tmp_path,
        [
            _satir(),
            _satir(rapor_id="b", url="https://x/kirik.pdf", dosya_adi="b.pdf"),
            _satir(rapor_id="c", dosya_adi="c.pdf", beklenen_boyut=str(rd.BUYUK_DOSYA + 1)),
            _satir(rapor_id="d", kategori="kidr", dosya_adi="d.pdf"),
        ],
    )
    sayac = rd.indir(tmp_path / "h", m, kategoriler=("sirket",))
    assert sayac == {"dogrulandi": 1, "hata": 1, "büyük, atlandı": 1}
    durum = {s["rapor_id"]: s for s in rd.oku(m)}
    assert durum["b"]["durum"] == "hata" and "404" in durum["b"]["notlar"]
    assert durum["d"]["durum"] == "planlandi"  # kategori dışı

    istenen.clear()
    rd.indir(tmp_path / "h", m, kategoriler=("sirket",))
    assert istenen == ["https://x/kirik.pdf"]  # doğrulanmış dosya yeniden indirilmez


def test_pdf_imzasi_ilk_1024_baytta_kabul_edilir(tmp_path):
    """KGK'deki Kardemir ve Klimasan 2025 PDF'lerinin başında 27 baytlık Java serileştirme
    öneki var; PDF okuyucular imzayı ilk 1024 baytta arar (2026-10-22'de bulundu)."""
    yol = tmp_path / "a.pdf"
    yol.write_bytes(b"\xac\xed\x00\x05ur\x00\x02[B" + b"\x00" * 17 + PDF)
    assert rd.pdf_mi(yol)
    yol.write_bytes(b"x" * 1100 + PDF)
    assert not rd.pdf_mi(yol)


def test_indir_html_hata_sayfasini_silip_yeniden_dener(tmp_path, poppler_yok, monkeypatch):
    """KGK zaman zaman PDF yerine 1.499 baytlık Error404 sayfası döndürüyor (2026-10-22)."""
    yanitlar = [HTML, PDF]
    monkeypatch.setattr(rd, "_indir_url", lambda url, hedef: hedef.write_bytes(yanitlar.pop(0)))
    m = _manifest(tmp_path, [_satir()])
    assert rd.indir(tmp_path / "h", m) == {"hata": 1}
    assert not (tmp_path / "h" / "sirket" / "ecoizge__sirket-ornek-2025.pdf").exists()
    assert rd.indir(tmp_path / "h", m) == {"dogrulandi": 1}


def test_indir_eksik_aktarimi_silip_yeniden_dener(tmp_path, poppler_yok, monkeypatch):
    """Vekil üzerinden indirilen 5 büyük dosyada 192 bayt eksik geldi; boyut denetimi yakaladı
    (Tüpraş 2024 vb., 2026-10-22)."""
    yanitlar = [PDF[:-3], PDF]
    monkeypatch.setattr(rd, "_indir_url", lambda url, hedef: hedef.write_bytes(yanitlar.pop(0)))
    m = _manifest(tmp_path, [_satir(beklenen_boyut=str(len(PDF)))])
    assert rd.indir(tmp_path / "h", m) == {"hata": 1}
    assert rd.indir(tmp_path / "h", m) == {"dogrulandi": 1}


def test_not_ekle_kaynak_notunu_korur():
    n = rd.not_ekle("KGK listesi", "boyut farklı")
    assert n == "KGK listesi; HATA: boyut farklı"
    assert rd.not_ekle(n, "PDF imzası yok") == "KGK listesi; HATA: PDF imzası yok"
    assert rd.not_ekle(n, "") == "KGK listesi"
    assert rd.not_ekle("", "x") == "HATA: x" and rd.not_ekle("HATA: x", "") == ""


def test_indir_once_denenmemisleri_sonra_hatalilari_isler(tmp_path, poppler_yok, monkeypatch):
    sira = []

    def sahte(url, hedef):
        sira.append(url)
        hedef.write_bytes(PDF)

    monkeypatch.setattr(rd, "_indir_url", sahte)
    m = _manifest(
        tmp_path,
        [
            _satir(rapor_id="a", url="https://x/hatali.pdf", durum="hata"),
            _satir(rapor_id="b", url="https://x/yeni.pdf", dosya_adi="b.pdf"),
        ],
    )
    rd.indir(tmp_path / "h", m)
    assert sira == ["https://x/yeni.pdf", "https://x/hatali.pdf"]
    assert [s["rapor_id"] for s in rd.oku(m)] == ["a", "b"]  # manifest sırası korunur
