
# DomainForge V1 — Tasks

## Phase 0 — Project Setup

* [x] Proje klasör yapısını oluştur
* [x] `requirements.txt` oluştur
* [x] `.gitignore` oluştur
* [x] `config.py` oluştur
* [x] Temel pipeline akışını tanımla

---

## Phase 1 — Document Ingestion

### PDF Loading

* [x] `pdf_loader.py` oluştur
* [x] PDF dosyalarını yükle
* [x] Sayfa bazlı metin çıkar
* [x] Document metadata oluştur

### Text Cleaning

* [x] `text_cleaner.py` oluştur
* [x] Gereksiz boşlukları temizle
* [x] Satır/paragraf düzenini normalize et
* [x] Temizlenmiş metni kaydet

---

## Phase 2 — Chunking

* [x] `chunker.py` oluştur
* [x] Chunking stratejisini belirle
* [x] Chunk boyutunu ve overlap değerini yapılandır
* [x] Chunk ID oluştur
* [x] Document ID ve page metadata'sını koru
* [x] Chunk kalitesini kontrol et
* [x] Processed veriyi kaydet

---

## Phase 3 — Embedding & Vector DB

### Embeddings

* [x] `embeddings.py` oluştur
* [x] Embedding modelini yapılandır
* [x] Chunk embedding'lerini üret

### Vector Store

* [x] `vector_store.py` oluştur
* [x] Vector database'i yapılandır
* [x] Chunk + embedding + metadata kayıtlarını oluştur
* [x] Indexleme işlemini oluştur

---

## Phase 4 — Retrieval & RAG

### Retrieval

* [x] `retriever.py` oluştur
* [x] Top-k retrieval yapılandır
* [x] Similarity score değerlerini döndür
* [x] Source metadata'sını koru
* [x] Retrieval sonuçlarını test et

### RAG

* [x] Retrieved context yapısını oluştur
* [x] RAG prompt yapısını oluştur
* [x] Context → LLM akışını oluştur
* [x] Kaynak provenance zincirini koru

---

## Phase 5 — Synthetic Q/A Generation

### Generation Profile

* [x] Generation Profile yapısını oluştur
* [x] Question count parametresi
* [x] Answer length parametresi
* [x] Depth parametresi
* [x] Temperature parametresi

### Prompt

* [x] `prompts.py` oluştur
* [x] Q/A generation promptunu oluştur
* [x] Kaynak-temelli cevap üretimini tanımla

### Q/A Generator

* [x] `qa_generator.py` oluştur
* [x] Retrieved context kullan
* [x] Structured output üret
* [x] Generated Q/A metadata'sını oluştur
* [x] Source, page ve chunk ID bilgisini koru

---

## Phase 6 — Q/A Validation

* [x] `qa_validator.py` oluştur
* [x] Pydantic schema validation
* [x] Eksik alan kontrolü
* [x] Kaynakla uyumluluk kontrolü
* [x] Hallucination kontrolü
* [x] Duplicate question kontrolü
* [x] Validation sonucunu kaydet
* [x] Geçerli kayıtları dataset'e aktar

---

## Phase 7 — JSONL Dataset

* [x] TrainingExample yapısını oluştur
* [x] Q/A kayıtlarını training formatına dönüştür
* [x] Training dataset oluştur
* [x] Evaluation dataset'i ayır
* [x] JSONL export oluştur
* [x] Dataset metadata'sını koru

---

## Phase 8 — Fine-Tuning

### Model

* [x] `model_loader.py` oluştur
* [x] Base model seç
* [x] Tokenizer yükle
* [x] Model/tokenizer uyumluluğunu kontrol et

### LoRA / QLoRA

* [x] `lora_config.py` oluştur
* [x] LoRA configuration oluştur
* [x] Gerekirse QLoRA yaklaşımını değerlendir
* [x] Apple Silicon uyumluluğunu kontrol et

### Training

* [x] `trainer.py` oluştur
* [x] Training Profile oluştur
* [x] Learning rate belirle
* [x] Epoch sayısını belirle
* [x] Batch size belirle
* [x] LoRA rank / alpha / dropout değerlerini belirle
* [x] Training dataset yükle
* [x] Fine-tuning çalıştır
* [x] Fine-tuned modeli kaydet

---

## Phase 9 — Evaluation

* [x] `evaluator.py` oluştur
* [x] Held-out evaluation dataset kullan
* [x] Base model çıktıları oluştur
* [x] Fine-tuned model çıktıları oluştur
* [x] Base vs fine-tuned karşılaştırması yap
* [x] Temel metrikleri hesapla
* [x] Qualitative analysis yap
* [x] Evaluation sonuçlarını kaydet

---

## Phase 10 — Pipeline Integration

* [x] `pipeline.py` oluştur
* [x] Ingestion → Processing akışını bağla
* [x] Processing → RAG akışını bağla
* [x] RAG → Q/A generation akışını bağla
* [x] Q/A → Validation akışını bağla
* [x] Validation → JSONL akışını bağla
* [x] JSONL → Fine-tuning akışını bağla
* [x] Fine-tuning → Evaluation akışını bağla
* [x] Config üzerinden pipeline çalıştır
* [x] End-to-end test gerçekleştir

---

## Phase 11 — Testing

* [x] PDF loading testleri
* [x] Text cleaning testleri
* [x] Chunking testleri
* [x] Embedding testleri
* [x] Retrieval testleri
* [x] Q/A schema testleri
* [x] Validation testleri
* [x] Dataset export testleri
* [x] Pipeline testleri

---

## Phase 12 — Documentation

* [x] `README.md` oluştur
* [x] Proje amacını dokümante et
* [x] Mimariyi dokümante et
* [x] Pipeline akışını dokümante et
* [x] Kurulum adımlarını ekle
* [x] Kullanım örneği ekle
* [x] Örnek input/output ekle
* [x] Evaluation sonuçlarını ekle
* [x] Limitations bölümünü ekle

### Project Records

* [x] `CHANGELOG.md` oluştur
* [x] Teknik kararları dokümante et
* [x] Önemli deneyleri kaydet
* [x] `docs/` altında mimari dokümantasyonu oluştur

---

## Final Checklist

* [x] Pipeline uçtan uca çalışıyor
* [x] Kaynak → Q/A provenance zinciri korunuyor
* [x] Training ve evaluation datasetleri ayrılmış
* [x] Base vs fine-tuned karşılaştırması mevcut
* [x] Testler çalışıyor
* [x] README tamamlandı
* [x] Teknik kararlar dokümante edildi
* [x] V1 scope dışına çıkılmadı
* [x] Proje tekrar çalıştırılabilir durumda
* [x] GitHub repository düzenli ve sunuma hazır
