---
id: S04
baslik: PDF çıkarım hattı v0 ve çıkarım kalite kümesi
faz: F1
durum: bekliyor
sorumlu: ml-engineer
skills: [pdf-extract, computer-vision]
gereksinimler: [R-PDF-01, R-PDF-02]
bagimlilik: [S03]
insan_onayi: QA kümesinin elle kontrolü
---

# S04 · PDF çıkarım hattı v0 ve çıkarım kalite kümesi

**Amaç.** PDF → paragraf/tablo çıkarımı ve ölçülmüş kalite.

## Girdi

3 rapor (S03).

## Çıktı

`pipelines/extract.py`, `data/processed/<rapor>/paragraphs.jsonl`, QA raporu (evaluator).

## Kabul kriterleri

- Çıktı şeması `pdf-extract` skill'indeki gibi
- QA kümesinde (20 sayfa) hata türleri sayılmış
- PyMuPDF / pdfplumber seçimi ölçümle, ADR

## Test komutu

```
python -m pytest -q -k extract
python tools/check_all.py
```

## Kanıt

QA raporu ve ADR.

## Hata durumunda

`.claude/rules/quality-gates.md` §Hata prosedürü. İki deneme başarısızsa orkestratör kullanıcıya seçenek sunar; görev `engelli` yapılır ve nedeni buraya yazılır.

## Kararlar

—
