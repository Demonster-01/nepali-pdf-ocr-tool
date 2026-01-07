#!/usr/bin/env python3
"""
PDF OCR Tool - Convert PDFs with custom fonts to searchable PDFs with proper Unicode text
Supports GPU acceleration via EasyOCR for faster processing
"""

import os
import sys
import argparse
from pathlib import Path
from tqdm import tqdm
import easyocr
from pdf2image import convert_from_path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import torch


def check_gpu():
    """Check if GPU is available for processing"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✓ GPU detected: {gpu_name}")
        print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        return True
    else:
        print("⚠ No GPU detected. Using CPU (will be slower)")
        return False


def initialize_ocr(use_gpu=True):
    """Initialize EasyOCR reader with Nepali language support"""
    print("\n📚 Initializing OCR engine...")
    print("   Loading Nepali language model (this may take a moment on first run)...")
    
    # Initialize reader with Nepali and English languages
    reader = easyocr.Reader(['ne', 'en'], gpu=use_gpu)
    print("   ✓ OCR engine ready")
    return reader


def pdf_to_images(pdf_path, dpi=200, max_pages=None):
    """Convert PDF pages to images using multithreading"""
    import multiprocessing
    # Use half the available cores for image conversion to stay safe
    num_threads = max(1, multiprocessing.cpu_count() // 2)
    
    print(f"\n📄 Converting PDF to images (DPI: {dpi}, Threads: {num_threads})...")
    try:
        kwargs = {
            'dpi': dpi,
            'thread_count': num_threads,
            'last_page': max_pages if max_pages else None
        }
        images = convert_from_path(pdf_path, **kwargs)
        print(f"   ✓ Converted {len(images)} pages")
        return images
    except Exception as e:
        print(f"   ✗ Error converting PDF: {e}")
        sys.exit(1)


def ocr_image(reader, image):
    """Perform OCR on a single image with optimized batching"""
    import numpy as np
    img_array = np.array(image)
    
    # Perform OCR with batch_size=8 for better GPU utilization
    results = reader.readtext(img_array, batch_size=8)
    
    text_blocks = []
    for (bbox, text, confidence) in results:
        if confidence > 0.2:  # Slightly lower threshold for faster modes
            text_blocks.append({
                'text': text,
                'bbox': bbox,
                'confidence': confidence
            })
    
    return text_blocks


def get_devanagari_font():
    """Locate a Devanagari font on the system"""
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", # Fallback
    ]
    for path in font_paths:
        if os.path.exists(path):
            return path
    return None


def create_searchable_pdf(images, text_data, output_path):
    """Create a searchable PDF with OCR'd text using memory-resident images"""
    print(f"\n📝 Creating searchable PDF: {output_path}")
    
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.utils import ImageReader
    
    font_path = get_devanagari_font()
    font_name = "Helvetica"
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont('Devanagari', font_path))
            font_name = "Devanagari"
        except Exception:
            pass

    c = canvas.Canvas(str(output_path), pagesize=letter)
    
    for idx, (image, text_blocks) in enumerate(tqdm(zip(images, text_data), 
                                                      total=len(images),
                                                      desc="   Generating PDF")):
        img_width, img_height = image.size
        aspect_ratio = img_width / img_height
        page_height = 792  
        page_width = page_height * aspect_ratio
        c.setPageSize((page_width, page_height))
        
        c.drawImage(ImageReader(image), 0, 0, width=page_width, height=page_height)
        c.setFillColorRGB(0, 0, 0, alpha=0)  
        
        for block in text_blocks:
            text = block['text']
            bbox = block['bbox']
            x = min(point[0] for point in bbox) * (page_width / img_width)
            y = page_height - (max(point[1] for point in bbox) * (page_height / img_height))
            bbox_height = max(point[1] for point in bbox) - min(point[1] for point in bbox)
            font_size = max(6, bbox_height * (page_height / img_height) * 0.7)
            
            c.setFont(font_name, font_size)
            c.drawString(x, y, text)
        
        c.showPage()
    
    c.save()
    print(f"   ✓ PDF created successfully")


def process_pdf(input_pdf, output_pdf, dpi=200, use_gpu=True, max_pages=None, progress_callback=None):
    """Main processing function with optional progress callback"""
    import time
    start_time = time.time()
    
    print("=" * 60)
    print("PDF OCR Tool - Optimized Nepali Document Processor")
    print("=" * 60)
    
    gpu_available = check_gpu()
    use_gpu = use_gpu and gpu_available
    
    reader = initialize_ocr(use_gpu=use_gpu)
    images = pdf_to_images(input_pdf, dpi=dpi, max_pages=max_pages)

    if not images:
        return None
    
    print(f"\n🔍 Performing OCR on {len(images)} pages...")
    print(f"   (Mode: {dpi} DPI, GPU: {use_gpu})\n")
    
    text_data = []
    for idx, image in enumerate(tqdm(images, desc="   Processing pages")):
        text_blocks = ocr_image(reader, image)
        text_data.append(text_blocks)
        
        if progress_callback:
            progress_callback(idx + 1, len(images), "ocr")
    
    create_searchable_pdf(images, text_data, output_pdf)
    
    if progress_callback:
        progress_callback(len(images), len(images), "complete")

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"✓ Processing complete in {elapsed/60:.1f} minutes!")
    print(f"  Input:  {input_pdf}")
    print(f"  Output: {output_pdf}")
    print(f"  Pages:  {len(images)} ({elapsed/len(images):.1f}s/page)")
    print("=" * 60)
    
    # Return useful data for the API
    return {
        "output_path": output_pdf,
        "page_count": len(images),
        "sample_text": text_data[0][:5] if text_data else []
    }


def main():
    parser = argparse.ArgumentParser(
        description='Convert PDFs with custom fonts to searchable PDFs with proper Unicode text',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input_pdf', type=str, help='Input PDF file path')
    parser.add_argument('output_pdf', type=str, help='Output PDF file path')
    parser.add_argument('--mode', type=str, choices=['fast', 'balanced', 'accurate'], default='balanced',
                        help='Processing mode: fast (150 DPI), balanced (200 DPI), accurate (300 DPI)')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU')
    parser.add_argument('--max-pages', type=int, default=None, help='Process only first N pages')
    
    args = parser.parse_args()
    
    dpi_map = {'fast': 150, 'balanced': 200, 'accurate': 300}
    dpi = dpi_map[args.mode]
    
    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file '{args.input_pdf}' not found")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_pdf)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    process_pdf(args.input_pdf, args.output_pdf, dpi=dpi, use_gpu=not args.no_gpu, max_pages=args.max_pages)


if __name__ == "__main__":
    main()
