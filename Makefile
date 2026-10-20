# ==============================================================================
# DomainForge V1 — Pipeline Makefile
# ==============================================================================

SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Varsayılan Parametreler (Komut satırından ezilebilir: make generate COUNT=5)
COUNT ?= 150
STAGE ?= all
MODEL ?= nvidia/nemotron-3-ultra-550b-a55b:free

.PHONY: help setup ingest generate format train eval all clean status show-eval

help:
	@echo "======================================================================"
	@echo "                DomainForge V1 Pipeline CLI                          "
	@echo "======================================================================"
	@echo "  make setup          : Sets up the virtual environment and installs packages"
	@echo "  make ingest         : Reads PDF documents, splits them and ingests them into ChromaDB"
	@echo "  make generate       : Retrieves context using RAG, generates synthetic Q&A and filters it"
	@echo "                        (Optional: make generate COUNT=5)"
	@echo "  make format         : Converts Q&A data into ChatML format and splits it into Train and Eval sets"
	@echo "  make train          : Starts LoRA fine-tuning training"
	@echo "  make eval           : Evaluates the model on the held-out test set"
	@echo "  make all            : Runs the entire pipeline from start to finish"
	@echo "  make show-eval      : Prints the final evaluation summary (JSON) to the screen"
	@echo "  make status         : Lists the status of the generated data and model"
	@echo "  make clean          : Clears processed temporary data and caches"
	@echo "======================================================================"

# --- KURULUM ---
setup:
	python3.11 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ The environment has been set up."

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

all: ingest generate format train eval
	@echo "🎉 The end-to-end pipeline has been successfully completed!"

# --- DENETİM VE GÖRÜNTÜLEME ---

show-eval:
	@if [ -f "data/final/eval_results.jsonl" ]; then \
		head -n 5 data/final/eval_results.jsonl; \
	elif [ -f "data/final/eval_results.json" ]; then \
		cat data/final/eval_results.json; \
	else \
		echo "⚠️ No assessment report has been found yet."; \
	fi

status:
	@echo "=== DOMAINFORGE VERİ DURUMU ==="
	@echo -n "ChromaDB Directory  : " && (ls -d data/chroma_db 2>/dev/null || echo "Not found")
	@echo -n "Verified Q&A (Line) : " && (wc -l data/processed/qa_dataset.jsonl 2>/dev/null || echo "0")
	@echo -n "Train Set (Row)     : " && (wc -l data/final/train.jsonl 2>/dev/null || echo "0")
	@echo -n "Eval Set (Row)      : " && (wc -l data/final/eval.jsonl 2>/dev/null || echo "0")
	@echo -n "Fine-Tuned Model    : " && (ls -d models/fine-tuned-governance 2>/dev/null || echo "Has not yet been trained")

clean:
	rm -rf data/processed/*.jsonl
	rm -rf data/final/*.jsonl
	rm -rf data/final/*.json
	rm -rf data/chroma_db
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "🧹 Temporary data sets and caches have been cleared."