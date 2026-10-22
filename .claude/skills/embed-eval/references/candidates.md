# Embedding adayları (başlangıç listesi, 2026-10-22)

Kaynak: TR-MTEB, EMNLP Findings 2025 (https://aclanthology.org/2025.findings-emnlp.471.pdf), Tablo 2. Değerler genel alan Türkçe görevleridir; kendi verimizde yeniden ölçülecektir.

| Model | TR-MTEB ortalama | Retrieval | STS | Not |
|---|---|---|---|---|
| multilingual-e5-large | 66,82 | 60,62 | 81,18 | En iyi ortalama; Colab T4'te yavaş olabilir |
| multilingual-e5-base | 64,26 | 58,29 | 78,37 | Hız/başarı dengesi için güçlü aday |
| multilingual-e5-large-instruct | 65,92 | 57,21 | 81,23 | Talimat öneki gerektirir |
| text-embedding-3-small (OpenAI) | 66,61 | 64,99 | 70,85 | Retrieval'da en iyi. Harici API: yalnızca kamu verisiyle (ADR-011) |
| TR-MTEB yazarlarının Türkçe modeli (ince ayarlı) | 63,42 | 52,75 | 78,44 | Türkçeye özel |
| bert-base-turkish-uncased (BERTurk, ham) | 49,54 | 34,82 | 56,74 | **Taban**: ham BERT retrieval için uygun değil |
| bge-m3 | — | — | — | TR-MTEB'de değerlendirilmemiş; Türkçe başarısı doğrulanmadı |

Model adları ve sürümleri kullanılmadan önce Hugging Face model kartından doğrulanır (lisans, önek, azami uzunluk). 2026 sonrası çıkan Türkçe modeller (ör. arama sonuçlarında görülen yeni Türkçe kodlayıcılar) `researcher` ile ayrıca taranır.
