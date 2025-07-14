# 🇹🇷 Türkçe PDF Soru-Cevap Sistemi

AI destekli semantik arama ile Türkçe PDF belgelerinizden otomatik soru-cevap yapın.

## ✨ Özellikler

- **Türkçe LLM**: `ytu-ce-cosmos/Turkish-Gemma-9b-v0.1` modeli
- **Semantik Arama**: `emrecan/bert-base-turkish-cased-mean-nli-stsb-tr` embedding modeli
- **Çoklu PDF Desteği**: Birden fazla PDF dosyasını aynı anda işleme
- **FAISS Indexleme**: Hızlı ve verimli arama
- **Chunk Fusion**: Birden fazla parçadan cevap birleştirme

## 🚀 Kurulum

### Gereksinimler

- Python 3.8+
- CUDA (isteğe bağlı, GPU desteği için)

### Adım 1: Repository'yi İndirin

```bash
git clone https://github.com/canertunc/turkish-semantic-qa.git
cd turkish-semantic-qa
```

### Adım 2: Sanal Ortam Oluşturun

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

## 📖 Kullanım

### İnteraktif Mod

```bash
python main.py
```

Program başladığında size PDF dosyası ekleme seçenekleri sunulur:

1. **Tek dosya yolu gir** - Spesifik bir PDF dosyası
2. **Klasör yolu gir** - Klasördeki tüm PDF'ler
3. **Dosya yollarını liste halinde gir** - Birden fazla dosya yolu
4. **Manuel dosya ekleme** - Tek tek dosya ekleme

### Command Line Kullanımı

#### Tek PDF Dosyası

```bash
python main.py -f document.pdf
```

#### Birden Fazla PDF

```bash
python main.py -f doc1.pdf doc2.pdf doc3.pdf
```

#### Klasördeki Tüm PDF'ler

```bash
python main.py -d ./documents
```

#### Belirli Bir Soruyla Başlama

```bash
python main.py -f document.pdf -q "Bu belge neyi anlatıyor?"
```

#### Gelişmiş Seçenekler

```bash
python main.py -f document.pdf --top-k 10 --interactive
```

### Command Line Parametreleri

| Parametre | Kısaltma | Açıklama |
|-----------|----------|-----------|
| `--files` | `-f` | PDF dosya yolları |
| `--directory` | `-d` | PDF klasör yolu |
| `--question` | `-q` | Başlangıç sorusu |
| `--top-k` | | Arama chunk sayısı (varsayılan: 5) |
| `--interactive` | | İnteraktif mod zorla |

## 🏗️ Proje Yapısı

```
turkish_semantic_qa/
├── main.py              # Ana script - giriş noktası
├── config.py            # Konfigürasyon ayarları
├── pdf_qa.py            # Ana QA sınıfı
├── pdf_processor.py     # PDF işleme modülü
├── utils.py             # Yardımcı fonksiyonlar
├── requirements.txt     # Python bağımlılıkları
├── README.md           
└── development/         # Geliştirme kodları
    ├── 01_gelistirme_kodlari.ipynb    # Model karşılaştırmaları, temel testler ve farklı teknikler
    ├── 02_gelistirme_kodlari.ipynb    
    ├── 03_gelistirme_kodlari.ipynb    
    └── README_development.md          # Geliştirme notları ve sonuçlar
```

### Modül Açıklamaları

#### `config.py`
- Model isimleri ve parametreleri
- Chunk ayarları
- Generation parametreleri
- Sistem konfigürasyonu

#### `pdf_processor.py`
- PDF okuma ve metin çıkarma
- Metin temizleme
- Token bazlı chunk'lara bölme

#### `pdf_qa.py`
- Ana QA sınıfı
- Model yükleme ve yönetimi
- Embedding ve indexleme
- Soru cevaplama pipeline'ı

#### `utils.py`
- Dosya validasyonu
- İnteraktif kullanıcı arayüzü
- PDF dosya bulma
- Yardımcı fonksiyonlar

