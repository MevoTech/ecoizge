# Orkestrasyon kuralları

Ayrıntılı yönlendirme tablosu: `docs/ORCHESTRATION.md`. Bu dosya tüm ajanlar için bağlayıcı kısa kurallardır.

- Tek ana ajan `engineering-orchestrator`'dır. Alt ajanlar birbirini çağırmaz; ihtiyaç duydukları her şeyi raporlarında orkestratörden ister.
- Her ajan yalnızca `.claude/hooks/write_scopes.json` içindeki kendi alanına yazar. Alan dışı bir değişiklik gerekiyorsa yapma, raporla.
- Aynı ajandan iki örnek paralel çalışacak ve dosya yazacaksa `isolation: worktree` zorunludur.

## Görev paketi

Orkestratör alt ajana şu başlıklarla görev verir. Eksik başlıkla görev verilmez.

```
Görev: <Sxx veya kısa ad>  ·  Gereksinimler: <R-...>
Amaç: <tek cümle>
Kapsam: <dokunulacak dosyalar / dokunulmayacaklar>
Girdi: <dosyalar, sürümler, komut çıktıları>
Kabul kriterleri: <ölçülebilir maddeler>
Kanıt: <hangi komutun hangi sonucu vermesi gerekir>
Sınırlar: <süre, araç, onay gerektirenler>
```

## Rapor biçimi

Her alt ajan ve orkestratör kullanıcıya şu biçimde döner:

```
Sonuç: TAMAM | KISMİ | BAŞARISIZ | ENGELLENDİ
Yapılanlar: <dosya → değişiklik>
Kanıt: <komut → çıkış kodu, özet çıktı>   (koşulmayan komut yazılmaz)
Test edilemeyenler: <ne, neden>
Açık konular / riskler: <...>
Onay gerektirenler: <karar, seçenekler, öneri>
```

`TAMAM` yalnızca tüm kabul kriterleri kanıtla karşılandıysa yazılır.
