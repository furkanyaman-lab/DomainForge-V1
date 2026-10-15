# ==============================================================================
# DomainForge V1 — Pipeline Makefile
# ==============================================================================

SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Varsayılan Parametreler (Komut satırından ezilebilir: make generate COUNT=5)
COUNT ?= 2
STAGE ?= all
MODEL ?= deepseek-r1:14b

.PHONY: help setup ingest generate format train eval all clean status show-eval

help:
	@echo "======================================================================"
	@echo "                DomainForge V1 Pipeline CLI                          "
	@echo "======================================================================"
	@echo "  make setup          : Sanal ortamı kurar ve paketleri yükler"
	@echo "  make ingest         : PDF dokümanlarını okur, böler ve ChromaDB'ye gömer"
	@echo "  make generate       : RAG ile bağlam çeker, sentetik Q/A üretir ve filtreler"
	@echo "                        (Opsiyonel: make generate COUNT=5)"
	@echo "  make format         : Q/A verilerini ChatML formatına sokar ve Train/Eval böler"
	@echo "  make train          : LoRA fine-tuning eğitimini başlatır"
	@echo "  make eval           : Held-out test seti üzerinde modeli değerlendirir"
	@echo "  make all            : Tüm boru hattını baştan sona icra eder"
	@echo "  make show-eval      : Son değerlendirme özetini (JSON) ekrana basar"
	@echo "  make status         : Üretilen veri ve model durumunu listeler"
	@echo "  make clean          : İşlenmiş geçici verileri ve cache'leri temizler"
	@echo "======================================================================"

# --- KURULUM ---
setup:
	python3.11 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Ortam kurulumu tamamlandı."

# --- PIPELINE AŞAMALARI ---

ingest:
	@echo "🔹 [STAGE 1] Ingestion & Vector Indexing..."
	$(PYTHON) app/pipeline.py --stage ingest

generate:
	@echo "🔹 [STAGE 2] Q/A Generation & Validation (Target Count: $(COUNT), Model: $(MODEL))..."
	$(PYTHON) app/pipeline.py --stage generate --count $(COUNT) --model "$(MODEL)"

format:
	@echo "🔹 [STAGE 3] Dataset Formatting (ChatML Split)..."
	$(PYTHON) app/pipeline.py --stage format

train:
	@echo "🔹 [STAGE 4] LoRA Fine-Tuning..."
	$(PYTHON) app/pipeline.py --stage train --train

eval:
	@echo "🔹 [STAGE 5] Model Evaluation & Benchmarking..."
	$(PYTHON) app/pipeline.py --stage eval

all: ingest generate format eval
	@echo "🎉 Uçtan uca boru hattı başarıyla tamamlandı!"

# --- DENETİM VE GÖRÜNTÜLEME ---

show-eval:
	@if [ -f "data/final/eval_results.jsonl" ]; then \
		head -n 5 data/final/eval_results.jsonl; \
	elif [ -f "data/final/eval_results.json" ]; then \
		cat data/final/eval_results.json; \
	else \
		echo "⚠️ Henüz değerlendirme raporu bulunamadı."; \
	fi

status:
	@echo "=== DOMAINFORGE VERİ DURUMU ==="
	@echo -n "ChromaDB Dizini      : " && ls -d data/chroma_db 2>/dev/null || echo "Bulunamadı"
	@echo -n "Doğrulanmış Q/A (Satır): " && wc -l data/processed/qa_dataset.jsonl 2>/dev/null || echo "0"
	@echo -n "Train Seti (Satır)    : " && wc -l data/final/train.jsonl 2>/dev/null || echo "0"
	@echo -n "Eval Seti (Satır)     : " && wc -l data/final/eval.jsonl 2>/dev/null || echo "0"
	@echo -n "Fine-Tuned Model     : " && ls -d models/fine-tuned-governance 2>/dev/null || echo "Henüz eğitilmedi"

clean:
	rm -rf data/processed/*.jsonl
	rm -rf data/final/*.jsonl
	rm -rf data/final/*.json
	rm -rf data/chroma_db
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "🧹 Geçici veri setleri ve önbellekler temizlendi."