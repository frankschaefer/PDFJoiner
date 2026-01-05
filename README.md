# PDF Joiner

A professional Python desktop application for batch processing and merging PDF files from multiple folders. Features a modern GUI built with CustomTkinter.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
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

PDF Joiner Team

## Support

For issues, questions, or contributions, please visit the GitHub repository.