#### `main.py`
- Command line argument parsing
- Ana program akışı
- Hata yönetimi

#### `development/`
Geliştirme aşamasında kullanılan kodlar ve testler:

- **`01_gelistirme_kodlari.ipynb`**: BM25 vs Dense Retriever karşılaştırması, extractive QA yaklaşımı, 4 farklı versiyon
- **`02_gelistirme_kodlari.ipynb`**: 5 LLM modelinin karşılaştırması, KOCDIGITAL %90, ytu-cosmos %75 başarı
- **`03_gelistirme_kodlari.ipynb`**: En iyi 2 model kapsamlı testi, kararlılık analizi, ytu-cosmos %95 final
- **`README_development.md`**: Kapsamlı geliştirme süreci, model kararlılık analizi ve kritik performans raporları

## ⚙️ Konfigürasyon

`config.py` dosyasında aşağıdaki ayarları değiştirebilirsiniz:

```python
# Model ayarları
LLM_MODEL_NAME = "ytu-ce-cosmos/Turkish-Gemma-9b-v0.1"
EMBEDDING_MODEL_NAME = "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr"

# Chunk ayarları
CHUNK_SIZE = 500          # Token sayısı
CHUNK_STRIDE = 100        # Overlap miktarı

# Generation ayarları
TEMPERATURE = 0.4         # Yaratıcılık seviyesi
TOP_K = 40               # Token seçim sayısı
MAX_NEW_TOKENS_FINAL = 150 # Maksimum cevap uzunluğu
```

## 🎯 Kullanım İpuçları

### PDF Dosyası Ekleme

1. **Drag & Drop**: Dosya yollarını doğrudan kopyalayıp yapıştırabilirsiniz
2. **Klasör Tarama**: Büyük klasörlerde otomatik PDF bulma
3. **Batch İşlem**: Birden fazla dosyayı aynı anda işleme
4. **Dosya Validasyonu**: Otomatik dosya kontrolü ve hata raporlama

### Soru Sorma

- ✅ **İyi**: "Bu belgede bahsedilen ana konular nelerdir?"
- ✅ **İyi**: "Şirketin 2023 yılı geliri ne kadardır?"
- ❌ **Kötü**: "Nasılsın?" (belge ile ilgisiz)
- ❌ **Kötü**: "Evet" (belirsiz)

### Performans Optimizasyonu

- **GPU kullanın**: CUDA destekli GPU varsa otomatik kullanılır
- **Chunk sayısını ayarlayın**: `--top-k` parametresi ile
- **Dosya boyutunu kontrol edin**: Çok büyük dosyalar parçalara bölünür

## 🔧 Sorun Giderme

### Yaygın Hatalar

#### "PDF okuma hatası"
- PDF dosyası bozuk olabilir
- Dosya şifreli olabilir
- Dosya yolu hatalı olabilir

#### "Bellek hatası"
- PDF dosyası çok büyük
- `CHUNK_SIZE` değerini küçültün
- GPU belleği yetersiz

#### "Model yükleme hatası"
- İnternet bağlantısını kontrol edin
- Disk alanını kontrol edin
- Gerekli paketlerin yüklü olduğundan emin olun

### Performans İpuçları

1. **GPU Kullanımı**: CUDA yüklü ise otomatik GPU kullanılır
2. **Bellek Optimizasyonu**: Büyük dosyalar için chunk boyutunu küçültün
3. **Hız Optimizasyonu**: `top_k` değerini azaltın

## 📋 Sistem Gereksinimleri

### Minimum Gereksinimler
- **CPU**: 4 çekirdek, 2.0 GHz
- **RAM**: 8 GB
- **Disk**: 10 GB boş alan
- **Python**: 3.8+

### Önerilen Gereksinimler
- **CPU**: 8 çekirdek, 3.0 GHz
- **RAM**: 16 GB
- **GPU**: NVIDIA RTX 3060 veya üzeri
- **Disk**: SSD, 20 GB boş alan
