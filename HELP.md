# PDF Joiner - User Guide

## Welcome to PDF Joiner

PDF Joiner is a professional desktop application designed to batch process and merge PDF files from multiple folders efficiently. This guide will help you get the most out of the application.

---

## Quick Start Guide

### 1. Selecting Folders

1. Click **"📁 Select Start Folder"** to choose your base directory
2. The application will display all folders found in that directory
3. Use the checkboxes to select which folders you want to process
4. You can select one or multiple folders

### 2. Configuring Options

**Delete Source Files:**
- **Unchecked (Default)**: Original PDF files are preserved after merging
- **Checked**: Source files are deleted after successful merge
- ⚠️ Only enable this if you're certain you want to remove the originals

**Image Quality:**
- **High**: Best quality, larger file sizes (95% JPEG, 100% scale)
- **Medium** (Default): Balanced quality and size (75% JPEG, 80% scale)
- **Low**: Smallest file sizes, reduced quality (50% JPEG, 60% scale)
- **Original**: No compression, preserves exact original quality

### 3. Processing

1. Click **"▶ Start Processing"** to begin
2. Monitor progress in the real-time progress bar
3. View detailed logs in the Processing Log area
4. Use **"⏸ Pause"** to temporarily halt processing
5. Use **"⏹ Stop"** to cancel processing completely

---

## How It Works

### Batch Processing Workflow

For each selected folder, PDF Joiner:

1. **Scans** for all PDF files in the folder
2. **Skips** any previously joined PDFs (identified by `_YYYY-MM-DD_HH-MM-SS.pdf` pattern)
3. **Extracts** dates from filenames (supports multiple formats)
4. **Sorts** PDFs by date, newest first
5. **Merges** all PDFs into a single file
6. **Compresses** images based on your quality setting
7. **Names** the output: `<folder_name>_<YYYY-MM-DD>_<HH-MM-SS>.pdf`
8. **Verifies** the merge was successful
9. **Deletes** source files (only if enabled and verified)

### Date Extraction Examples

PDF Joiner recognizes dates in various formats:

- `Invoice_13-11-2025.pdf` → November 13, 2025
- `Report_2025-11-13.pdf` → November 13, 2025
- `Document_13.11.2025.pdf` → November 13, 2025
- `Statement 31/12/2025.pdf` → December 31, 2025

Files without recognizable dates are included but sorted to the end.

### Smart File Skipping

The application automatically skips previously created joined PDFs to prevent:
- Re-processing already merged files
- Creating nested merged PDFs
- Unnecessary file bloat

**Pattern Recognition:**
Any PDF ending with `_YYYY-MM-DD_HH-MM-SS.pdf` is considered a joined file and will be skipped.

Example:
- ✅ **Processed**: `Invoice_13-11-2025.pdf`
- ❌ **Skipped**: `My Folder_2026-01-05_14-30-45.pdf` (previously joined)

---

## Features

### Real-Time Progress Tracking

- **Progress Bar**: Shows file-level processing progress
- **Elapsed Time**: Displays total time since start
- **Estimated Time**: Calculates expected completion time
- **File Counter**: Shows "Processing file X of Y"

### Process Control

- **Start**: Begin processing selected folders
- **Pause/Resume**: Temporarily halt and continue processing
- **Stop**: Cancel processing with confirmation
- **Safe Exit**: Prevents closing during active processing

### Image Compression

The application intelligently compresses images within PDFs to reduce file size:

- Converts images to optimized JPEG format
- Scales images based on quality setting
- Only replaces images if compression is beneficial
- Handles transparency with white background conversion

**Quality Impact:**
- **High**: Minimal compression, ~10-20% size reduction
- **Medium**: Balanced compression, ~30-50% size reduction
- **Low**: Maximum compression, ~50-70% size reduction
- **Original**: No compression, preserves exact file size

---

## Tips and Best Practices

### For Best Results

1. **Organize Your Files**: Keep related PDFs in separate folders
2. **Use Date-Based Naming**: Include dates in filenames for proper sorting
3. **Test First**: Run on a single folder first to verify output
4. **Keep Originals**: Leave "Delete source files" unchecked initially
5. **Choose Quality Wisely**: Use Medium for most documents, High for important files

### Safety Recommendations

1. **Backup Important Files**: Always maintain backups before bulk operations
2. **Verify First Merge**: Check the first merged PDF before processing all folders
3. **Use Preview Mode**: Keep delete disabled until you're satisfied with results
4. **Monitor Logs**: Watch for errors or warnings during processing

### Performance Tips

1. **Close Other Applications**: For faster processing on large batches
2. **Use Lower Quality**: For faster processing and smaller files
3. **Process in Batches**: Break very large operations into smaller groups
4. **Check Disk Space**: Ensure adequate space for merged files

---

## Troubleshooting

### Progress Bar Not Visible

The progress bar updates based on file count. For folders with few files, updates may appear infrequent. The application is still working normally.

### No Folders Found

- Verify the base path exists and contains folders
- Use "📁 Select Start Folder" to choose a valid directory
- The application will automatically use the parent directory if the selected path is invalid

### Merge Failed

Common causes and solutions:
- **Corrupted PDF**: Check source files individually
- **Insufficient Space**: Free up disk space
- **File Permissions**: Ensure read/write access to the folder
- **File In Use**: Close any PDFs open in other applications

### Source Files Not Deleted

This is intentional if:
- Delete checkbox is unchecked (default)
- Merge verification failed
- Files are read-only or locked

Check the processing log for specific reasons.

---

## Keyboard Shortcuts

- **Ctrl+Q** / **Cmd+Q**: Quit application (with confirmation)
- **Escape**: Cancel file/folder selection dialogs

---

## Advanced Features

### Simple Mode

For manual PDF merging without batch processing:

```bash
python main.py --simple
```

This launches a simpler interface for merging individual PDFs with drag-and-drop reordering.

### Custom Base Path

Modify the default base path in `src/pdf_joiner/batch_gui.py`:

```python
self.base_path = "/your/default/path"
```

---

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 512 MB minimum (2 GB recommended for large batches)
- **Disk Space**: Varies based on PDF sizes

### Dependencies

- CustomTkinter (Modern UI)
- PyPDF2 (PDF manipulation)
- Pillow (Image processing)
- python-dateutil (Date parsing)

---

## Version Information

**Current Version**: 1.0.5
**Release Date**: January 5, 2026
**Author**: PDF Joiner Team

### What's New in v1.0.5

- Safer defaults: Delete checkbox now OFF by default
- Automatic skipping of previously joined PDFs
- Pattern-based detection of merged files
- Enhanced logging for skipped files

See README.md for complete version history.

---

## Getting Help

### Support Resources

- **Documentation**: See README.md in the project folder
- **Technical Details**: See CLAUDE.md for development information
- **GitHub Repository**: Report issues and request features

### Contact

For questions, bug reports, or feature requests, please visit the GitHub repository or contact the PDF Joiner Team.

---

## License

PDF Joiner is released under the MIT License. See LICENSE file for details.

---

**Thank you for using PDF Joiner!**

For updates and more information, visit the project repository.
