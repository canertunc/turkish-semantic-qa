#!/usr/bin/env python3
"""
Türkçe PDF QA Sistemi - Ana Script
Kullanım:
    python main.py                          # İnteraktif mod
    python main.py -f dosya.pdf             # Tek dosya
    python main.py -f dosya1.pdf dosya2.pdf # Birden fazla dosya
    python main.py -d /path/to/folder       # Klasördeki tüm PDF'ler
"""
import argparse
import sys
import os
from typing import List, Optional

from config import Config
from utils import (
    print_banner, 
    get_pdf_files_interactive, 
    print_files_summary, 
    get_confirmation,
    validate_pdf_file,
    find_pdf_files
)
from pdf_qa import TurkishPDFQA

def parse_arguments():
    """Command line argümanlarını parse eder"""
    parser = argparse.ArgumentParser(
        description="Türkçe PDF Soru-Cevap Sistemi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım örnekleri:
  python main.py                           # İnteraktif mod
  python main.py -f document.pdf           # Tek dosya
  python main.py -f doc1.pdf doc2.pdf      # Birden fazla dosya  
  python main.py -d ./documents            # Klasördeki tüm PDF'ler
  python main.py -f doc.pdf -q "Soru?"     # Tek soru ile başlat
        """
    )
    
    parser.add_argument(
        '-f', '--files',
        nargs='+',
        help='PDF dosya yolları'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='PDF dosyalarının bulunduğu klasör'
    )
    
    parser.add_argument(
        '-q', '--question',
        help='Başlangıç sorusu'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=Config.DEFAULT_TOP_K,
        help=f'Arama için kullanılacak chunk sayısı (varsayılan: {Config.DEFAULT_TOP_K})'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Dosya seçimi için interaktif modu zorla'
    )
    
    return parser.parse_args()

def get_pdf_files_from_args(args) -> List[str]:
    """Command line argümanlarından PDF dosyalarını alır"""
    pdf_files = []
    
    if args.files:
        # Dosya yolları verilmiş
        for file_path in args.files:
            if validate_pdf_file(file_path):
                pdf_files.append(file_path)
                
    elif args.directory:
        # Klasör yolu verilmiş
        if os.path.isdir(args.directory):
            found_files = find_pdf_files(args.directory)
            if found_files:
                print(f"📁 {args.directory} klasöründe {len(found_files)} PDF dosyası bulundu:")
                for i, f in enumerate(found_files, 1):
                    print(f"   {i}. {os.path.basename(f)}")
                
                if get_confirmation("Tümünü yükle?"):
                    pdf_files.extend(found_files)
            else:
                print(f"❌ {args.directory} klasöründe PDF dosyası bulunamadı")
        else:
            print(f"❌ Geçersiz klasör: {args.directory}")
    
    return pdf_files

def run_qa_session(qa_system: TurkishPDFQA, initial_question: Optional[str] = None, top_k: int = None):
    """Soru-cevap oturumunu çalıştırır"""
    print("\n" + Config.SEPARATOR_LINE)
    print("🤖 SORU-CEVAP OTURUMU")
    print(Config.SEPARATOR_LINE)
    print("💡 İpuçları:")
    print("   • Açık ve spesifik sorular sorun")
    print("   • 'çık', 'exit' veya 'quit' ile çıkabilirsiniz")
    print("   • 'stats' ile sistem istatistiklerini görebilirsiniz")
    print(Config.SEPARATOR_LINE)
    
    # İlk soru varsa sor
    if initial_question:
        print(f"📝 İlk Soru: {initial_question}")
        try:
            answer = qa_system.ask_question(initial_question, top_k)
            print(f"\n🤖 Cevap: {answer}")
            print(Config.QUESTION_SEPARATOR)
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
    
    # Ana soru-cevap döngüsü
    while True:
        try:
            question = input("\n🤔 Sorunuz: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['çık', 'exit', 'quit']:
                print("👋 Görüşmek üzere!")
                break
                
            if question.lower() == 'stats':
                stats = qa_system.get_stats()
                print("\n📊 Sistem İstatistikleri:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                continue
            
            print("🔍 Cevap aranıyor...")
            answer = qa_system.ask_question(question, top_k)
            print(f"\n🤖 Cevap: {answer}")
            print(Config.QUESTION_SEPARATOR)
            
        except KeyboardInterrupt:
            print("\n\n👋 Program sonlandırıldı!")
            break
        except Exception as e:
            print(f"\n❌ Hata: {str(e)}")
            print("🔄 Tekrar deneyin veya farklı bir soru sorun.")

def main():
    """Ana program"""
    try:
        # Banner göster
        print_banner()
        
        # Argümanları parse et
        args = parse_arguments()
        
        # PDF dosyalarını al
        if args.interactive or (not args.files and not args.directory):
            # İnteraktif mod
            pdf_files = get_pdf_files_interactive()
        else:
            # Command line'dan dosya yolları
            pdf_files = get_pdf_files_from_args(args)
        
        # Dosya kontrolü
        if not print_files_summary(pdf_files):
            sys.exit(1)
        
        if not get_confirmation("PDF'leri yükleyip sistemi başlat?"):
            print("❌ İşlem iptal edildi.")
            sys.exit(0)
        
        # QA sistemini başlat
        print("\n" + Config.SEPARATOR_LINE)
        print("🚀 SİSTEM BAŞLATILIYOR")
        print(Config.SEPARATOR_LINE)
        
        qa_system = TurkishPDFQA()
        
        # PDF'leri yükle
        qa_system.load_pdfs(pdf_files)
        
        # Soru-cevap oturumunu başlat
        run_qa_session(qa_system, args.question, args.top_k)
        
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Kritik hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 