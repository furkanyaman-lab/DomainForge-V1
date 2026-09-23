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
- Gelişmeler coomit edilip push'landı
## Gün-4 23.09.2026
### Faz-3 Tamamlandı
- embedding.py oluşturuldu
- Embedding modeli yapılandırıldı
- vector_store.py oluşturuldu
- Vector Database yapılandırıldı
- rag.ipynb üzerinden Chunk + embedding + metadata test kayıtları oluşturuldu
- 