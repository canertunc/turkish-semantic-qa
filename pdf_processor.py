"""
Türkçe PDF QA Sistemi - PDF İşleme Modülü
"""
import PyPDF2
import io
from typing import List, Union, BinaryIO
from config import Config
from utils import clean_text

class PDFProcessor:
    """PDF dosyalarını işleme ve metin çıkarma sınıfı"""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
    
    def extract_text_from_pdf(self, pdf_source: Union[str, BinaryIO]) -> str:
        """Tek PDF dosyasından metin çıkarır"""
        print("📄 PDF okunuyor...")
        
        if isinstance(pdf_source, str):
            # Dosya yolu verilmiş
            with open(pdf_source, 'rb') as file:
                return self._extract_text_from_file(file)
        else:
            # Dosya objesi verilmiş
            return self._extract_text_from_file(pdf_source)
    
    def extract_text_from_multiple_pdfs(self, pdf_sources: List[Union[str, BinaryIO]]) -> str:
        """Birden fazla PDF dosyasından metin çıkarır ve birleştirir"""
        print(f"📚 {len(pdf_sources)} PDF dosyası işleniyor...")
        all_texts = []
        
        for i, pdf_source in enumerate(pdf_sources, 1):
            print(f"📄 PDF {i}/{len(pdf_sources)} işleniyor...")
            try:
                text = self.extract_text_from_pdf(pdf_source)
                if text.strip():
                    all_texts.append(text)
                    print(f"✅ PDF {i} başarıyla işlendi ({len(text)} karakter)")
                else:
                    print(f"⚠️  PDF {i} boş veya okunamadı")
            except Exception as e:
                print(f"❌ PDF {i} işlenirken hata: {str(e)}")
                continue
        
        if not all_texts:
            raise ValueError("Hiçbir PDF dosyasından metin çıkarılamadı!")
        
        # Tüm metinleri birleştir
        combined_text = "\n\n--- YENİ DÖKÜMAN ---\n\n".join(all_texts)
        print(f"✅ Toplam {len(all_texts)} PDF birleştirildi ({len(combined_text)} karakter)")
        return combined_text
    
    def _extract_text_from_file(self, file_obj: BinaryIO) -> str:
        """Dosya objesinden metin çıkarır"""
        try:
            reader = PyPDF2.PdfReader(file_obj)
            full_text = ""
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                except Exception as e:
                    print(f"⚠️  Sayfa {page_num} okunurken hata: {str(e)}")
                    continue
            
            return clean_text(full_text)
            
        except Exception as e:
            raise Exception(f"PDF okuma hatası: {str(e)}")
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """Metni token bazlı parçalara böler"""
        print("🔪 Metin token bazlı parçalara bölünüyor...")
        
        try:
            tokens = self.tokenizer.encode(text, add_special_tokens=False)
            chunks = []
            start = 0
            
            while start < len(tokens):
                end = min(start + Config.CHUNK_SIZE, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk_text = self.tokenizer.decode(chunk_tokens, clean_up_tokenization_spaces=True)
                chunks.append(chunk_text)
                start += Config.CHUNK_SIZE - Config.CHUNK_STRIDE
            
            print(f"✅ Metin {len(chunks)} parçaya bölündü")
            return chunks
            
        except Exception as e:
            raise Exception(f"Metin bölme hatası: {str(e)}")
    
    def process_pdf_files(self, pdf_files: List[str]) -> List[str]:
        """PDF dosyalarını işleyip chunk'lara böler"""
        print("🚀 PDF işleme başlıyor...")
        
        if len(pdf_files) == 1:
            # Tek dosya
            combined_text = self.extract_text_from_pdf(pdf_files[0])
        else:
            # Birden fazla dosya
            combined_text = self.extract_text_from_multiple_pdfs(pdf_files)
        
        if not combined_text.strip():
            raise ValueError("PDF'lerden hiç metin çıkarılamadı!")
        
        # Chunk'lara böl
        chunks = self.split_text_into_chunks(combined_text)
        
        if not chunks:
            raise ValueError("Metin chunk'lara bölünemedi!")
        
        return chunks 