from pathlib import Path

# Temel Dizin Yapısı 
DIRS = [
    "data/raw",
    "data/processed",
    "models",
    "notebooks",
    "app/ingestion",
    "app/rag",
    "app/generation",
    "app/training",
    "app/evaluation",
]

# Phase 0 - Hazırlık aşamasında gerekli olan dosyalar bu script üzerinden tek bir hamle ile oluşturulacak.
FILES = {
    ".gitignore": 
"""__pycache__/
.venv/
data/
models/
.DS_Store
""",
    "requirements.txt": 
"""
PyMuPDF                     # PDF okuma ve metin temizleme
pandas                      # PDF okuma ve metin temizleme
numpy                       # Embedding çıkarma ve vektör arama
sentence-transformers       # Embedding çıkarma ve vektör arama
chromadb                    # Embedding çıkarma ve vektör arama
transformers                # LoRA adaptasyonu ve model eğitimi
datasets                    # LoRA adaptasyonu ve model eğitimi
peft                        # LoRA adaptasyonu ve model eğitimi
trl                         # LoRA adaptasyonu ve model eğitimi
accelerate                  # LoRA adaptasyonu ve model eğitimi
pydantic                    # Sentetik QA üretiminde şema doğrulaması
python-dotenv               # Güvenli konfigürasyon yönetimi 
pytest                      # Birim ve entegrasyon testleri
""",
# Son iki küütüphaneyi ilk defa bu projede kullanacağım.
    "README.md": 
"""# DomainForge
Proje açıklaması ve notlar buraya gelecek.
""",
    "app/__init__.py": "",
    "app/ingestion/__init__.py": "",
    "app/rag/__init__.py": "",
    "app/generation/__init__.py":"",
    "app/training/__init__.py": "",
    "app/evaluation/__init__.py": "",
}

for d in DIRS:
    Path(d).mkdir(parents=True, exist_ok=True)

for dosya, icerik in FILES.items():
    Path(dosya).write_text(icerik.strip() + "\n", encoding="utf-8")

print("Hazır.")