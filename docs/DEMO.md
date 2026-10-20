# DomainForge V1: Uçtan Uca Teknik Demo & Çalıştırma Rehberi

Bu rehber, DomainForge V1 AI Governance modelinin veri alımından (ingestion) A/B değerlendirmesine kadar olan 6 aşamalı MLOps yaşam döngüsünü yerel ortamda çalıştırmak için hazırlanmıştır.


### 1. Ortam Kurulumu (Environment Setup)

Sanal ortamı (`.venv`), temel kütüphaneleri ve Hugging Face / PyTorch bağımlılıklarını tek komutla kurun:

```bash
make setup
```

![Sanal Ortam Kurulumu](https://lh3.googleusercontent.com/d/1_nWFz2jFAf41z82gDJ8vzZZekyoZ5wSX)

> **Teknik Not:** Bağımlılıklar arası uyum sebebiyle Python 3.11+ tercih edilir.


### 2. Doküman Alımı ve Vektörleştirme (Ingestion Pipeline)

Alana özgü ham dokümanları (NIST AI 100-1, 600-1 ve UNESCO: Recommendation on the Ethics of Artificial Intelligence) sisteme aktarın:

```bash
make ingest
```

![Ingestion Aşaması](https://lh3.googleusercontent.com/d/1Q7mbuejCaF7ePPM3gG_LOFMh9PAZlzgw)

> **Teknik Not:** Bu aşamada PDF metinleri gürültülerden temizlenir, anlamsal parçalara (semantic chunking) bölünür ve SentenceTransformers ile gömülerek (embedding) yerel vektör indeksine yazılır.

---

### 3. Sentetik Soru-Cevap (Q/A) Üretimi

Eğitim için regülasyon kaynaklı sentetik soru-cevap çiftleri oluşturun:

```bash
make generate COUNT=150 MODEL="nvidia/nemotron-3-ultra-550b-a55b:free"
```


![Q/A Çiftlerinin Üretim Aşaması](https://lh3.googleusercontent.com/d/1flhQml24Rre3v51Z12NOsMBkSZxymwzx)

* `COUNT`: Üretilecek nihai doğrulanmış Q/A çifti sayısını belirler.
* `MODEL`: Üretim motoru olarak görev yapan öğretici LLM modelidir.

![Üretim Tamamlandı](https://lh3.googleusercontent.com/d/1AML8Wwy54wvaZ96FeUi3KEnc22ZHiRjX)

> **Kalite Filtreleri:** 
> - **Benzerlik Eşiği:** Veri setinin tek tipleşmesini engellemek için %85 anlamsal benzerlik eşiği (cosine similarity threshold) uygulanır; benzer sorular elenir.
> - **Yasaklı Kavramlar & Halüsinasyon Önleme:** Yüzeysel yanıtlar, yasaklı kavramlar ve kaynaksız iddialar Q/A Validation mimarisi tarafından üretim anında reddedilir.

---

### 4. Veri Doğrulama ve Format Dönüşümü (Formatting & Splitting)

Üretilen ham verileri ChatML formatına dönüştürüp eğitime hazır hale getirin:

```bash
make format
```

![Verileri Eğitime Hazırlama](https://lh3.googleusercontent.com/d/1FDjFJzyZ9cnWBP4w72rA3gN70NGbw5Bs)

 **Teknik Not:** Veri seti derinlik etiketlerine (`foundational`, `technical`, `comparative`) göre tabakalı (stratified) olarak **Train** ve **Eval** kümelerine ayrılır; standart ChatML şablonuna (`system / user / assistant`) dönüştürülür.

---

### 5. PEFT / LoRA Fine-Tuning

#### Hiperparametre Konfigürasyonu ve MLOps Tercihleri

Model eğitimi ve PEFT konfigürasyonu `schemas.py` içerisindeki Pydantic veri şeması ile tip denetimine bağlanmıştır:

![Eğitim Hiperparametreleri](https://lh3.googleusercontent.com/d/1OhvyfS5FQyPdjhrSBZyM6zjsRBsWJ_rv)

| Parametre | Değer | MLOps & Donanım Gerekçesi |
| :--- | :--- | :--- |
| **Model** | `Qwen2.5-3B-Instruct` | 3B ölçeğiyle Apple Silicon üzerinde hızlı eğitim ve yüksek regülasyon uyumu. |
| **Batch / Accumulation** | `1 / 8` | Efektif batch boyutu 8 yapılarak OOM(Bellek taşması) riski sıfırlanmış, kararlı gradyan sağlanmıştır. |
| **Learning Rate** | `2e-4` (Cosine Decay) | LoRA adaptörleri için ideal yakınsama hızı, 5 adımlık `warmup` ile desteklenmiştir. |
| **Epoch** | `3` | Aşırı öğrenmeyi (overfitting) önleyen optimal eğitim döngüsü. |
| **LoRA Rank & Alpha** | `r=16, alpha=32` | Karmaşık standartları içselleştirmek için agresif öğrenme, artırılmış adaptör kapasitesi (alpha/r = 2). |
| **Target Modules** | All-Linear (7 modül) | Attention ve MLP katmanlarının tümü hedeflenerek eksiksiz terminoloji entegrasyonu sağlanmıştır. |

Hazırlanan veri seti üzerinde default = `Qwen2.5-3B-Instruct` modelini fine-tune edin: 
(Eğer cihazınızda model yüklü değilse *ollama run qwen2.5:3b-instruct* terminal komutu ile modeli cihazınıza yükleyin.)

```bash
make train
```

![Eğitim Aşaması](https://lh3.googleusercontent.com/d/1MFmRYT2wq6tjlwXQhXvGiUbUF86rXKJD)

> **Eğitim Profili (Apple Silicon MPS):**
> - **Mimari:** LoRA ($r=16, \alpha=32$), `bfloat16` veri hassasiyeti.
> - **Bellek Optimizasyonu:** `per_device_train_batch_size=1`, `gradient_accumulation_steps=8` (Sıfır OOM garantisi).
> - **Eğitim Süresi:** 3 epoch ~20 dakika (`loss: 3.37 → 1.85` kararlı yakınsama).

---

### 6. A/B Değerlendirme & Halüsinasyon Denetimi (Evaluation)

Fine-Tuned Model ile Base Modeli bağımsız eval verisinde karşılaştırın:

```bash
make eval
```

![Değerlendirme Aşaması](https://lh3.googleusercontent.com/d/1nI026PewZc1SkDzM0waJenztowUWwVs3)

> **Değerlendirme Metrikleri:**
> - **Anlamsal Benzerlik (Cosine Sim):** Ground truth ile üretilen yanıt arasındaki anlamsal yakınlık ölçülür.
> - **LLM-as-a-Judge (Faithfulness):** Bağımsız hakem model (nvidia/nemotron-3-super-120b-a12b:free), üretilen yanıtlardaki regülatif kodların doğruluğunu ve kaynak dışı halüsinasyonları madde madde raporlar.

---

### 7. Ortam Temizliği (Clean)

Eğitim önbelleğini, geçici çıktıları ve checkpoint kalıntılarını sıfırlamak için:

```bash
make clean
```

![Temizlik İşlemi](https://lh3.googleusercontent.com/d/1y5d2QJNb41RIDxLYMfaCQQZl2yhrhCxq)

