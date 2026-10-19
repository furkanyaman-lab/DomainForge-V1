# DomainForge

## Proje başlığı
DomainForge V1 : RAG Tabanlı Sentetik Q/A Veri Üretimi ve Küçük Dil Modeli Fine-Tuning Prototipi 

## Sorun tanımı
Büyük dil modellerinin belirli bir bilgi alanına uyarlanabilmesi için kaliteli ve alanla ilişkili eğitim verilerine ihtiyaç vardır. Ancak bu verilerin manuel hazırlanması zaman alıcı ve maliyetlidir. DomainForge V1, bu aşamada global AI governance kaynaklarından yararlanarak RAG (Retrieval-Augmented Generation) ile kaynak temelli sentetik soru-cevap verisi üretmeyi ve bu veriyle küçük bir dil modelini LoRA/QLoRA kullanarak fine-tune etmeyi amaçlamaktadır.

## Bu projenin önemi
- Hedef kullanıcı / kullanım senaryosu
Sistem; belirli bir doküman kümesinden kendi alanına yönelik eğitim verisi ve küçük dil modeli oluşturmak isteyen geliştirici veya araştırmacıyı hedeflemektedir. Kullanıcı dokümanları sisteme sağlar ve sistem dökümanlardan yola çıkarak RAG yardımıyla Q/A çiftleri oluşturur. Oluşturulan Q/A çiftleri eğitim verisi haline getirilerek proje uzantısı olarak base model fine tuning edilir.

## Mimariye genel bakış
Proje;
     Ingestion -> Processing -> RAG -> Q/A Generation -> Q/A Validation -> JSONL/Formatting -> Fine-Tuning -> Evaluation 
     akışından oluşmaktadır.

## Teknoloji yığını
Proje Python dili ile yazılmış olup projede; PDF parsing, text preprocessing, chunking, embeddings, vector database, RAG, reranker, LLM, structured output/JSONL, Hugging Face Transformers, PEFT/LoRA ve temel model değerlendirme yöntemleri kullanılmıştır.

## Klasör yapısı
    "data/raw" : Alana yönelik dökümanlar,
    "data/processed" : Oluşturulan Q/A çiftleri,
    "data/final" : Train-Eval verileri,
    "data/chroma_db" : Vektörel veriler,
    "data/interim" : Dökümanlardan çıkarılan konu haritaları ve anahatar kelimeler,
    "models" : Üretim sonucu/ Fine Tuned Model,
    "notebooks" : Mimariye dair deneysel çalışmalar,
    "app/ingestion" : Projenin Ingesiton Mimarisi,
    "app/rag" : Projenin RAG Mimarisi,
    "app/generation" : Projenin Q/A Generation Mimarisi,
    "app/training" : Projenin Training Akışı,
    "app/evaluation" : Projenin Evaluation Mimarisi

## Kurulum § Ortam kurulumu
Proje için Makefile dosyası oluşturulmuş olup terminalde "make setup" komutuyla kurulum tamamlanacaktır.

## Çalıştırma talimatları
Pipeline aşamaları "make" komutuyla çalıştırılabilir durumdadır. Detaylı bilgiye Makefile dosyasından ulaşabilirsiniz. Örnek komutlar:
- "make ingest" -> Ingestion ve vektörleştirme aşamalarını tetikler
- "make generate" -> Q/A Generation ve Validation aşamalrını tetikler
- "make format" -> Veriyi eğitime hazır hale getirir
- "make train" -> Hazırlanan veriler üzerinden fine-tuning işlemini başlatır
- "make eval" -> Base ve Fine-Tuned Model üzerinden Evaluation ve Benchmarking sonuçlarını çıkarır.

## Kullanım örneği
Projenin generate aşamasında:
    "make generate COUNT=150 MODEL="nvidia/nemotron-3-ultra-550b-a55b:free" 
    komutu ile beraber üretim başlar.
    Komutta yer alan "COUNT=" bölümü oluşturulacak nihai soru sayısını, "MODEL=" kısmı da üretimde kullanılacak modeli belirtir.

