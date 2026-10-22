---
name: perf-profile
description: 'Performans ölçmek ve darboğaz bulmak için kullan: embedding üretim süresi, vektör sorgu gecikmesi, PDF çıkarım süresi, bellek.'
---

# perf-profile

## Adımlar
1. Ölçülecek senaryoyu ve hedefi yaz (ör. 300 sayfalık rapor < 2 dk çıkarım).
2. Ölç: `python -m cProfile -o out.prof <betik>`; bellek için `tracemalloc`; SQL için `EXPLAIN ANALYZE`.
3. Darboğazı tek değişkenle iyileştir; önce/sonra ölçümünü aynı girdiyle yap.
4. Sonucu `reports/experiments/perf-<tarih>.md` (evaluator) veya görev raporuna yaz.

## Kontrol listesi
- [ ] Önce/sonra aynı makine, aynı girdi
- [ ] Doğruluk değişmedi (ilgili testler yeşil)
