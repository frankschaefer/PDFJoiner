# PDF Joiner

A professional Python desktop application for batch processing and merging PDF files from multiple folders. Features a modern GUI built with CustomTkinter.

![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

### Batch Processing Mode (Default)
- **Intelligent Folder Processing**: Select and process multiple folders simultaneously with subfolder support
- **Smart Date Extraction**: Automatically extracts dates from PDF filenames
- **Automatic Sorting**: Orders PDFs by date (newest first) before merging
- **Advanced Image Compression**: Real JPEG compression with 4 quality presets (40-80% file size reduction)
- **OCR Integration**: Add searchable text layer to scanned PDFs for LLM access
- **Safe File Management**: Verifies merge success before deleting source files
- **Real-time Progress Tracking**: Visual progress bar with time estimates and file size reduction display
- **Process Control**: Start, Pause/Resume, and Stop functionality
- **Professional Output Naming**: `<folder_name>_<YYYY-MM-DD>_<HH-MM-SS>.pdf`

### Simple Mode
- Manual selection and merging of individual PDF files
- Drag and drop interface
- Reorder files before merging

### User Interface
- Modern, professional GUI built with CustomTkinter
- Folder browser with checkbox selection
- Detailed processing log
- Elapsed and estimated time display
- Version information and status bar

## Quick Start

### Easy Launch (Recommended)

**Windows:**
```cmd
start.bat
```

**macOS/Linux:**
```bash
./start.sh
```

The startup scripts will automatically:
- Check and activate virtual environment
- Install missing dependencies
- Launch the application

### Manual Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Batch Mode (Default)
```bash
python main.py
```

1. Click "📁 Select Start Folder" to choose your base directory
2. Select folders you want to process using checkboxes
3. Click "▶ Start Processing"
4. Monitor progress in real-time
5. Merged PDFs will be created in each folder, source files deleted upon success

### Simple Mode
```bash
python main.py --simple
```

## How It Works

### Batch Processing Workflow

1. **Folder Selection**: Choose a base directory containing multiple folders
2. **For Each Selected Folder**:
   - Scans for all PDF files
   - Extracts dates from filenames (supports formats like `DD-MM-YYYY`, `YYYY-MM-DD`)
   - Sorts PDFs by date (newest first)
   - Merges into a single PDF with timestamp
   - Verifies file integrity
   - Deletes source files only if merge successful

### Date Extraction Examples
- `Invoice_13-11-2025.pdf` → Extracted: November 13, 2025
- `Report_2025-11-13.pdf` → Extracted: November 13, 2025
- `Document_13.11.2025.pdf` → Extracted: November 13, 2025

## Project Structure

```
PDF-Joiner/
├── main.py                      # Application entry point
├── start.bat                    # Windows launcher
├── start.sh                     # macOS/Linux launcher
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── CLAUDE.md                    # Development documentation
├── HELP.md                      # User help guide
├── ERROR_HANDLING.md            # Error documentation
├── OCR_INTEGRATION.md           # OCR integration guide
├── src/
│   └── pdf_joiner/
│       ├── __init__.py         # Version metadata
│       ├── batch_gui.py        # Batch processing UI with OCR controls
│       ├── batch_processor.py  # Batch processing logic with OCR
│       ├── date_extractor.py   # Date parsing utilities
│       ├── gui.py              # Simple mode UI
│       ├── pdf_merger.py       # Legacy PyPDF2 merging
│       ├── pikepdf_merger.py   # Advanced pikepdf merging with compression
│       └── ocr_processor.py    # OCR text layer integration
├── tests/
│   ├── __init__.py
│   ├── test_pdf_merger.py
│   ├── test_batch_processor.py
│   ├── test_multiple_folders.py
│   ├── test_quality_settings.py
│   └── test_pikepdf_compression.py
└── assets/                      # UI resources
```

## Development

### Running Tests
```bash
python -m pytest tests/

# With verbose output
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_pdf_merger.py
```

### Dependencies
- **customtkinter** - Modern UI framework
- **pikepdf** - Advanced PDF manipulation with real image compression
- **PyPDF2** - Legacy PDF support
- **pillow** - Image handling
- **python-dateutil** - Flexible date parsing
- **pytest** - Testing framework
- **reportlab** - PDF generation for tests
- **ocrmypdf** (optional) - OCR text layer integration

## Configuration

Default base path can be modified in `src/pdf_joiner/batch_gui.py`:
```python
self.base_path = "/your/default/path"
```

Or use the "📁 Select Start Folder" button to choose a different directory at runtime.

## Version History

### v1.3.0 (2026-01-06) - OCR Integration
- **OCR Integration for LLM Access**: Add searchable text layer to scanned PDFs
  - New OCRProcessor class wrapping OCRmyPDF functionality
  - GUI checkbox: "🔍 Add OCR text layer (macht PDFs durchsuchbar für LLMs)"
  - Language selection dropdown (German, English, French, Italian, Spanish, Portuguese, Dutch)
  - Optimal workflow: OCR individual files → Compress → Merge (avoids processing huge merged files)
  - Automatic skip of pages that already contain text (`--skip-text`)
  - Graceful degradation if OCRmyPDF not installed
- **Enhanced Error Handling**: Detailed error messages with automatic file skipping
  - Show full file path, size, and problem type for all errors
  - Automatic skipping of empty files (0 bytes) and tiny files (<100 bytes)
  - Specific error messages for corrupt PDFs, password-protected PDFs, damaged PDFs
  - Continue processing other files when individual files fail
  - Comprehensive ERROR_HANDLING.md documentation
- **Documentation**: Complete OCR_INTEGRATION.md guide with installation and usage

### v1.2.1 (2026-01-06) - Ultra Compression & Error Handling
- **Ultra-Low Quality Preset**: Aggressive downsampling option (50% JPEG, 100 DPI)
  - Achieves 70-90% file size reduction for image-heavy PDFs
  - Useful for large archives and internal documents
  - Added to quality dropdown with clear description
- **Enhanced Error Messages**: Improved error reporting in pikepdf_merger.py
  - Full file path shown in all error messages
  - Detailed error categorization (corrupt structure, password-protected, damaged)
  - File size information included in error reports
  - Helpful tips for fixing corrupt PDFs (Adobe/Preview repair, Ghostscript)
- **File Validation**: Pre-merge validation of all input files
  - Check for 0-byte files (skip automatically)
  - Check for files <100 bytes (likely corrupt, skip automatically)
  - Detailed skipped file summary at end of processing

### v1.2.0 (2026-01-06) - Real Image Compression
- **pikepdf Integration**: Migrated from PyPDF2 to pikepdf for real compression
  - Actual JPEG compression of images within PDFs
  - DPI downsampling (300/200/150/100 DPI based on quality)
  - RGB color space conversion for compatibility
  - Object stream compression for smaller file sizes
- **Quality Presets**: Professional compression settings
  - High (85% JPEG, 300 DPI): 20-40% reduction, best for archival
  - Medium (75% JPEG, 200 DPI): 40-60% reduction, balanced (default)
  - Low (60% JPEG, 150 DPI): 60-80% reduction, maximum compression
  - Original: No compression, preserves exact input quality
- **Compression Results**: Actual file size reduction (previously files were increasing)
  - Typical reduction: 40-60% for medium quality
  - Smart image handling: skips tiny images, converts transparency
- **Tests**: Comprehensive test suite for compression verification

### v1.1.0 (2026-01-06) - Multi-Folder & Compression
- **Recursive Subfolder Processing**: Process entire folder trees automatically
  - Uses os.walk() for deep folder traversal
  - Parent folder name included in output filename (ParentFolder_ChildFolder)
  - Maintains folder hierarchy in merged PDF naming
- **Multiple Folder Processing Fix**: All selected folders now process correctly
  - Fixed issue where only first folder was processed
  - Progress tracking across all selected folders
- **File Size Tracking**: Real-time file size reduction monitoring
  - New progress bar showing percentage reduction
  - Detailed size comparison: input vs output in MB/GB
  - Color-coded display (green for reduction, red for increase)
  - Total size tracking across all folders
- **Enhanced Logging**: Detailed size reduction information per folder
  - Shows exact MB/GB reduction
  - Displays percentage reduction
  - Warning if files increase in size

### v1.0.7 (2026-01-06) - Progress & Error Fixes
- **Button State Management**: Fixed button states after processing errors
  - Stop button now properly deactivates after completion
  - Exit button properly activates after completion
  - Consistent state regardless of success/failure
- **Progress Throttling**: Smooth progress bar updates
  - Throttled to max 10 updates per second
  - Fixed jumping from 0 to final value instantly
  - Better visual feedback during processing
- **Error Handling**: Improved PyPDF2 error handling
  - Graceful handling of "Image data not rectangular"
  - Fixed "cannot write mode PA as PNG" errors
  - Handled "Illegal character in Name Object" warnings
  - Fixed "'NullObject' object has no attribute '_clone'" crashes
- **Stability**: More robust PDF processing with better error recovery

### v1.0.6 (2026-01-05)
- Added comprehensive Help documentation (HELP.md)
- New Help button in UI header with green styling
- Modal help window displays full user guide
- Professional help content covering all features and workflows
- Troubleshooting section with common issues and solutions
- Tips and best practices for optimal usage
- Keyboard shortcuts reference
- System requirements and dependencies

### v1.0.5 (2026-01-05)
- Changed default for "Remove source files" checkbox to OFF for safer operation
- Automatic detection and skipping of previously joined PDF files
- Pattern matching identifies joined PDFs by `_YYYY-MM-DD_HH-MM-SS.pdf` suffix
- Prevents re-processing of already merged files in subsequent runs
- Enhanced logging shows count of skipped joined PDFs per folder
- Improved safety: preserves source files by default unless explicitly enabled

### v1.0.4 (2026-01-05)
- Added configurable image quality/compression settings
- New quality dropdown with 4 presets: High, Medium, Low, Original
- Intelligent image compression reduces PDF file sizes significantly
- Medium quality (75% JPEG, 80% scale) now default for balanced output
- Low quality option (50% JPEG, 60% scale) for maximum size reduction
- High quality option (95% JPEG, 100% scale) preserves near-original quality
- Original option disables compression entirely
- Quality setting is disabled during processing for safety
- Enhanced logging shows selected quality level during processing

### v1.0.3 (2026-01-05)
- Enhanced progress bar with file-level tracking for improved visibility
- Added file counting phase before processing with real-time updates
- Implemented high-frequency progress updates during PDF merging
- Progress bar now updates based on individual files rather than folders
- Increased time estimation update frequency to ~2 times per second (500ms intervals)
- Improved user feedback with detailed file processing counts
- Better progress visibility for folders with many PDFs

### v1.0.2 (2026-01-05)
- Added configurable source file deletion option
- New checkbox: "Remove source files after successful merge (recommended)"
- Users can now choose to preserve original PDFs after merging
- Enhanced logging shows deletion status during processing
- Added comprehensive unit tests for batch processing functionality
- Improved file deletion safety and control

### v1.0.1 (2026-01-05)
- Added professional "Exit Application" button with confirmation dialogs
- Implemented comprehensive button state management system
- Browse folder button now properly disabled during processing
- Quit button disabled during active processing for safety
- Improved window close behavior with consistent quit handling
- Enhanced user experience with state-aware button controls

### v1.0.0 (2026-01-05)
- Initial release
- Batch folder processing
- Smart date extraction and sorting
- Real-time progress tracking
- Safe file deletion
- Process control (Start/Pause/Stop)

## License

MIT License - See LICENSE file for details

## Author

Frank Schäfer

## Support

For issues, questions, or contributions, please visit the GitHub repository.
