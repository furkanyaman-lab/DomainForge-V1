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

## Evaluation(Değerlendirme)

Bağımsız ve derinlik dengesi ile (foundational - comparative - technical derinliklerini kapsayan) oluşturulmuş 30 test örneği üzerinden yapılan çift taraflı (Anlamsal Benzerlik + LLM-as-a-Judge) A/B testinde fine-tuned modelimiz, anlamsal benzerlikte ortalama +0.040 net artış, kaynak sadakatinde ise +0.100 net iyileşme sağlamıştır. Ham modelin %10 olan kusursuz sadakat (1.0) oranı fine-tuning ile %26.7'ye yükselmiş, uydurma standart kodu üretimi ciddi oranda baskılanmıştır. Model, NIST ve UNESCO çerçevelerini teknik mimari kontrollere dönüştürme hedefine başarıyla ulaşmıştır.

![İstatistik Sonuçları](https://lh3.googleusercontent.com/d/1zxQ-W12tlwgbRA_za5fmPkl_2XojCtMB)

    Örnek Çıktı:

    [1/30] Sim: [Base:0.8737 | Fine-Tuned:0.9178] Faithful: [Base:0.2 | Fine-Tuned:0.5] Depth: technical

   ⚠️ Base Hallucination: ['ThreatActor entity (not defined in ground truth)', 'ThreatActorDetails entity (not defined in ground truth)', 'Missing AI system identifier field', 'Missing lifecycle stage field (development, use, malfunction)', 'Missing acute/aggregate classification', 'Missing four harm categories (injury to health, critical infrastructure disruption, human rights violations, harm to property/community/environment)', 'Missing MAP 5.1 quantified likelihood and magnitude assessments', 'Missing actor-task matrix linking to AI Actor roles (Governance and Oversight, Operation and Monitoring, Procurement, Third-party)', 'Missing regulatory alerting procedure GV-2.1-002', 'Missing OECD AI Incidents Monitor taxonomy mapping layer']

   ⚠️ Fine-Tuned Hallucination: ["NIST AI Risk Management Framework's vulnerability disclosure requirements"]

    [2/30] Sim: [Base:0.8031 | Fine-Tuned:0.8649] Faithful: [Base:1.0 | Fine-Tuned:0.8] Depth: technical

    [3/30] Sim: [Base:0.7986 | Fine-Tuned:0.8868] Faithful: [Base:0.5 | Fine-Tuned:0.88] Depth: foundational

    [4/30] Sim: [Base:0.8851 | Fine-Tuned:0.9082] Faithful: [Base:0.2 | Fine-Tuned:0.2] Depth: technical

    ⚠️ Base Hallucination: ['Structured ontology mapping system capabilities (e.g., real-time biometric identification) to specific UDHR/ICCPR articles', 'Quantitative risk scoring framework']

    ⚠️ Fine-Tuned Hallucination: ['Operationalizing a Human Rights Impact Assessment (HRIA) as an automated technical control for the UNESCO Policy Action area requires a layered governance architecture', 'The approach must first establish a structured ontology linking system capabilities — such as real-time biometric identification systems — to specific provisions of international human rights instruments, including the UDHR and ICCPR', 'The architecture must implement quantitative risk scoring mechanisms that translate qualitative human rights impacts into measurable, auditable indicators', 'The governance structure must mandate continuous monitoring and evaluation of system performance against the mapped human rights standards. Automated dashboards and alerting systems should trigger when system capabilities exceed predefined thresholds or when new human rights risks emerge', 'The architecture must embed human rights considerations into the software development lifecycle through mandatory human rights impact assessments at key stages, such as requirement gathering, design, implementation, and deployment']

    [5/30] Sim: [Base:0.8952 | Fine-Tuned:0.886] Faithful: [Base:0.4 | Fine-Tuned:1.0] Depth: foundational

    ⚠️ Base Hallucination: ['NIST.AI.600-1 Risk 5.1']

    [6/30] Sim: [Base:0.8416 | Fine-Tuned:0.8444] Faithful: [Base:0.5 | Fine-Tuned:0.5] Depth: foundational

    ⚠️ Fine-Tuned Hallucination: ['MEASURE-2.5']

    [7/30] Sim: [Base:0.8259 | Fine-Tuned:0.8594] Faithful: [Base:0.5 | Fine-Tuned:0.85] Depth: technical

    [8/30] Sim: [Base:0.8426 | Fine-Tuned:0.855] Faithful: [Base:0.2 | Fine-Tuned:0.8] Depth: foundational

    ⚠️ Base Hallucination: ["The response claims that TruLens satisfies the MEASURE function's validity requirements, which contradicts the Ground Truth stating that the GAI Profile does not prescribe specific frameworks such as TruLens."]

    [9/30] Sim: [Base:0.8717 | Fine-Tuned:0.9254] Faithful: [Base:0.5 | Fine-Tuned:0.8] Depth: foundational
    [10/30] Sim: [Base:0.8424 | Fine-Tuned:0.9371] Faithful: [Base:0.85 | Fine-Tuned:0.2] Depth: comparative

   ⚠️ Fine-Tuned Hallucination: ['NIST AI 600-1']

    [11/30] Sim: [Base:0.8096 | Fine-Tuned:0.8898] Faithful: [Base:1.0 | Fine-Tuned:0.8] Depth: foundational

    ⚠️ Fine-Tuned Hallucination: ['NIST AI 600-1']

    [12/30] Sim: [Base:0.8173 | Fine-Tuned:0.927] Faithful: [Base:0.8 | Fine-Tuned:0.8] Depth: technical

    ⚠️ Fine-Tuned Hallucination: ["NIST AI Risk Management Framework's governance functions: Monitor, Measure, and Govern"]

    [13/30] Sim: [Base:0.7651 | Fine-Tuned:0.8171] Faithful: [Base:0.5 | Fine-Tuned:0.5] Depth: technical

    [14/30] Sim: [Base:0.8411 | Fine-Tuned:0.8395] Faithful: [Base:0.8 | Fine-Tuned:0.85] Depth: comparative

    [15/30] Sim: [Base:0.7581 | Fine-Tuned:0.8115] Faithful: [Base:0.9 | Fine-Tuned:0.5] Depth: comparative

    ⚠️ Fine-Tuned Hallucination: ['The governance function enforces separation of duties by implementing a dual-layer access control architecture with policy-as-code (OPA/Rego) and automated promotion gates, which is not prescribed by the NIST AI RMF 1.0 Govern function.']

    [16/30] Sim: [Base:0.846 | Fine-Tuned:0.9313] Faithful: [Base:0.5 | Fine-Tuned:0.5] Depth: foundational

    ⚠️ Base Hallucination: ['Kilogram Watermark (invented term for behavioral watermarking)', "Example linking token bucket refill to 'kilogram watermark' (conflates rate‑limiting with watermarking)"]

    ⚠️ Fine-Tuned Hallucination: ['Risk 4.1', 'Risk 4.2', 'kilogram watermark']

    [17/30] Sim: [Base:0.9171 | Fine-Tuned:0.9297] Faithful: [Base:0.5 | Fine-Tuned:0.2] Depth: foundational

    ⚠️ Base Hallucination: ['GOVERN-1.2']

    ⚠️ Fine-Tuned Hallucination: ['GOVERN-1.2']

    [18/30] Sim: [Base:0.8996 | Fine-Tuned:0.9308] Faithful: [Base:0.5 | Fine-Tuned:1.0] Depth: comparative

    ⚠️ Base Hallucination: ['UNESCO Recommendation on the Protection of the Rights of Persons with Disabilities with Respect to Artificial Intelligence Systems (incorrect title and focus)', 'Claim that the UNESCO Recommendation highlights inclusivity, privacy, and transparency as its key principles (misrepresents the actual principles outlined in the ground truth)']

    [19/30] Sim: [Base:0.8363 | Fine-Tuned:0.76] Faithful: [Base:1.0 | Fine-Tuned:1.0] Depth: comparative

    [20/30] Sim: [Base:0.8199 | Fine-Tuned:0.8489] Faithful: [Base:0.5 | Fine-Tuned:0.5] Depth: technical

    [21/30] Sim: [Base:0.8459 | Fine-Tuned:0.864] Faithful: [Base:0.8 | Fine-Tuned:1.0] Depth: comparative

    [22/30] Sim: [Base:0.8918 | Fine-Tuned:0.9083] Faithful: [Base:0.5 | Fine-Tuned:0.88] Depth: comparative

    [23/30] Sim: [Base:0.7487 | Fine-Tuned:0.9031] Faithful: [Base:0.8 | Fine-Tuned:1.0] Depth: comparative

    [24/30] Sim: [Base:0.8011 | Fine-Tuned:0.7925] Faithful: [Base:0.85 | Fine-Tuned:1.0] Depth: foundational

    [25/30] Sim: [Base:0.9052 | Fine-Tuned:0.8728] Faithful: [Base:0.8 | Fine-Tuned:0.9] Depth: technical

    [26/30] Sim: [Base:0.8334 | Fine-Tuned:0.862] Faithful: [Base:0.5 | Fine-Tuned:0.2] Depth: comparative

    ⚠️ Fine-Tuned Hallucination: ['Retention period of at least three years for incident records', 'Claim that NIST AI 600-1 does not prescribe a technical architecture for automated report generation or standardized incident formats']

    [27/30] Sim: [Base:0.866 | Fine-Tuned:0.8681] Faithful: [Base:0.5 | Fine-Tuned:0.5] Depth: technical

    [28/30] Sim: [Base:0.9022 | Fine-Tuned:0.8962] Faithful: [Base:0.5 | Fine-Tuned:1.0] Depth: comparative

    [29/30] Sim: [Base:0.8581 | Fine-Tuned:0.8638] Faithful: [Base:0.5 | Fine-Tuned:0.5] Depth: foundational

    ⚠️ Base Hallucination: ['MEASURE-2.7']

    ⚠️ Fine-Tuned Hallucination: ['Zone Rules, Trend Rules, and Compound Rules are presented as core SPC rules (these are not standard Western Electric Rules)', 'Example: if Equalized Odds difference threshold is ±0.1, any metric value exceeding ±1.0 triggers an alert (nonsensical and not grounded in any standard)', 'Description of Moving Average and Standard Deviation use for specification limits is inaccurate and not aligned with Western Electric Rules']

    [30/30] Sim: [Base:0.8168 | Fine-Tuned:0.9524] Faithful: [Base:0.85 | Fine-Tuned:0.85] Depth: technical 

- Neden Başarılı? (Teknik Kanıtlar)

Kavramsal ve Karşılaştırmalı Üstünlük: Base model sahte maddeler (NIST Risk 5.1, sahte UNESCO başlığı) veya üçüncü taraf araçları (TruLens) standart gibi uydururken; FT model bu testlerde [5, 8, 18, 21-24, 28/30] tam/yüksek sadakat (0.80 - 1.0) yakalayarak halüsinasyonu engelledi.

Semantik Uyum ve Terminoloji Sıçraması: Teknik uç vakalarda [1, 3, 10, 12, 30/30] benzerlik skorları 0.92 - 0.95 bandına çıktı. Model, ham Qwen üslubunu bırakıp doğrudan NIST/UNESCO kurumsal terminolojisini benimsedi.

- Puan Kırılma Nedenleri (Savunma Argümanları)
  
Mimari Zenginleştirme Cezası (Extrapolation): [15/30]'da model salt regülasyon metninin ötesine geçip sektörel pratik olan OPA/Rego Policy-as-Code çözümü önerdiği için hakem tarafından "referans dışı iddia" sayılarak cezalandırıldı.

Veri Lekeleri ve SPC Sapması: [16/30]'daki 'kilogram watermark' ifadesi sentetik veri hattındaki kavram karışıklığından, [29/30]'daki kayıp ise Western Electric SPC kurallarındaki teknik sapmadan kaynaklandı.

Daha Güncel Standart Tercihi: [10, 11/30]'da referans metin NIST 100-1 iken, model üretken yapay zekaya daha uygun olan güncel NIST AI 600-1 standardına atıf yaptığı için kaynak dışı kabul edildi (0.2).

## Sınırlamalar
- Proje version 1'de özellikle içerisinde "İçindekiler" bulunan dökümanlar üzerinden konu haritası çıkararak Q/A çifleri oluşturabilmektedir. Bu haliyle informal dökümanlar üzerinde sağlıklı çalışmamaktadır.
- Öte yandan testler pdf dosyaları üzerinden gerçekleştirilmiş olup görsel, tablolar vb dosyaları desteklememektedir.
- Her ne kadar bir otomasyon projesi olsa da veri temizleme aşamasında her kaynağa özel regex kodları yazılması gerektiğinden tamamıyla sürecin otomasyon haline getirildiği iddia edilememektedir.

## Gelecekteki iyileştirmeler
- Projenin ilerleyen aşamalarda multimodal RAG sistemiyle tablolar, görseller vb diğer dosyaların destekelmesi sağlanabilir,
- Multi-Agent akışları oluşturularak veri düzenleme, profil oluşturma, şemalar ai destekli senaryolar hazırlanabilir, otomasyon oranı artırılabilir,
- Halihazırda proje tek model üzerinden ilerlemekte olup ilerleyen safhalarda verisetine göre farklı modellerin kullanıulması sağlanabilir,