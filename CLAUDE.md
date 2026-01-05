# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF-Joiner is a Python desktop application for batch processing and merging PDF files from multiple folders. It features a modern GUI built with CustomTkinter and uses PyPDF2 for PDF manipulation.

The application operates in two modes:
- **Batch Mode** (default): Process multiple folders, merge PDFs within each folder, and clean up source files
- **Simple Mode**: Manual selection and merging of individual PDF files

## Architecture

The application has a modular structure with separate components for batch processing and simple merging:

### Core Modules

- **`main.py`** - Entry point with mode selection (batch or simple)
- **`src/pdf_joiner/`** - Main application package
  - `batch_gui.py` - Batch processing UI (`BatchPDFJoinerApp` class)
  - `batch_processor.py` - Batch processing logic (`BatchProcessor` class)
  - `date_extractor.py` - Date parsing from filenames (`DateExtractor` class)
  - `gui.py` - Simple merger UI (`PDFJoinerApp` class)
  - `pdf_merger.py` - Core PDF merging (`PDFMerger` class)
  - `__init__.py` - Version and metadata
- **`tests/`** - Unit tests using pytest
- **`assets/`** - UI assets and resources

### Batch Processing Workflow

1. User selects folders from a base directory
2. For each folder:
   - Scans for PDF files
   - Extracts dates from filenames (format: `filename_DD-MM-YYYY.pdf`)
   - Sorts PDFs by date (newest first)
   - Merges into single PDF with naming: `<folder_name>_<YYYY-MM-DD>_<HH-MM-SS>.pdf`
   - Verifies output file integrity
   - Deletes source PDFs if merge successful
3. Shows real-time progress, elapsed time, and estimated completion time

### Key Features

- **Date Extraction**: Parses dates from filenames in formats like `13-11-2025`, `2025-11-13`, etc.
- **Smart Sorting**: Orders PDFs by extracted date (newest first) before merging
- **Progress Tracking**: Real-time progress bar with folder-level status
- **Time Estimation**: Shows elapsed time and estimates completion time
- **Process Control**: Start, Pause/Resume, and Stop buttons
- **Safe Deletion**: Only deletes source files after successful merge verification
- **Thread Safety**: Processing runs in background thread to keep UI responsive

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Batch mode (default)
python main.py

# Simple mode
python main.py --simple
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_pdf_merger.py
```

## Key Dependencies

- **customtkinter** - Modern UI framework (Tkinter wrapper)
- **PyPDF2** - PDF manipulation library
- **pillow** - Image handling (required by CustomTkinter)
- **python-dateutil** - Flexible date parsing from filenames
- **pytest** - Testing framework

## Configuration

Default base path is set in `batch_gui.py` line 23:
```python
self.base_path = "/Users/fs_mku/Desktop/January 5, 2026 08:38 PM"
```

To change the base directory, modify this value or add UI controls for path selection.
