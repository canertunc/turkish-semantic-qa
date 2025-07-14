"""
Türkçe PDF QA Sistemi Yardımcı Fonksiyonları
"""
import os
import re
import glob
from pathlib import Path
from typing import List, Optional
from config import Config

def clean_text(text: str) -> str:
    """Metni temizler ve normalleştirir"""
    # Fazla boşlukları temizle
    clean = re.sub(r'\s+', ' ', text)
    # Özel karakterleri temizle (Türkçe karakterleri koru)
    clean = re.sub(r'[^\w\s.,!?;:()\-]', '', clean)
    return clean.strip()

def validate_pdf_file(file_path: str) -> bool:
    """PDF dosyasının geçerli olup olmadığını kontrol eder"""
    if not os.path.exists(file_path):
        print(f"❌ Dosya bulunamadı: {file_path}")
        return False
    
    if not file_path.lower().endswith('.pdf'):
        print(f"❌ Desteklenmeyen dosya formatı: {file_path}")
        return False
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > Config.MAX_PDF_SIZE_MB:
        print(f"❌ Dosya çok büyük ({file_size_mb:.1f}MB): {file_path}")
        return False
    
    return True

def find_pdf_files(directory: str) -> List[str]:
    """Dizindeki tüm PDF dosyalarını bulur"""
    pdf_files = []
    for pattern in ['*.pdf', '*.PDF']:
        pdf_files.extend(glob.glob(os.path.join(directory, pattern)))
        pdf_files.extend(glob.glob(os.path.join(directory, '**', pattern), recursive=True))
    
    return sorted(list(set(pdf_files)))

def get_pdf_files_interactive() -> List[str]:
    """Kullanıcıdan PDF dosyalarını interaktif olarak alır"""
    pdf_files = []
    
    print("\n🔍 PDF Dosyası Ekleme Seçenekleri:")
    print("1️⃣  Tek dosya yolu gir")
    print("2️⃣  Klasör yolu gir (tüm PDF'ler)")
    print("3️⃣  Dosya yollarını liste halinde gir")
    print("4️⃣  Manuel dosya ekleme (tek tek)")
    
    choice = input("\nSeçiminiz (1-4): ").strip()
    
    if choice == "1":
        file_path = input("PDF dosya yolu: ").strip().strip('"\'')
        if validate_pdf_file(file_path):
            pdf_files.append(file_path)
            
    elif choice == "2":
        dir_path = input("Klasör yolu: ").strip().strip('"\'')
        if os.path.isdir(dir_path):
            found_files = find_pdf_files(dir_path)
            if found_files:
                print(f"📁 {len(found_files)} PDF dosyası bulundu:")
                for i, f in enumerate(found_files, 1):
                    print(f"   {i}. {os.path.basename(f)}")
                
                if input("\nTümünü ekle? (e/h): ").lower().startswith('e'):
                    pdf_files.extend(found_files)
            else:
                print("❌ Klasörde PDF dosyası bulunamadı")
        else:
            print("❌ Geçersiz klasör yolu")
            
    elif choice == "3":
        print("Dosya yollarını virgül veya yeni satırla ayırarak girin (çift ENTER ile bitirin):")
        paths_input = ""
        while True:
            line = input()
            if line == "":
                break
            paths_input += line + "\n"
        
        # Virgül veya yeni satırla ayrılmış dosya yolları
        paths = re.split(r'[,\n]+', paths_input)
        for path in paths:
            path = path.strip().strip('"\'')
            if path and validate_pdf_file(path):
                pdf_files.append(path)
                
    elif choice == "4":
        print("Dosya yollarını tek tek girin (boş satır ile bitirin):")
        while True:
            file_path = input("PDF dosya yolu (boş=bitir): ").strip().strip('"\'')
            if not file_path:
                break
            if validate_pdf_file(file_path):
                pdf_files.append(file_path)
                print(f"✅ Eklendi: {os.path.basename(file_path)}")
    
    else:
        print("❌ Geçersiz seçim")
    
    return pdf_files

def print_banner():
    """Program başlangıç banner'ını yazdırır"""
    print(Config.SEPARATOR_LINE)
    print("🇹🇷 TÜRKÇe PDF SORU-CEVAP SİSTEMİ")
    print("   AI Destekli Semantik Arama")
    print(Config.SEPARATOR_LINE)

def print_files_summary(pdf_files: List[str]):
    """Yüklenen dosyaların özetini yazdırır"""
    if not pdf_files:
        print("❌ Hiç PDF dosyası seçilmedi!")
        return False
    
    print(f"\n📚 {len(pdf_files)} PDF dosyası yüklenecek:")
    for i, file_path in enumerate(pdf_files, 1):
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        print(f"   {i}. {os.path.basename(file_path)} ({file_size:.1f}MB)")
    
    return True

def get_confirmation(message: str = "Devam edilsin mi?") -> bool:
    """Kullanıcıdan onay alır"""
    response = input(f"\n{message} (e/h): ").strip().lower()
    return response.startswith('e') 