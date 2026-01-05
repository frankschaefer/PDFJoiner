# PDF Joiner

A professional Python desktop application for batch processing and merging PDF files from multiple folders. Features a modern GUI built with CustomTkinter.

![Version](https://img.shields.io/badge/version-1.0.6-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

### Batch Processing Mode (Default)
- **Intelligent Folder Processing**: Select and process multiple folders simultaneously
- **Smart Date Extraction**: Automatically extracts dates from PDF filenames
- **Automatic Sorting**: Orders PDFs by date (newest first) before merging
- **Safe File Management**: Verifies merge success before deleting source files
- **Real-time Progress Tracking**: Visual progress bar with time estimates
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
├── CLAUDE.md                    # Development documentation
├── src/
│   └── pdf_joiner/
│       ├── __init__.py         # Version metadata
│       ├── batch_gui.py        # Batch processing UI
│       ├── batch_processor.py  # Batch processing logic
│       ├── date_extractor.py   # Date parsing utilities
│       ├── gui.py              # Simple mode UI
│       └── pdf_merger.py       # Core PDF merging
├── tests/
│   ├── __init__.py
│   └── test_pdf_merger.py
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
- **PyPDF2** - PDF manipulation
- **pillow** - Image handling
- **python-dateutil** - Flexible date parsing
- **pytest** - Testing framework

## Configuration

Default base path can be modified in `src/pdf_joiner/batch_gui.py`:
```python
self.base_path = "/your/default/path"
```

Or use the "📁 Select Start Folder" button to choose a different directory at runtime.

## Version History

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
