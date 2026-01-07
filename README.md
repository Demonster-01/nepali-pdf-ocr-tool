# 🇳🇵 Nepali PDF OCR Tool (GPU Accelerated)

Stop struggling with garbled text from old Nepali PDFs! This tool converts PDFs using legacy fonts (like Preeti, Kantipur, etc.) into modern, searchable PDFs with proper copy-pasteable Devanagari Unicode.

🚀 **Optimized for speed:** Process a 120-page legal document in ~10 minutes using your GPU.

## ✨ Features

- ✅ **Fixed Copy-Paste**: Converts legacy font shapes into standard Unicode. No more `tyf Joj:yf`; you get `तथा व्यवस्था`.
- 🏎️ **GPU Acceleration**: Leverages NVIDIA CUDA (RTX 3050+) for ultra-fast processing via EasyOCR.
- 🧵 **Multithreaded**: Simultaneous PDF-to-image conversion to maximize CPU usage.
- ⚡ **Speed Modes**: Choose your balance between quality and performance.
- 🔍 **Searchable Output**: Generates an invisible text layer perfectly mapped to the visual document.
- 📦 **UV Powered**: Uses the lightning-fast `uv` package manager for dependency management.

## 🛠️ Requirements

### 1. System Dependencies
You need `poppler-utils` for PDF processing and `Noto Sans Devanagari` fonts for the text layer.

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils fonts-noto-core
```

### 2. Python Environment
This project uses [uv](https://github.com/astral-sh/uv).

```bash
# Install dependencies and setup environment
uv sync
```

## 🌐 Web Dashboard

The `UI-api` branch includes a modern web interface for easier processing and visualization.

### How to Run
1. **Start the server**:
   ```bash
   uv run python app.py
   ```
2. **Open your browser**:
   Navigate to `http://localhost:8000`

### Features
- **Drag & Drop**: Easy PDF uploading.
- **Side-by-Side Comparison**: See the "Before" (garbled) vs "After" (Unicode) text.
- **Live Progress**: Visual tracking of the OCR engine.

## 🚀 CLI Usage
| Mode | DPI | Description |
| :--- | :--- | :--- |
| `--mode fast` | 150 | Highest speed, good for clear documents. |
| `--mode balanced` | 200 | (Default) Best balance for most PDFs. |
| `--mode accurate` | 300 | Best for blurry or small-font documents. |

### Advanced Examples
```bash
# Process only the first 5 pages for testing
uv run pdf_ocr.py input.pdf output.pdf --max-pages 5

# Force CPU (if you don't have an NVIDIA GPU)
uv run pdf_ocr.py input.pdf output.pdf --no-gpu
```

## 📖 How it Works
1.  **Image Conversion**: The PDF is split into images using multiple CPU threads.
2.  **AI OCR**: EasyOCR looks at the visual shapes of the characters (ignoring the broken internal font data).
3.  **Unicode Mapping**: The detected shapes are mapped to standard Devanagari Unicode.
4.  **Invisible Layer**: A new PDF is generated using the original images with a hidden, perfectly aligned Unicode text layer.

## 🤝 Contributing
Feel free to open issues or submit pull requests to improve accuracy or speed!

## 📜 License
MIT
