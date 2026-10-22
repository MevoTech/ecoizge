---
name: frontend-dev
description: 'React + TypeScript arayüz bileşeni geliştirmek için kullan: formlar, boşluk matrisi, taslak editörü, tahmin paneli. Şu an etkin değil (F3 sonrası).'
---

# frontend-dev

## Durum
**Etkin değil.** `web/` F3'te açılır. Onay arayüzü Streamlit'tir (`label-review`).

## Adımlar
1. Ekranın API uçlarını `docs/API_SPEC.md`'den al; tipleri şemadan üret.
2. Form: React Hook Form + Zod; alanlar katalogdaki `veri_turu`'ndan türetilir (Teknik Kapsam 7).
3. Veri: TanStack Query; hata ve yükleniyor durumları zorunlu.
4. Gerçekleşmiş/tahmin: düz çizgi/kesikli çizgi + rozet (Sunum S-19).
5. Test: Vitest + React Testing Library; bir uçtan uca akış.

## Kontrol listesi
- [ ] `npm run lint`, `npm test` yeşil
- [ ] Klavye ile kullanılabilir, kontrast yeterli
