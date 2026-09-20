
# DomainForge V1 — Tasks

## Phase 0 — Project Setup

* [ ] Proje klasör yapısını oluştur
* [ ] `requirements.txt` oluştur
* [ ] `.gitignore` oluştur
* [ ] `config.py` oluştur
* [ ] Temel pipeline akışını tanımla
* [ ] Logging yapısını oluştur

---

## Phase 1 — Document Ingestion

### PDF Loading

* [ ] `pdf_loader.py` oluştur
* [ ] PDF dosyalarını yükle
* [ ] Sayfa bazlı metin çıkar
* [ ] Document metadata oluştur

### Text Cleaning

* [ ] `text_cleaner.py` oluştur
* [ ] Gereksiz boşlukları temizle
* [ ] Satır/paragraf düzenini normalize et
* [ ] Temizlenmiş metni kaydet

---

## Phase 2 — Chunking

* [ ] `chunker.py` oluştur
* [ ] Chunking stratejisini belirle
* [ ] Chunk boyutunu ve overlap değerini yapılandır
* [ ] Chunk ID oluştur
* [ ] Document ID ve page metadata'sını koru
* [ ] Chunk kalitesini kontrol et
* [ ] Processed veriyi kaydet

---

## Phase 3 — Embedding & Vector DB

### Embeddings

* [ ] `embeddings.py` oluştur
* [ ] Embedding modelini yapılandır
* [ ] Chunk embedding'lerini üret

### Vector Store

* [ ] `vector_store.py` oluştur
* [ ] Vector database'i yapılandır
* [ ] Chunk + embedding + metadata kayıtlarını oluştur
* [ ] Indexleme işlemini oluştur

---

## Phase 4 — Retrieval & RAG

### Retrieval

* [ ] `retriever.py` oluştur
* [ ] Top-k retrieval yapılandır
* [ ] Similarity score değerlerini döndür
* [ ] Source metadata'sını koru
* [ ] Retrieval sonuçlarını test et

### RAG

* [ ] Retrieved context yapısını oluştur
* [ ] RAG prompt yapısını oluştur
* [ ] Context → LLM akışını oluştur
* [ ] Kaynak provenance zincirini koru

---

## Phase 5 — Synthetic Q/A Generation

### Generation Profile

* [ ] Generation Profile yapısını oluştur
* [ ] Question count parametresi
* [ ] Answer length parametresi
* [ ] Depth parametresi
* [ ] Temperature parametresi

### Prompt

* [ ] `prompts.py` oluştur
* [ ] Q/A generation promptunu oluştur
* [ ] Kaynak-temelli cevap üretimini tanımla

### Q/A Generator

* [ ] `qa_generator.py` oluştur
* [ ] Retrieved context kullan
* [ ] Structured output üret
* [ ] Generated Q/A metadata'sını oluştur
* [ ] Source, page ve chunk ID bilgisini koru

---

## Phase 6 — Q/A Validation

* [ ] `qa_validator.py` oluştur
* [ ] Pydantic schema validation
* [ ] Eksik alan kontrolü
* [ ] Kaynakla uyumluluk kontrolü
* [ ] Hallucination kontrolü
* [ ] Duplicate question kontrolü
* [ ] Validation sonucunu kaydet
* [ ] Geçerli kayıtları dataset'e aktar

---

## Phase 7 — JSONL Dataset

* [ ] TrainingExample yapısını oluştur
* [ ] Q/A kayıtlarını training formatına dönüştür
* [ ] Training dataset oluştur
* [ ] Evaluation dataset'i ayır
* [ ] JSONL export oluştur
* [ ] Dataset metadata'sını koru

---

## Phase 8 — Fine-Tuning

### Model

* [ ] `model_loader.py` oluştur
* [ ] Base model seç
* [ ] Tokenizer yükle
* [ ] Model/tokenizer uyumluluğunu kontrol et

### LoRA / QLoRA

* [ ] `lora_config.py` oluştur
* [ ] LoRA configuration oluştur
* [ ] Gerekirse QLoRA yaklaşımını değerlendir
* [ ] Apple Silicon uyumluluğunu kontrol et

### Training

* [ ] `trainer.py` oluştur
* [ ] Training Profile oluştur
* [ ] Learning rate belirle
* [ ] Epoch sayısını belirle
* [ ] Batch size belirle
* [ ] LoRA rank / alpha / dropout değerlerini belirle
* [ ] Training dataset yükle
* [ ] Fine-tuning çalıştır
* [ ] Fine-tuned modeli kaydet

---

## Phase 9 — Evaluation

* [ ] `evaluator.py` oluştur
* [ ] Held-out evaluation dataset kullan
* [ ] Base model çıktıları oluştur
* [ ] Fine-tuned model çıktıları oluştur
* [ ] Base vs fine-tuned karşılaştırması yap
* [ ] Temel metrikleri hesapla
* [ ] Qualitative analysis yap
* [ ] Evaluation sonuçlarını kaydet

---

## Phase 10 — Pipeline Integration

* [ ] `pipeline.py` oluştur
* [ ] Ingestion → Processing akışını bağla
* [ ] Processing → RAG akışını bağla
* [ ] RAG → Q/A generation akışını bağla
* [ ] Q/A → Validation akışını bağla
* [ ] Validation → JSONL akışını bağla
* [ ] JSONL → Fine-tuning akışını bağla
* [ ] Fine-tuning → Evaluation akışını bağla
* [ ] Config üzerinden pipeline çalıştır
* [ ] End-to-end test gerçekleştir

---

## Phase 11 — Testing

* [ ] PDF loading testleri
* [ ] Text cleaning testleri
* [ ] Chunking testleri
* [ ] Embedding testleri
* [ ] Retrieval testleri
* [ ] Q/A schema testleri
* [ ] Validation testleri
* [ ] Dataset export testleri
* [ ] Pipeline testleri

---

## Phase 12 — Documentation

* [ ] `README.md` oluştur
* [ ] Proje amacını dokümante et
* [ ] Mimariyi dokümante et
* [ ] Pipeline akışını dokümante et
* [ ] Kurulum adımlarını ekle
* [ ] Kullanım örneği ekle
* [ ] Örnek input/output ekle
* [ ] Evaluation sonuçlarını ekle
* [ ] Limitations bölümünü ekle

### Project Records

* [ ] `CHANGELOG.md` oluştur
* [ ] Teknik kararları dokümante et
* [ ] Önemli deneyleri kaydet
* [ ] `docs/` altında mimari dokümantasyonu oluştur

---

## Final Checklist

* [ ] Pipeline uçtan uca çalışıyor
* [ ] Kaynak → Q/A provenance zinciri korunuyor
* [ ] Training ve evaluation datasetleri ayrılmış
* [ ] Base vs fine-tuned karşılaştırması mevcut
* [ ] Testler çalışıyor
* [ ] README tamamlandı
* [ ] Teknik kararlar dokümante edildi
* [ ] V1 scope dışına çıkılmadı
* [ ] Proje tekrar çalıştırılabilir durumda
* [ ] GitHub repository düzenli ve sunuma hazır
