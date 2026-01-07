#!/usr/bin/env python3
"""
Quick test script - Process just the first 3 pages for testing
"""

import subprocess
import sys

# Run the main OCR script but extract only first 3 pages from the PDF
print("Creating a 3-page sample PDF for quick testing...")
subprocess.run([
    "pdftk", "muluki_ain.pdf", "cat", "1-3", "output", "sample_3pages.pdf"
], check=False)

# If pdftk is not available, we'll process all pages but with reduced DPI
import os
if not os.path.exists("sample_3pages.pdf"):
    print("⚠ pdftk not found, will demonstrate with full PDF (may take 10-15 minutes)")
    print("\nTo speed this up, install pdftk:")
    print("  sudo apt-get install pdftk")
    print("\nProceeding with full PDF processing...")
    input("Press Enter to continue or Ctrl+C to cancel...")
    subprocess.run(["uv", "run", "pdf_ocr.py", "muluki_ain.pdf", "muluki_ain_ocr.pdf"])
else:
    print("✓ Created 3-page sample\n")
    print("Processing 3 pages (this will take ~2-3 minutes)...\n")
    subprocess.run(["uv", "run", "pdf_ocr.py", "sample_3pages.pdf", "sample_3pages_ocr.pdf"])
    print("\n" + "="*60)
    print("✓ Test complete! Check sample_3pages_ocr.pdf")
    print("  Open it and try copying text - it should be proper Nepali Unicode!")
    print("="*60)
