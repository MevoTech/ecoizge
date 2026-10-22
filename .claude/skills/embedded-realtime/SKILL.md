---
name: embedded-realtime
description: 'Gömülü ve gerçek zamanlı sistem tasarımı için kullan: sayaç/sensör veri toplama, zamanlama, kaynak kısıtları. Bu projede kapsam dışı.'
---

# embedded-realtime

## Durum
**Etkin değil.** Sistem şirket verisini form ve dosyayla alır; donanım yok.

## Etkinleşme koşulu
Sayaç/IoT ile otomatik enerji verisi toplama kapsama alınırsa (ADR).

## O durumda kontrol listesi
- Örnekleme hızı ve zaman damgası kaynağı (saat senkronu)
- Kayıp bağlantıda tampon ve yeniden gönderim
- Protokol (MQTT/Modbus) ve kimlik doğrulama
- Veri `olcum_gerceklesmis` tablosuna `kaynak_turu = sayac` ile yazılır
