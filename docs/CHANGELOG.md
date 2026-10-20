# Değişiklik Günlüğü (CHANGELOG)
## Gün-1 20.09.2026
### Faz-0 Tamamlandı
- setup_project.py ile proje iskeleti oluşturuldu
- makefile ile sanal ortam kurulumu tamamlandı
- .gitignore oluşturuldu
- schemas.py oluşturularak modüller arası veri sözleşmesi yapılandırıldı
- ilk commit ve push furkanyaman-lab adresine yapıldı
## Gün-2 21.09.2026
### Faz-1 Tamamlandı
- Proje için gerekli pdf dosyaları data/raw içerisine yerleştirildi
- pdf_loader.py oluşturuldu
- schemas.py dikkate alınarak sayfa bazlı metin çıkarıldı, metadata oluşturuldu
- text_cleaner.py oluşturuldu
- Genel gürültü giderildi(gereksiz boşluklar giderildi, satır/paragraf düzeni normalize edildi)
- match-case yapısı ile dosya özelinde tekrarlı ifadeler(header-footer metinleri, sayfa numarası vb ifadeler ) temizlendi
- ingestion.ipynb üzerinden testler yapıldı
- gelişmeler commit edilip push'landı.
## Gün-3 22.09.2026
### Faz-2 Tamamlandı
- Q/A çift üretimi dikkate alınarak Semantic Chunk mimarisi tercih edildi
- chunker.py oluşturuldu
- Alan içi döküman kullanımı dikakte alınarak yüksek threshold tercih edildi.
- schemas.py dikkate alınarak chunk düzeni korundu
- rag.ipynb üzerinden testler yapıldı
- Gelişmeler commit edilip push'landı
## Gün-4 23.09.2026
### Faz-3 Tamamlandı
- embedding.py oluşturuldu
- Embedding modeli hızlı protoripleme sebebiyle all-MiniLM-L6-v2 modeli üzerinden yapılandırıldı
- vector_store.py oluşturuldu
- Vector Database yapılandırıldı
- rag.ipynb üzerinden Chunk + embedding + metadata test kayıtları oluşturuldu
- Gelişmeler commit edilip push'landı
### Faz-4 Tamamlandı
- retriever.py oluşturuldu
- Top-K, 4 olarak belirlendi
- Retrieved context şema/yapısı oluşturuldu
- app/generation/prompts.py üzerinde RAG prompt yapısı oluşturuldu
- Context -> LLM akışı sağlandı
- Retrieval sonuçlarının yetersiz görülmesinin ardından embedding ve retrieval aşamaları için all-MiniLM-L6-v2 modelinden daha yüksek kapasiteli BAAI/bge-base-en-v1.5 modeline geçildi.
- Gelişmeler commit edilip push'landı.
## Gün-5 24.09.2026
### Faz-5
- GenerationProfile ve GeneratedQA veri sözleşmeleri schemas.py üzerinden oluşturuldu
- Şema üzerinden Question Count, Answer Legnth, Temperature vb hiperparametreler belirlendi.
- prompts.py üzerinden kaynak temelli Q/A Generation promptu oluşturuldu.
- qa_generator.py oluşturuldu.
- Generating mimarisinde Source, page ve chunk ID bilgisini korundu
- generation.ipynb üzerinden ilk testler yapıldı.
## Gün-6 25.09.2026
### Faz-5
- Çıktılar yetersiz bulunduğundan "Single-Chunk Bias" (Tekil Parça Önyargısı) aşılmak için iki aşamalı arama (Retrieval -> Reranking -> Çoklu Bağlam Sentezi) mimarisine geçildi.
- schema.py, prompts.py ve qa_generator.py üzerinde ilgili değişiklikler yapıldı.
- reranker.py oluşturuldu.
- Sistemin vektörel sıralamada 20 seçim yapması, ardından LLM yardımıyla bulduğu en uygun 5 chunk üzerinden yanıt oluşturması sağlandı
- Üretilen yanıtlar derinlik ve teknik anlamda yeterli bulundu. (Sadece LLM'den kaynaklı kaynak bazında halüsinasyon görmesinin engellenmesi maksadıyla sistem promptuna negatif prompt/kısıtlama eklendi)
- Gelişmeler commit edilip push'landı.
## Gün-7 26.09.2026
### Faz-6
- ValidatedQA şeması hazırlandı.
- qa_validator.py oluşturuldu.
- Uzunluk, yasaklı kelime kullanımı ve util.cos_sim kullanılarak benzerlik metrikleri üzerinden sonuçlar kontrol edildi, generation.ipynb üzerinden testler yapıldı
- torch.stack kullanılarak boyut problemi çözüldü
- prompts.py üzerinden negatif promptlar genişletildi, çıktılar içerisinde .pdf uzantısının geçmesi engellendi 
- Geçerli ve doğrulanan kayıtlar dataset'e aktarıldı
- Gelişmeler commit edilip push'landı
## Gün-8 27.09.2026
### Faz-7
- Training example şeması ve train/eval yapısı hazırlandı.
- formatter.py oluşturuldu.
- Train ratio 0.8 olarak belirlendi, veriler rastgele dağıtıldı.
- Veriler jsonl formatında data/final klasörüne kaydedildi.
- training.ipynb üzerinden testler yapıldı
- Gelişmeler commit edilip push'landı
## Gün-9 28.09.2026
### Faz-8
- model_loader.py oluşturuldu
- Base model olarak eğitim veri hacmi, performans ve hız dengesi göz önünde bulundurularak "Qwen/Qwen2.5-3B-Instruct" seçildi.
- Train aşamasının verimle devam edebilmesi için cihaz/donanım tespit fonksiyonu geliştirildi.
- torch.bfloat16 yapısıyla parametreler 32 bit'ten 16 bit'e indirilerek performans hızlandırıldı.
- Model/tokenizer uyumluluğu test edildi.
- lora_config.py oluşturuldu.
- Neden LoRA? Donanım yeterliliği (Mac Studio m1 Max 32 gb) ve küçük modellerle çalışıldığı için eğitim hızı ve max performans göz önünde bulundurularak LoRA, QLoRA yerine tercih edildi.
- LoRA configuration oluşturuldu. Denge gözetilerek r = 16, dropout=0.05 olarak belirlendi. Hedef modüller modelin doğruluğu ve adaptasyon yeteneği göz önünde bulundurularak modelin tüm katmanlarına etkili olacak şekilde seçildi.
- trainer.py oluşturuldu.
- schemas.py üzerinden Training Profile, eğitim parametreleri belirlendi.
- training.ipynb üzerinden "Smoke Test" gerçekleştirildi.
- Gelişmeler commit edilip push'landı.
## Gün-10 29.09.2026
### Faz-9
- Daha doğru değerlendirme sonuçlarını elde etmek için EvalSampleResult ve EvaluationSummary pydantic şemaları oluşturuldu.
- Şema düzeni üzerinden evaluator.py oluşturuldu
- Evaluate aşamasında model kıyaslamasına gidilirken Fine-Tuing model base modele LoRA Adaptörü giydirilerek temsil edildi. Bu sayede deneysel bir alan oluşturularak nihaiz model için yeniden üretim karar mekanizması hızlandırıldı.
- Fine-Tuning model ile Base Model çıktıları arasında kelime eşleşmesi ile değil kosinüs benzerliği üzerinden değerlendirme yapıldı. Bu sayede iki çıktının kelime kesişimi düşük olsa da referans cevaba olan anlamsal yakınlık dikkate alındı.
- Evaluate aşaması sonucunda tüm soruların skor ortalaması hesaplanarak sürümlenebilir json dosyalarına kaydedilmesi sağlandı
- evaluation.ipynb üzerinden "Smoke Test" gerçekleştirildi.
- Gelişmeler commit edilip push'landı.
### Faz-10
## Gün-11 30.09.2026
- schemas.py üzerinden PipelineConfig yapılandırma şeması oluşturuldu
- `pipeline.py` oluşturuldu. Makefile dosyası akışa göre düzenlendi
- pipeline.py üzerinden temel akış oluşturuldu:
  - Ingestion → Processing akışı bağlandı
  - Processing → RAG akışı bağlandı
  - RAG → Q/A generation akışı bağlandı
  - Q/A → Validation akışı bağlandı
  - Validation → JSONL akışı bağlandı
## Gün-12 02.10.2026
- Fine tuning aşaması öncesinde testler yapıldı. Test sonrası mimariye sadık kalınarak temel akış üzerinde aşağıdaki değişiklikler yapıldı:
  - İlk test çalışması sonrasında üretilen q/a çiftlerinde yüzeysellik ve halüsinasyon belirlendiği için bunu engellemek adına summarizer.py üzerinden ham pdflerden konu başlıkları/içerik haritası çıkarılması sağlandı.
## Gün-13 03.10.2026
  - Oluşturulan içerik haritası interim/framework_summaries.json üzerine kaydedildi. Bu içerik üzerinden üretime tekrar başlandı
  - Üretilen verilerde belgeye dair dağılımın dengeli olmaması sebebiyle qa_generator.py üzerinden generate_balanced_dataset fonksiyonu oluşturuldu.
## Gün-14 04.10.2026
  - Üretim yenilendi, deneme üzerine yeniden çalıştırma durumu düşünülerek üretimin konu dağılımı ve soru sayısına göre kaldığı yerden devam etmesi için gerekli değişiklikler yapıldı.
## Gün-15 13.10.2026
  - Q/A Validation işleminin daha sağlıklı ilerlemesi için kayıt öncesi negatif promptlar/guardrails oluşturuldu,
  - Local model deepseek R1 kullanılarak nihai testlere geçildi.
## Gün-16 14.10.2026
  - Üretilen veri derinliği, kalite ve hız göz önünde bulundurarak nvidia/nemotron-3-ultra-550b-a55b:free modeline geçildi. karşılaştırma için karma veriseti yedeklendi
  - Api üzerinden nihai üretim aşamasına geçildi
## Gün-17 15.10.2026
- Üretilen veri seti LLM'ler yardımıyla değerlendirildi
- Değerlendirme sonrası guardrails'tan geçen kayıtlar için terminal üzerinden tekrar temizleme işlemi yapıldı
- Kalan 160 kayıt üzerinden fine tuning/train işlemi gerçekleştirildi
- Oluşan adaptor üzerinden base model kıyaslanarak evaluation/değerlendirme yapıldı
### Faz-11/12
## Gün-18 17.10.2026
- Gerekli testler yapıldı
- README.md oluşturuldu
  - Proje amacı, mimari ve akış dökümante edildi
  - Örnek çıktı üzerinden değerlendirme yapıldı
  - Proje sınırlılıkları ve gelecek iyileştirilmelerden bahsedildi
- DESICION.md oluşturuldu
## Gün-19 20.10.2026
- LLM-as-a-Judge mimarisi oluşturuldu
- Fine tuned ve Base Model cevaplarının anlamsal benzerlik skorlarının yanı sıra LLM aracılığıyla doğruluk, dökümana bağlılık ve halüsinasyon riski metrikleri ile değerlendirme sağlandı
- Kullanıcıya rehberlik etmesi amacıyla DEMO.md oluşturuldu.