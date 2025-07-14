"""
Türkçe PDF QA Sistemi - Ana QA Sınıfı
"""
import torch
import faiss
import numpy as np
from typing import List
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from config import Config
from pdf_processor import PDFProcessor

class TurkishPDFQA:
    """Türkçe PDF Soru-Cevap Ana Sınıfı"""
    
    def __init__(self):
        """Sınıfı başlatır ve modelleri yükler"""
        print("🚀 Türkçe PDF QA sistemi başlatılıyor...")
        
        # Torch optimizasyonu
        torch.set_float32_matmul_precision('high')
        
        # LLM modeli yükleniyor
        print(f"🤖 LLM modeli yükleniyor: {Config.LLM_MODEL_NAME}")
        self.tokenizer = AutoTokenizer.from_pretrained(Config.LLM_MODEL_NAME)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            Config.LLM_MODEL_NAME,
            torch_dtype=Config.TORCH_DTYPE,
            device_map=Config.DEVICE_MAP,
            low_cpu_mem_usage=True
        )
        self.device = next(self.model.parameters()).device
        print(f"✅ LLM modeli yüklendi (Device: {self.device})")
        
        # Embedding modeli yükleniyor
        print(f"🧠 Embedding modeli yükleniyor: {Config.EMBEDDING_MODEL_NAME}")
        self.embed_model = SentenceTransformer(Config.EMBEDDING_MODEL_NAME)
        print("✅ Embedding modeli yüklendi")
        
        # PDF processor
        self.pdf_processor = PDFProcessor(self.tokenizer)
        
        # Veri saklama
        self.pdf_chunks = []
        self.embeddings = None
        self.index = None
        
        print("✅ Sistem hazır!")
    
    def load_pdfs(self, pdf_files: List[str]):
        """PDF dosyalarını yükler ve index oluşturur"""
        print("\n" + Config.SEPARATOR_LINE)
        print("📚 PDF YÜKLEME VE İNDEXLEME")
        print(Config.SEPARATOR_LINE)
        
        try:
            # PDF'leri işle
            self.pdf_chunks = self.pdf_processor.process_pdf_files(pdf_files)
            
            # Embeddings oluştur
            print("🧠 Embedding'ler oluşturuluyor...")
            self.embeddings = self.embed_model.encode(
                self.pdf_chunks, 
                convert_to_numpy=True, 
                show_progress_bar=True
            )
            
            # FAISS index oluştur
            print("🔍 Arama index'i oluşturuluyor...")
            self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
            self.index.add(self.embeddings)
            
            print(f"✅ İndexleme tamamlandı!")
            print(f"   📊 Toplam chunk sayısı: {len(self.pdf_chunks)}")
            print(f"   🎯 Embedding boyutu: {self.embeddings.shape[1]}")
            
        except Exception as e:
            print(f"❌ PDF yükleme hatası: {str(e)}")
            raise
    
    def ask_question(self, question: str, top_k: int = None) -> str:
        """Soruya cevap verir"""
        if not self.is_ready():
            raise ValueError("Sistem hazır değil! Önce PDF dosyalarını yükleyin.")
        
        if top_k is None:
            top_k = Config.DEFAULT_TOP_K
        
        try:
            # Soru embedding'i
            question_embedding = self.embed_model.encode([question], convert_to_numpy=True)
            
            # En yakın chunk'ları bul
            D, I = self.index.search(question_embedding, top_k)
            top_chunks = [self.pdf_chunks[i] for i in I[0]]
            
            # Her chunk için cevap üret
            chunk_answers = []
            for i, chunk in enumerate(top_chunks):
                print(f"🔄 Chunk {i+1}/{len(top_chunks)} işleniyor...")
                answer = self._generate_answer_for_chunk(chunk, question)
                chunk_answers.append(answer)
            
            # Cevapları birleştir
            final_answer = self._fuse_answers(chunk_answers, question)
            return final_answer
            
        except Exception as e:
            print(f"❌ Soru cevaplama hatası: {str(e)}")
            raise
    
    def _generate_answer_for_chunk(self, chunk: str, question: str) -> str:
        """Tek chunk için cevap üretir"""
        prompt = f"""Metin: {chunk}\n\nSoru: {question}\n\nCevap:"""
        
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=Config.MAX_NEW_TOKENS_CHUNK,
                temperature=Config.TEMPERATURE,
                top_p=Config.TOP_P,
                top_k=Config.TOP_K,
                do_sample=False,
                repetition_penalty=Config.REPETITION_PENALTY,
                no_repeat_ngram_size=Config.NO_REPEAT_NGRAM_SIZE,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()
    
    def _fuse_answers(self, answers: List[str], question: str) -> str:
        """Birden fazla cevabı birleştirir"""
        fusion_prompt = "\n".join([f"Parça {i+1} Cevap: {ans}" for i, ans in enumerate(answers)])
        fusion_prompt += f"""

Sadece yukarıdaki cevaplara dayalı teknik ve doğru bir Türkçe cevap ver.
Genel açıklamalardan, tahminlerden ve konu dışı ifadelerden kaçın. Sadece doğrudan sorunun teknik cevabını ver.

SORU: {question}

CEVAP:"""
        
        fusion_inputs = self.tokenizer(
            fusion_prompt, 
            return_tensors="pt", 
            truncation=True, 
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            final_output = self.model.generate(
                **fusion_inputs,
                max_new_tokens=Config.MAX_NEW_TOKENS_FINAL,
                temperature=Config.TEMPERATURE,
                top_p=Config.TOP_P,
                top_k=Config.TOP_K,
                do_sample=False,
                repetition_penalty=Config.REPETITION_PENALTY,
                no_repeat_ngram_size=Config.NO_REPEAT_NGRAM_SIZE,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        final_answer = self.tokenizer.decode(final_output[0], skip_special_tokens=True)
        return final_answer.split("CEVAP:")[-1].strip()
    
    def is_ready(self) -> bool:
        """Sistemin hazır olup olmadığını kontrol eder"""
        return (self.pdf_chunks is not None and 
                len(self.pdf_chunks) > 0 and 
                self.embeddings is not None and 
                self.index is not None)
    
    def get_stats(self) -> dict:
        """Sistem istatistiklerini döndürür"""
        if not self.is_ready():
            return {"status": "not_ready"}
        
        return {
            "status": "ready",
            "chunk_count": len(self.pdf_chunks),
            "embedding_dim": self.embeddings.shape[1],
            "device": str(self.device),
            "model_name": Config.LLM_MODEL_NAME
        } 