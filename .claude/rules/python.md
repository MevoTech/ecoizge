---
paths:
  - "**/*.py"
---

# Python kuralları

- Python ≥ 3.11. Biçim ve lint: `ruff` (yapılandırma `pyproject.toml`'da). PostToolUse hook'u düzenlenen dosyada `ruff format` koşar.
- Paket adları servis bazında ayrıdır: `report_service`, `forecast_service`, `review_ui`. Genel `app` adı kullanılmaz.
- Her modülün testi kendi servisinin `tests/` dizininde ya da kökteki `tests/` altında olur. Test adı veya docstring ilgili R-* kimliğini içerir.
- Rastgelelik içeren her kod `seed` parametresi alır.
- Sayı, birim ve tarih ayrıştırması yalnızca `report_service.verify.numbers` üzerinden yapılır; aynı mantık başka yerde tekrar yazılmaz.
- Gizli değerler `os.environ`'dan okunur, koda yazılmaz.
