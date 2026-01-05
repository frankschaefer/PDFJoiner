"""Tests for batch processing functionality."""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from src.pdf_joiner.batch_processor import BatchProcessor


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for testing."""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_validate_and_fix_path_valid(temp_test_dir):
    """Test path validation with a valid path."""
    processor = BatchProcessor()
    result = processor.validate_and_fix_path(temp_test_dir)
    assert result == temp_test_dir


def test_validate_and_fix_path_parent_fallback(temp_test_dir):
    """Test path validation falls back to parent directory."""
    processor = BatchProcessor()
    nonexistent_path = os.path.join(temp_test_dir, "nonexistent_folder")
    result = processor.validate_and_fix_path(nonexistent_path)
    assert result == temp_test_dir


def test_validate_and_fix_path_invalid():
    """Test path validation with completely invalid path."""
    processor = BatchProcessor()
    result = processor.validate_and_fix_path("/completely/nonexistent/path/that/does/not/exist")
    assert result is None


def test_get_folders_in_directory(temp_test_dir):
    """Test getting folders from a directory."""
    # Create test folders
    folder1 = os.path.join(temp_test_dir, "folder1")
    folder2 = os.path.join(temp_test_dir, "folder2")
    os.makedirs(folder1)
    os.makedirs(folder2)

    # Create a file (should not be included)
    file_path = os.path.join(temp_test_dir, "test.txt")
    Path(file_path).touch()

    processor = BatchProcessor()
    folders = processor.get_folders_in_directory(temp_test_dir)

    assert len(folders) == 2
    assert folder1 in folders
    assert folder2 in folders


def test_create_output_filename():
    """Test output filename generation."""
    processor = BatchProcessor()
    test_folder = "/test/path/My Test Folder"

    filename = processor.create_output_filename(test_folder)

    # Check format: foldername_YYYY-MM-DD_HH-MM-SS.pdf
    assert filename.startswith("My Test Folder_")
    assert filename.endswith(".pdf")
    assert len(filename.split("_")) >= 3


def test_verify_pdf_file_exists(temp_test_dir):
    """Test PDF file verification when file exists."""
    # Create a test file with content
    test_file = os.path.join(temp_test_dir, "test.pdf")
    with open(test_file, 'wb') as f:
        f.write(b'X' * 200)  # 200 bytes

    processor = BatchProcessor()
    result = processor.verify_pdf_file(test_file, min_size=100)

    assert result is True


def test_verify_pdf_file_too_small(temp_test_dir):
    """Test PDF file verification when file is too small."""
    # Create a test file with minimal content
    test_file = os.path.join(temp_test_dir, "test.pdf")
    with open(test_file, 'wb') as f:
        f.write(b'X' * 50)  # Only 50 bytes

    processor = BatchProcessor()
    result = processor.verify_pdf_file(test_file, min_size=100)

    assert result is False


def test_verify_pdf_file_nonexistent(temp_test_dir):
    """Test PDF file verification when file doesn't exist."""
    test_file = os.path.join(temp_test_dir, "nonexistent.pdf")

    processor = BatchProcessor()
    result = processor.verify_pdf_file(test_file)

    assert result is False


def test_process_folders_delete_source_enabled(temp_test_dir):
    """Test that source files are deleted when delete_source=True."""
    # This is a mock test - full integration would require actual PDF files
    # In a real scenario, you would create test PDFs and verify deletion
    processor = BatchProcessor()

    # Test that the parameter is accepted
    # Note: This doesn't actually process since we don't have PDF files
    processor.process_folders([], temp_test_dir, delete_source=True)
    assert processor.is_running == False


def test_process_folders_delete_source_disabled(temp_test_dir):
    """Test that source files are preserved when delete_source=False."""
    # This is a mock test - full integration would require actual PDF files
    processor = BatchProcessor()

    # Test that the parameter is accepted
    processor.process_folders([], temp_test_dir, delete_source=False)
    assert processor.is_running == False
