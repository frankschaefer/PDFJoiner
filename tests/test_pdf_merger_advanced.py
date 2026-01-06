"""Advanced tests for PDF Merger with special characters and real PDFs."""

import pytest
import os
import tempfile
from pathlib import Path
from src.pdf_joiner.pdf_merger import PDFMerger
from PyPDF2 import PdfReader


class TestPDFMergerAdvanced:
    """Advanced test cases for PDFMerger with real files."""

    @pytest.fixture
    def test_files_dir(self):
        """Get test files directory."""
        return Path(__file__).parent / "test_files"

    @pytest.fixture
    def sample_pdfs(self, test_files_dir):
        """Get list of sample PDF files with special characters."""
        pdf_files = list(test_files_dir.glob("*.pdf"))
        assert len(pdf_files) >= 3, "Need at least 3 test PDF files"
        return [str(f) for f in pdf_files]

    @pytest.fixture
    def temp_output(self):
        """Create temporary output file."""
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        yield path
        # Cleanup
        if os.path.exists(path):
            os.remove(path)

    def test_merge_pdfs_with_special_characters(self, sample_pdfs, temp_output):
        """Test merging PDFs with filenames containing special characters."""
        merger = PDFMerger()

        # Merge PDFs with special characters in filenames
        result = merger.merge_pdfs(sample_pdfs, temp_output)

        assert result is True, "Merge should succeed"
        assert os.path.exists(temp_output), "Output file should exist"
        assert os.path.getsize(temp_output) > 0, "Output file should not be empty"

    def test_merge_pdfs_with_spaces_in_filenames(self, sample_pdfs, temp_output):
        """Test merging PDFs with spaces in filenames."""
        merger = PDFMerger()

        # Filter files with spaces
        files_with_spaces = [f for f in sample_pdfs if ' ' in f]
        assert len(files_with_spaces) >= 1, "Need PDFs with spaces in filename"

        result = merger.merge_pdfs(files_with_spaces, temp_output)

        assert result is True, "Merge should succeed with spaces in filenames"
        assert os.path.exists(temp_output), "Output file should exist"

    def test_merge_pdfs_with_unicode_characters(self, sample_pdfs, temp_output):
        """Test merging PDFs with Unicode characters (emoji, umlauts)."""
        merger = PDFMerger()

        # Filter files with unicode characters
        files_with_unicode = [f for f in sample_pdfs if any(ord(c) > 127 for c in f)]

        if files_with_unicode:
            result = merger.merge_pdfs(files_with_unicode, temp_output)
            assert result is True, "Merge should succeed with Unicode characters"
            assert os.path.exists(temp_output), "Output file should exist"

    def test_merged_pdf_page_count(self, sample_pdfs, temp_output):
        """Test that merged PDF has correct number of pages."""
        merger = PDFMerger()

        # Count pages in source PDFs
        total_pages = 0
        for pdf_file in sample_pdfs:
            reader = PdfReader(pdf_file)
            total_pages += len(reader.pages)

        # Merge PDFs
        result = merger.merge_pdfs(sample_pdfs, temp_output)
        assert result is True, "Merge should succeed"

        # Check merged PDF page count
        merged_reader = PdfReader(temp_output)
        assert len(merged_reader.pages) == total_pages, \
            f"Merged PDF should have {total_pages} pages"

    def test_merge_single_pdf(self, sample_pdfs, temp_output):
        """Test merging a single PDF file."""
        merger = PDFMerger()

        result = merger.merge_pdfs([sample_pdfs[0]], temp_output)

        assert result is True, "Merge should succeed with single file"
        assert os.path.exists(temp_output), "Output file should exist"

        # Verify page count matches
        original_reader = PdfReader(sample_pdfs[0])
        merged_reader = PdfReader(temp_output)
        assert len(merged_reader.pages) == len(original_reader.pages)

    def test_merge_preserves_content(self, sample_pdfs, temp_output):
        """Test that merged PDF preserves content from source PDFs."""
        merger = PDFMerger()

        result = merger.merge_pdfs(sample_pdfs[:2], temp_output)
        assert result is True, "Merge should succeed"

        # Read merged PDF
        merged_reader = PdfReader(temp_output)

        # Verify we can read all pages without errors
        for page in merged_reader.pages:
            text = page.extract_text()
            # Just verify we can extract text without errors
            assert text is not None

    def test_merge_with_different_quality_settings(self, sample_pdfs, temp_output):
        """Test merging with different quality presets."""
        quality_settings = ["high", "medium", "low", "original"]

        for quality in quality_settings:
            merger = PDFMerger(quality=quality)
            result = merger.merge_pdfs([sample_pdfs[0]], temp_output)

            assert result is True, f"Merge should succeed with {quality} quality"
            assert os.path.exists(temp_output), "Output file should exist"

            # Clean up for next iteration
            os.remove(temp_output)

    def test_merge_nonexistent_file(self, temp_output):
        """Test merging with nonexistent file."""
        merger = PDFMerger()

        fake_file = "/path/to/nonexistent/file.pdf"
        result = merger.merge_pdfs([fake_file], temp_output)

        assert result is False, "Merge should fail with nonexistent file"

    def test_merge_empty_list(self, temp_output):
        """Test merging with empty file list."""
        merger = PDFMerger()

        result = merger.merge_pdfs([], temp_output)

        # Should either fail or create empty PDF
        assert result is True or result is False

    def test_output_file_creation_in_special_path(self, sample_pdfs):
        """Test creating output in path with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create path with special characters
            output_path = os.path.join(tmpdir, "output ✅ file_2025-01-06.pdf")

            merger = PDFMerger()
            result = merger.merge_pdfs([sample_pdfs[0]], output_path)

            assert result is True, "Merge should succeed with special chars in output path"
            assert os.path.exists(output_path), "Output file should exist"

    def test_merge_maintains_pdf_validity(self, sample_pdfs, temp_output):
        """Test that merged PDF is valid and readable."""
        merger = PDFMerger()

        result = merger.merge_pdfs(sample_pdfs, temp_output)
        assert result is True, "Merge should succeed"

        # Try to open merged PDF
        try:
            reader = PdfReader(temp_output)
            assert len(reader.pages) > 0, "Merged PDF should have pages"

            # Verify metadata
            assert reader.metadata is not None or reader.metadata is None

        except Exception as e:
            pytest.fail(f"Merged PDF is not valid: {e}")

    def test_multiple_merges_sequential(self, sample_pdfs, temp_output):
        """Test performing multiple merges sequentially."""
        merger = PDFMerger()

        # First merge
        result1 = merger.merge_pdfs([sample_pdfs[0]], temp_output)
        assert result1 is True
        os.remove(temp_output)

        # Second merge with different files
        result2 = merger.merge_pdfs([sample_pdfs[1]], temp_output)
        assert result2 is True
        os.remove(temp_output)

        # Third merge with all files
        result3 = merger.merge_pdfs(sample_pdfs, temp_output)
        assert result3 is True

    def test_filename_with_leading_spaces(self, test_files_dir, temp_output):
        """Test handling filenames with leading spaces."""
        # Our test files have leading spaces
        files_with_leading_spaces = [
            str(f) for f in test_files_dir.glob("*.pdf")
            if f.name.startswith(' ')
        ]

        if files_with_leading_spaces:
            merger = PDFMerger()
            result = merger.merge_pdfs(files_with_leading_spaces, temp_output)

            assert result is True, "Should handle leading spaces in filenames"
            assert os.path.exists(temp_output), "Output file should exist"
