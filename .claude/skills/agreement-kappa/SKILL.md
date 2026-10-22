---
name: agreement-kappa
description: 'Etiketleyiciler arası uyumu ölçmek için kullan: ağırlıklı Cohen''s κ ve anlaşmazlık listesi.'
allowed-tools: Bash(python tools/kappa.py *)
---

# agreement-kappa

## Komut
```
python tools/kappa.py <etiketA.csv> <etiketB.csv> --weights quadratic --out reports/experiments/kappa-<tarih>.md
```

## Yöntem
- Eşleme anahtarı: (`paragraf_id`, `madde_id`). Bir tarafta olmayan çift `NONE` sayılır.
- Sıralı ölçek: NONE=0, 1=1, 2=2. `U` sıralı ölçeğe girmez; U satırları ayrı sayılır ve raporlanır.
- κ insan–insan ve insan–model ayrı raporlanır (B6).
- 50 paragraf κ için küçük: rapora örneklem büyüklüğünü ve anlaşmazlık listesini yaz; amaç kılavuz belirsizliğini bulmak.

## Kontrol listesi
- [ ] Hangi dosyaların karşılaştırıldığı ve satır sayıları raporda
- [ ] Anlaşmazlık listesi kılavuz v1 tartışmasına girdi