## Örnek çıktılar
Projenin eval aşamasında alınan örnek bir çıktı aşağıda verilmiştir.
- "question", dökümanlarda yer alan konu başlıkları baz alınarak oluşturulan soruyu
- "ground_truth", sorunun RAG aracılığı ile oluşturulmuş cevabı
- "base_response", soruya base modelin verdiği cevap
- "finetuned_response", soruya fine tuned modelin verdiği cevap
- "semantic_sim_base": 0.827, base model cevabının "ground_truth" cevaba olan vektörel uzaklığı, benzeşim skoru
- "semantic_sim_ft": 0.9052, fine tuned modelin cevabının "ground_truth" cevaba olan vektörel uzaklığı, benzeşim skoru

  "question": "How can GOVERN-4.2 (Organizational culture) be technically enforced via Policy as Code (OPA/Rego) gates in the model registry to prevent deployment of models lacking specific bias evaluation reports?",
      "ground_truth": "Organizational culture commitments under GOVERN 4.1 require policies and practices that foster a critical thinking and safety-first mindset throughout the AI lifecycle. GOVERN 1.4 mandates that risk management processes be established through transparent policies, procedures, and controls aligned with organizational risk priorities. These governance directives can be technically enforced by codifying policy requirements as machine-executable rules within a Policy-as-Code framework such as Open Policy Agent (OPA) using Rego. Specifically, model registry deployment gates can be configured to evaluate admission policies that require the presence of specific bias evaluation reports as mandatory artifacts before a model version transitions to a production-ready state. The policy engine evaluates metadata attached to model registry entries — such as evaluation report identifiers, fairness metric thresholds, and approval signatures — against the codified rules. If the required bias evaluation evidence is absent or does not meet defined criteria, the gate denies deployment, thereby operationalizing the safety-first mindset and transparent controls prescribed by the governance framework. This approach transforms organizational policy into automated, auditable enforcement points that prevent deployment of models lacking documented bias assessments, ensuring compliance with the risk management process and cultural commitments.",
      "base_response": "user\nTo enforce organizational culture through technical means such as Policy as Code (OPA/Rego) gates in the model registry, you need to ensure that certain criteria are met before a model can be deployed. Specifically, you want to enforce that all models have undergone and provided bias evaluation reports. Here’s how you can achieve this:\n\n### 1. Define the Policy as Code (OPA/Rego)\nFirst, you need to define a policy using OPA (Open Policy Agent) Rego language that checks if a model has a bias evaluation report before allowing its deployment.\n\n#### Example Rego Policy:\n```rego\npackage org.modelregistry\n\nimport (\n    \"github.com/open-policy-agent/opa/rego\"\n)\n\n# Define the input data structure for a model\ntype Model struct {\n    Name string\n    BiasEvaluationReport string\n}\n\n# Define the policy\nallow_model_deployment := {\n    # Check if the model has a bias evaluation report\n    report := input.BiasEvaluationReport,\n    # If no report is provided, deny the deployment\n    report == \"\"\n}\n\n# Allow deployment if the condition is met\nallow_model_deployment\n```\n\n### 2. Implement the Policy in OPA\nYou would implement this policy within your OPA server. This involves creating a new rule or updating an existing one to check for the presence of a bias evaluation report.\n\n### 3. Integrate with the Model Registry\nEnsure that the policy is integrated into",
      "finetuned_response": "assistant\nGovern-4.2 requires that organizational culture and values permeate every governance layer, embedding ethical standards into the software development lifecycle. Technically enforcing this mandate via Policy as Code gates in the model registry must translate cultural norms into executable policy rules that validate model deployment against predefined ethical benchmarks. The first step is to codify the organization's bias assessment policies — including mandatory reporting for all model outputs — into a formal policy language such as Open Policy Agent (OPA) orrego. This policy document should define thresholds for disparate impact, demographic parity, equalized odds, and other fairness metrics, specifying that any model without a signed, auditable bias evaluation report is non-compliant. Next, the model registry must integrate these policy gates at the deployment stage: each model artifact must pass through a gate that checks whether a corresponding bias evaluation report exists in the repository. If the report is missing or invalid, the gate denies deployment, triggering an automated feedback loop where the model owner is alerted to complete the required evaluation before re-submission. This enforcement mechanism ensures that cultural expectations about transparency, accountability, and continuous improvement are operationalized as immutable policy constraints on model lineage and deployment pipelines.",
      "semantic_sim_base": 0.827,
      "semantic_sim_ft": 0.9052

Çıktıda gördüldüğü üzere;
- Base Model rol karmaşası ve halüsinasyon içindeyken Fine-Tuned Model yapılandırılmış, bağlam ve disiplini koruyan bir yanıt üretmiştir,
- Base Model cevabında yüzeysel kalırken Fine-Tuned Model teknik terminolojiye hakim ve net yanıtlar vermiştir,
- Similarity Skorları arasında %7'lik bir fark bulunmaktadır,
tüm bu sebeplerle Fine-Tuned Model üzerinde ilerleme kaydedildiği somut olarak görülmüştür.

Skor bazlı ilk 5 örnek:
1. [15/32] Durumu (+0.0992 artış)
	• Base: 0.7761 | Fine-Tuned: 0.8753
2. [8/32] Durumu (+0.0982 artış)
	• Base: 0.8479 | Fine-Tuned: 0.9461
3. [5/32] Durumu (+0.0811 artış)
	• Base: 0.7768 | Fine-Tuned: 0.8579
4. [20/32] Durumu (+0.0782 artış)
	• Base: 0.8270 | Fine-Tuned: 0.9052 (Yukarıda detayları verilmiştir.)
5. [17/32] Durumu (+0.0745 artış)
	• Base: 0.8147 | Fine-Tuned: 0.8892
Not: Sıralama, iki model arasındaki doğrudan puan farkı (Fine-Tuned - Base) hesaplanarak yapılmıştır.

Detaylı bilgilere data/final/eval_results.json dosyasından ulaşabilirsiniz.

## Sınırlamalar
- Proje version 1'de özellikle içerisinde "İçindekiler" bulunan dökümanlar üzerinden konu haritası çıkararak Q/A çifleri oluşturabilmektedir. Bu haliyle informal dökümanlar üzerinde sağlıklı çalışmamaktadır.
- Öte yandan testler pdf dosyaları üzerinden gerçekleştirilmiş olup görsel, tablolar vb dosyaları desteklememektedir.
- Her ne kadar bir otomasyon projesi olsa da veri temizleme aşamasında her kaynağa özel regex kodları yazılması gerektiğinden tamamıyla sürecin otomasyon haline getirildiği iddia edilememektedir.

## Gelecekteki iyileştirmeler
- Projenin ilerleyen aşamalarda multimodal RAG sistemiyle tablolar, görseller vb diğer dosyaların destekelmesi sağlanabilir,
- Multi-Agent akışları oluşturularak veri düzenleme, profil oluşturma, şemalar ai destekli senaryolar hazırlanabilir, otomasyon oranı artırılabilir,
- Halihazırda proje tek model üzerinden ilerlemekte olup ilerleyen safhalarda verisetine göre farklı modellerin kullanıulması sağlanabilir,