# Türkçe PDF QA Sistemi - Geliştirme Notları

Bu dokümanda, Türkçe PDF Soru-Cevap sisteminin geliştirme sürecinde yapılan deneyler, model karşılaştırmaları ve performans analizleri yer almaktadır.

## 📊 Genel Bakış

Proje gelişimi 3 ana aşamada gerçekleştirilmiştir:

### **Notebook 1**: `01_gelistirme_kodlari.ipynb` 
**Temel Yaklaşımlar ve İlk Deneyler**

### **Notebook 2**: `02_gelistirme_kodlari.ipynb`
**Model Karşılaştırmaları ve RAG Sistemleri**

### **Notebook 3**: `03_gelistirme_kodlari.ipynb`
**Final Sistem ve Optimizasyonlar**

---

## Notebook 1: Temel Yaklaşımlar

### **Test Edilen Yöntemler:**

#### 1. **BM25 (Sparse Retriever)**
- **Yaklaşım**: Klasik extractive QA
- **Pipeline**: InMemoryDocumentStore + BM25Retriever + FARMReader
- **Model**: `savasy/bert-base-turkish-squad`
- **Özellik**: Hızlı, yerel çalışma, GPU gereksinimsiz
- **Sonuç**: Sadece metinden alıntı yapar, generative değil

#### 2. **Dense Retriever (FAISS + Embedding)**
- **Yaklaşım**: Semantic search tabanlı
- **Embedding Model**: `emrecan/bert-base-turkish-cased-mean-nli-stsb-tr`
- **Reader Model**: `savasy/bert-base-turkish-squad`
- **Özellik**: Anlam bütünlüğü korunur, daha isabetli sonuçlar

### **Ana Bulgular:**
- **Extractive QA vs RAG**: Türkçe için extractive QA daha pratik
- **4 farklı versiyon** geliştirildi, Dense Retriever en iyi sonuç
- **Dense retriever** daha iyi semantic anlama sağlar
- **BM25** hızlı ama yüzeysel eşleştirme yapar
- **Foundation** for RAG-based approach established

---

## Notebook 2: Model Karşılaştırmaları

### **Test Edilen LLM Modelleri:**

1. **kadirnar/turkish-gemma9b-v0** 
2. **WiroAI/wiroai-turkish-llm-9b**
3. **KOCDIGITAL/Kocdigital-LLM-8b-v0**
4. **Orbina/Orbita-v0.1** 
5. **ytu-ce-cosmos/Turkish-Gemma-9b-v0.1** 

### **Embedding & Re-ranking Modelleri:**

- **Ana Embedding**: `atasoglu/turkish-e5-large-m2v`
- **Re-ranker**: `seroe/jina-reranker-v2-base-multilingual-turkish-reranker-triplet_v1`
- **FAISS**: Yüksek hızlı similarity search

### 📈 **Performans Sonuçları:**

| Model | Doğru Cevap | Kısmen Doğru | Yanlış | Başarı Oranı |
|-------|-------------|---------------|---------|---------------|
| **kadirnar/turkish-gemma9b-v0** | 5 | 2 | 3 | **60%** |
| **WiroAI/wiroai-turkish-llm-9b** | 3 | 2 | 5 | **40%** |
| **KOCDIGITAL/Kocdigital-LLM-8b-v0.1** | 8 | 2 |  | **90%** ⭐ |
| **Orbina/Orbita-v0.1** | 1 | 4 | 5 | **30%** |
| **ytu-ce-cosmos/Turkish-Gemma-9b-v0.1** | 7 | 1 | 2 | **75%** |

### 🏆 **Kritik Sonuç:**
> **İlk testlerde KOCDIGITAL en iyi (%90) görünse de, kapsamlı testlerde ytu-cosmos modeli (%95) en kararlı performansı göstermiştir**

---

## Notebook 3: Final Sistem ve Optimizasyonlar

### **Odak Modeli**: `ytu-ce-cosmos/Turkish-Gemma-9b-v0.1`

#### **Sistem Optimizasyonları:**
- **Re-ranker Çıkarıldı**: Hız performansı için
- **Embedding**: `emrecan/bert-base-turkish-cased-mean-nli-stsb-tr` (hız odaklı)
- **Top-K Azaltıldı**: İlk 5 cevap (performans iyileştirmesi)

### **Çoklu PDF Test Sonuçları:**

#### **En İyi İki Model - Kapsamlı Test (3 PDF, 30 Soru):**

| Model | Doğru | Kısmen | Yanlış | Başarı | Kararlılık |
|-------|-------|--------|---------|---------|------------|
| **KOCDIGITAL/Kocdigital-LLM-8b-v0.1** | 10 | 7 | 13 | **45%** | ❌ Düşük |
| **ytu-ce-cosmos/Turkish-Gemma-9b-v0.1** | 27 | 3 | 0 | **95%** | ✅ Yüksek |

#### **📊 Performans Analizi:**
- **KOCDIGITAL**: İlk testlerde %90 → Kapsamlı testlerde %45 (**%45 düşüş!**)
- **ytu-cosmos**: İlk testlerde %75 → Kapsamlı testlerde %95 (**%20 artış!**)

### **Detaylı Performans Analizi:**

