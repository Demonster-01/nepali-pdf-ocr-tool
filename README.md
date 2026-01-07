# PDF OCR Tool for Nepali Documents

Convert PDFs with custom/non-standard fonts into searchable PDFs with proper Unicode text. This tool uses GPU-accelerated OCR (EasyOCR) to extract text from Nepali documents.

## Problem It Solves

When you copy text from PDFs with custom fonts (especially Nepali documents), you often get garbled Unicode characters like:
```
tyf Joj:yf sfod u/L ;j{;fwf/0fsf]
```

This tool performs OCR on the PDF and creates a new searchable PDF where copied text appears as proper Nepali Unicode (Devanagari script).

## Features

- ✅ **GPU Acceleration**: Utilizes your NVIDIA GPU (RTX 3050) for faster processing
- ✅ **Nepali Language Support**: Optimized for Devanagari script
- ✅ **Multi-page Processing**: Handles PDFs of any length with progress tracking
- ✅ **Searchable Output**: Generated PDFs are fully searchable and copyable
- ✅ **High Quality**: Configurable DPI settings for optimal results

## Requirements

### System Dependencies

Install poppler-utils for PDF processing:
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils
```

### Python Dependencies

The project uses UV for dependency management:

```bash
# Dependencies are already configured in pyproject.toml
uv sync
```

Or to add more packages:
```bash
uv add package-name
```

**Note**: On first run, EasyOCR will automatically download the Nepali language model (~100MB). This is a one-time download.

## Installation

```bash
cd /home/personal/Desktop/learning/pdf-ocr-tool
uv sync
```

## Usage

### Basic Usage

```bash
uv run pdf_ocr.py input.pdf output.pdf
```

### Advanced Options

```bash
# Higher quality (slower processing)
uv run pdf_ocr.py input.pdf output.pdf --dpi 400

# Use CPU only (no GPU)
uv run pdf_ocr.py input.pdf output.pdf --no-gpu

# Show help
uv run pdf_ocr.py --help
```

## Example with Your PDF

```bash
# Download the test PDF
wget "https://supremecourt.gov.np/web/assets/downloads/%E0%A4%AE%E0%A5%81%E0%A4%B2%E0%A5%81%E0%A4%95%E0%A5%80-%E0%A4%85%E0%A4%AA%E0%A4%B0%E0%A4%BE%E0%A4%A7-%E0%A4%B8%E0%A4%82%E0%A4%B9%E0%A4%BF%E0%A4%A4%E0%A4%BE-%E0%A4%90%E0%A4%A8-%E0%A5%A8%E0%A5%A6%E0%A5%AD%E0%A5%AA.pdf" -O muluki_ain.pdf

# Process it
uv run pdf_ocr.py muluki_ain.pdf muluki_ain_ocr.pdf

# Now open muluki_ain_ocr.pdf and copy text - it will be proper Nepali Unicode!
```

## How It Works

1. **PDF → Images**: Converts each PDF page to high-resolution images
2. **OCR Processing**: Uses EasyOCR with Nepali language model to extract text
3. **PDF Generation**: Creates a new PDF with:
   - Original images as the visual layer
   - Extracted text as an invisible searchable layer
4. **Result**: A PDF that looks identical but has proper copyable Unicode text

## GPU vs CPU Performance

- **With GPU (RTX 3050)**: ~5-10 seconds per page
- **With CPU only**: ~30-60 seconds per page

For long documents, GPU acceleration makes a significant difference!

## Troubleshooting

### "No GPU detected"
- Make sure CUDA is installed: `nvidia-smi`
- Check PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`

### "poppler not found"
- Install poppler-utils: `sudo apt-get install poppler-utils`

### Low OCR accuracy
- Increase DPI: `--dpi 400` (but slower)
- Ensure the source PDF is not too blurry or low quality

## License

Free to use and modify for your needs.
