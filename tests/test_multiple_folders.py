"""Tests for multiple folder processing."""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from src.pdf_joiner.batch_processor import BatchProcessor


def create_test_pdf(file_path: str, content: str = "Test PDF", num_pages: int = 1):
    """
    Create a simple test PDF file.

    Args:
        file_path: Path where PDF will be saved
        content: Text content to include
        num_pages: Number of pages to create
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(file_path, pagesize=letter)
    for i in range(num_pages):
        c.drawString(100, 750, f"{content} - Page {i+1}")
        c.showPage()
    c.save()


@pytest.fixture
def multi_folder_test_dir():
    """Create a test directory with multiple folders and PDFs."""
    test_dir = tempfile.mkdtemp()

    # Create folder structure:
    # test_dir/
    #   Folder1/
    #     file1_01-01-2025.pdf
    #     file2_02-01-2025.pdf
    #   Folder2/
    #     doc1_15-01-2025.pdf
    #     doc2_16-01-2025.pdf
    #     doc3_17-01-2025.pdf
    #   Folder3/
    #     report_20-01-2025.pdf

    folder1 = os.path.join(test_dir, "Folder1")
    folder2 = os.path.join(test_dir, "Folder2")
    folder3 = os.path.join(test_dir, "Folder3")

    os.makedirs(folder1)
    os.makedirs(folder2)
    os.makedirs(folder3)

    # Create test PDFs in Folder1
    create_test_pdf(os.path.join(folder1, "file1_01-01-2025.pdf"), "Folder1 Doc1")
    create_test_pdf(os.path.join(folder1, "file2_02-01-2025.pdf"), "Folder1 Doc2")

    # Create test PDFs in Folder2
    create_test_pdf(os.path.join(folder2, "doc1_15-01-2025.pdf"), "Folder2 Doc1")
    create_test_pdf(os.path.join(folder2, "doc2_16-01-2025.pdf"), "Folder2 Doc2")
    create_test_pdf(os.path.join(folder2, "doc3_17-01-2025.pdf"), "Folder2 Doc3")

    # Create test PDF in Folder3
    create_test_pdf(os.path.join(folder3, "report_20-01-2025.pdf"), "Folder3 Report")

    yield test_dir

    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_multiple_folders_processing(multi_folder_test_dir):
    """Test that multiple selected folders are all processed correctly."""
    processor = BatchProcessor()

    # Track log messages
    log_messages = []
    processor.set_log_callback(lambda msg: log_messages.append(msg))

    # Process all three folders
    selected_folders = ["Folder1", "Folder2", "Folder3"]
    processor.process_folders(
        selected_folders,
        multi_folder_test_dir,
        delete_source=False,  # Keep source files for verification
        quality="original"
    )

    # Verify all folders were processed
    folder1_path = os.path.join(multi_folder_test_dir, "Folder1")
    folder2_path = os.path.join(multi_folder_test_dir, "Folder2")
    folder3_path = os.path.join(multi_folder_test_dir, "Folder3")

    # Check that merged PDFs were created in each folder
    folder1_files = [f for f in os.listdir(folder1_path) if f.endswith('.pdf')]
    folder2_files = [f for f in os.listdir(folder2_path) if f.endswith('.pdf')]
    folder3_files = [f for f in os.listdir(folder3_path) if f.endswith('.pdf')]

    # Should have original files + 1 merged file in each folder
    assert len(folder1_files) == 3, f"Folder1 should have 3 PDFs (2 original + 1 merged), found {len(folder1_files)}"
    assert len(folder2_files) == 4, f"Folder2 should have 4 PDFs (3 original + 1 merged), found {len(folder2_files)}"
    assert len(folder3_files) == 2, f"Folder3 should have 2 PDFs (1 original + 1 merged), found {len(folder3_files)}"

    # Verify all folders mentioned in logs
    log_text = "\n".join(log_messages)
    assert "Folder1" in log_text, "Folder1 should be mentioned in logs"
    assert "Folder2" in log_text, "Folder2 should be mentioned in logs"
    assert "Folder3" in log_text, "Folder3 should be mentioned in logs"

    # Verify success messages for all folders
    assert log_text.count("Successfully merged") >= 3, "Should have success messages for all 3 folders"


def test_nested_folder_processing(multi_folder_test_dir):
    """Test processing of nested subfolders."""
    # Create nested structure
    parent_folder = os.path.join(multi_folder_test_dir, "ParentFolder")
    child_folder = os.path.join(parent_folder, "ChildFolder")
    os.makedirs(child_folder)

    # Create PDFs in nested folder
    create_test_pdf(os.path.join(child_folder, "nested1_10-01-2025.pdf"), "Nested Doc1")
    create_test_pdf(os.path.join(child_folder, "nested2_11-01-2025.pdf"), "Nested Doc2")

    processor = BatchProcessor()
    log_messages = []
    processor.set_log_callback(lambda msg: log_messages.append(msg))

    # Process parent folder (should include child folder PDFs)
    processor.process_folders(
        ["ParentFolder"],
        multi_folder_test_dir,
        delete_source=False,
        quality="original"
    )

    # Check that merged PDF was created in child folder
    child_files = [f for f in os.listdir(child_folder) if f.endswith('.pdf')]

    # Should have 2 original + 1 merged
    assert len(child_files) == 3, f"Child folder should have 3 PDFs, found {len(child_files)}"

    # Find the merged PDF (should contain parent folder name)
    merged_pdfs = [f for f in child_files if '_20' in f and len(f) > 30]  # Merged files have timestamps
    assert len(merged_pdfs) == 1, "Should have exactly one merged PDF"

    # Verify parent folder name is in the merged filename
    merged_filename = merged_pdfs[0]
    assert "ParentFolder" in merged_filename or "ChildFolder" in merged_filename, \
        f"Merged filename '{merged_filename}' should contain parent or child folder name"


def test_skip_previously_joined_pdfs(multi_folder_test_dir):
    """Test that previously joined PDFs are skipped in subsequent runs."""
    processor = BatchProcessor()

    # First run - process folder
    processor.process_folders(
        ["Folder1"],
        multi_folder_test_dir,
        delete_source=False,
        quality="original"
    )

    # Get the merged PDF from first run
    folder1_path = os.path.join(multi_folder_test_dir, "Folder1")
    first_run_files = sorted([f for f in os.listdir(folder1_path) if f.endswith('.pdf')])

    # Second run - should skip the previously joined PDF
    log_messages = []
    processor.set_log_callback(lambda msg: log_messages.append(msg))

    processor.process_folders(
        ["Folder1"],
        multi_folder_test_dir,
        delete_source=False,
        quality="original"
    )

    # Check logs for skip message
    log_text = "\n".join(log_messages)
    assert "Skipped" in log_text and "previously joined" in log_text, \
        "Should log that previously joined PDFs were skipped"

    # Verify file count
    second_run_files = sorted([f for f in os.listdir(folder1_path) if f.endswith('.pdf')])

    # Should have added one more merged PDF
    assert len(second_run_files) == len(first_run_files) + 1, \
        "Second run should create one additional merged PDF"


def test_file_size_tracking(multi_folder_test_dir):
    """Test that file sizes are tracked and reported correctly."""
    processor = BatchProcessor()
    log_messages = []
    processor.set_log_callback(lambda msg: log_messages.append(msg))

    # Process folders
    processor.process_folders(
        ["Folder1", "Folder2"],
        multi_folder_test_dir,
        delete_source=False,
        quality="medium"
    )

    # Check that size information is in logs
    log_text = "\n".join(log_messages)

    # Should have total size summary
    assert "Total input size:" in log_text, "Should report total input size"
    assert "Total output size:" in log_text, "Should report total output size"

    # Should report per-folder size changes
    assert any("reduced by" in msg or "increased by" in msg or "no size change" in msg.lower()
               for msg in log_messages), "Should report size changes per folder"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
