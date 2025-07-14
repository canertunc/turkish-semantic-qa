"""
Türkçe PDF QA Sistemi Konfigürasyon Ayarları
"""
import torch

class Config:
    """Ana konfigürasyon sınıfı"""
    
    # Model ayarları
    LLM_MODEL_NAME = "ytu-ce-cosmos/Turkish-Gemma-9b-v0.1"
    EMBEDDING_MODEL_NAME = "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr"
    
    # Chunk ayarları
    CHUNK_SIZE = 500
    CHUNK_STRIDE = 100
    
    # Arama ayarları
    DEFAULT_TOP_K = 5
    
    # Generation ayarları
    MAX_NEW_TOKENS_CHUNK = 100
    MAX_NEW_TOKENS_FINAL = 150
    TEMPERATURE = 0.4
    TOP_P = 0.95
    TOP_K = 40
    REPETITION_PENALTY = 1.1
    NO_REPEAT_NGRAM_SIZE = 3
    
    # Sistem ayarları
    USE_CUDA = torch.cuda.is_available()
    TORCH_DTYPE = torch.float16 if USE_CUDA else torch.float32
    DEVICE_MAP = "auto" if USE_CUDA else None
    
    # Dosya ayarları
    SUPPORTED_EXTENSIONS = ['.pdf']
    MAX_PDF_SIZE_MB = 100
    
    # UI Ayarları
    SEPARATOR_LINE = "=" * 80
    QUESTION_SEPARATOR = "-" * 80 