**Test Metrikleri:**
- **Toplam Soru**: 30 adet (3 PDF × 10 soru)
- **Test Edilen Model**: 2 adet (en iyi iki model)
- **Kararlılık Testi**: KOCDIGITAL %45 düşüş, ytu-cosmos %20 artış
- **Alakalı Cevap Oranı**: Ortalama 4.2/10 (chunk'larda)
- **Hız**: Re-ranker olmadan %40 daha hızlı
- **Final Doğruluk**: %95 genel başarı oranı (ytu-cosmos)

---

## 🎯 En İyi Performans Konfigürasyonu

### 🏆 **Final Sistem Özellikleri:**

```python
# Model Stack
LLM: "ytu-ce-cosmos/Turkish-Gemma-9b-v0.1"
Embedding: "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr"
Search: FAISS IndexFlatL2

# Optimizasyon Parametreleri
top_k: 5
chunk_size: 500 tokens
chunk_stride: 100 tokens
temperature: 0.4
max_new_tokens: 150
```

### ✅ **Avantajlar:**
- **%95 doğruluk oranı** 
- **Hızlı response time**
- **Çoklu PDF desteği**
- **Stable performance**

### ⚠️ **Bilinen Limitasyonlar:**
- Yazım yanlışları hala mevcut
- Çok hızlı olduğu söylenemez
- GPU gereksinimi (önerilen)

---

## 🔄 Geliştirme Evrimi

### **Faz 1**: Proof of Concept
- BM25 vs Dense retriever
- Temel Türkçe model testleri
- Extractive QA yaklaşımı

### **Faz 2**: Model Optimizasyonu  
- 5 farklı LLM karşılaştırması
- RAG pipeline geliştirme
- Re-ranking model entegrasyonu

### **Faz 3**: Production Ready
- En iyi iki model detaylı test (KOCDIGITAL vs ytu-cosmos)
- Kararlılık analizi (ytu-cosmos kazandı)
- Hız optimizasyonları
- Çoklu PDF sistemi
- %95 stable accuracy achievement

---

## Kritik Model Seçim Analizi

### **İlk Test Sonuçları vs Kapsamlı Test Karşılaştırması:**

| Model | İlk Test | Kapsamlı Test | Kararlılık | Son Karar |
|-------|----------|---------------|------------|-----------|
| **KOCDIGITAL** | %90 ⭐ | %45 ❌ | **-45% düşüş** | Reddedildi |
| **ytu-cosmos** | %75 | %95 ⭐ | **+20% artış** | ✅ Seçildi |

### 🔍 **Kararlılık Analizi:**

#### **KOCDIGITAL/Kocdigital-LLM-8b-v0.1**
- **Avantajları**: İlk testlerde yüksek performans (%90)
- **Dezavantajları**: Kapsamlı testlerde dramatik düşüş (%45)
- **Risk**: Overfiit eğilimi, inconsistent behavior
- **Kararsızlık Oranı**: %45 performance drop

#### **ytu-ce-cosmos/Turkish-Gemma-9b-v0.1**
- **Avantajları**: Tutarlı performans artışı (%75 → %95)
- **Kararlılık**: Çoklu test ortamında stabile performance
- **Güvenilirlik**: Sürekli improvement pattern
- **İyileştirme Oranı**: %20 performance increase

### 🏆 **Final Sonuç:**
> **ytu-cosmos modeli sadece daha iyi değil, aynı zamanda daha kararlı ve güvenilir. Production ortamı için ideal seçim.**

---

## Performans İyileştirmeleri

| Optimizasyon | Öncesi | Sonrası | İyileştirme |
|-------------|--------|---------|-------------|
| **Re-ranker Removal** | Yavaş | +40% hız | ⚡ Hız |
| **Top-K Reduction** | 10 chunk | 5 chunk | 🎯 Odak |
| **Model Selection** | KOCDIGITAL 45% | ytu-cosmos 95% | 🚀 Kararlılık |
| **Multi-PDF Support** | Tek dosya | Çoklu | 📚 Esneklik |

---

## Test Metodolojisi

### **Test Seti:**
- **3 farklı PDF** (farklı konular)
- **Her PDF için 10 soru** 
- **Toplam 30 test sorusu**
- **Çeşitli zorluk seviyeleri**

### **Değerlendirme Kriterleri:**
- ✅ **Doğru**: Tam ve doğru cevap
- 🟡 **Kısmen**: Eksik ama doğru bilgi
- ❌ **Yanlış**: Hatalı veya alakasız

## 📋 Teknik Detaylar

### **Hardware Requirements:**
- **CPU**: 8+ çekirdek önerilen
- **RAM**: 16GB+ (modele bağlı)
- **GPU**: NVIDIA CUDA destekli (opsiyonel ama önerilen)
- **Storage**: 10GB+ model dosyaları için

### **Software Stack:**
```bash
torch>=2.6.0
transformers>=4.53.1
sentence-transformers>=4.1.0
faiss-cpu>=1.11.0
PyPDF2>=3.0.1
numpy>=2.0.2
```

### **Model Sizes:**
- **LLM**: ~9B parametre
- **Embedding**: ~110M parametre  
- **Total Memory**: ~18GB GPU (optimal)
