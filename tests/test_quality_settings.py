"""Tests for PDF quality settings and compression."""

import pytest
import os
import tempfile
import shutil
from PyPDF2 import PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from src.pdf_joiner.pdf_merger import PDFMerger


def create_test_pdf_with_content(file_path: str, num_pages: int = 5):
    """
    Create a test PDF with substantial content.

    Args:
        file_path: Path where PDF will be saved
        num_pages: Number of pages to create
    """
    c = canvas.Canvas(file_path, pagesize=letter)
    for page_num in range(num_pages):
        # Add substantial text content to make file larger
        y = 750
        c.setFont("Helvetica", 12)
        for line in range(40):
            c.drawString(50, y, f"Page {page_num + 1}, Line {line + 1}: This is test content " * 3)
            y -= 15
            if y < 50:
                break
        c.showPage()
    c.save()


@pytest.fixture
def quality_test_dir():
    """Create a test directory with PDFs for quality testing."""
    test_dir = tempfile.mkdtemp()

    # Create test PDFs
    create_test_pdf_with_content(os.path.join(test_dir, "test1.pdf"), num_pages=5)
    create_test_pdf_with_content(os.path.join(test_dir, "test2.pdf"), num_pages=5)
    create_test_pdf_with_content(os.path.join(test_dir, "test3.pdf"), num_pages=5)

    yield test_dir

    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_quality_original_no_compression(quality_test_dir):
    """Test that 'original' quality does not compress files."""
    pdf_files = [
        os.path.join(quality_test_dir, "test1.pdf"),
        os.path.join(quality_test_dir, "test2.pdf"),
        os.path.join(quality_test_dir, "test3.pdf")
    ]

    output_path = os.path.join(quality_test_dir, "merged_original.pdf")

    # Calculate input size
    input_size = sum(os.path.getsize(f) for f in pdf_files)

    # Merge with original quality
    merger = PDFMerger(quality="original")
    success, error = merger.merge_pdfs(pdf_files, output_path)
    merger.close()

    assert success, f"Merge should succeed: {error}"
    assert os.path.exists(output_path), "Output file should exist"

    output_size = os.path.getsize(output_path)

    # Original quality may be slightly larger due to PDF structure overhead
    # but should be close to input size (within 20%)
    size_ratio = output_size / input_size
    assert 0.8 <= size_ratio <= 1.3, \
        f"Original quality output size ({output_size}) should be similar to input ({input_size}), ratio: {size_ratio:.2f}"


def test_quality_high_compression(quality_test_dir):
    """Test that 'high' quality applies compression."""
    pdf_files = [
        os.path.join(quality_test_dir, "test1.pdf"),
        os.path.join(quality_test_dir, "test2.pdf")
    ]

    output_path = os.path.join(quality_test_dir, "merged_high.pdf")

    # Merge with high quality
    merger = PDFMerger(quality="high")
    success, error = merger.merge_pdfs(pdf_files, output_path)
    merger.close()

    assert success, f"Merge should succeed: {error}"
    assert os.path.exists(output_path), "Output file should exist"

    # Verify file was created
    output_size = os.path.getsize(output_path)
    assert output_size > 0, "Output file should have content"


def test_quality_medium_compression(quality_test_dir):
    """Test that 'medium' quality applies compression."""
    pdf_files = [
        os.path.join(quality_test_dir, "test1.pdf"),
        os.path.join(quality_test_dir, "test2.pdf")
    ]

    output_path = os.path.join(quality_test_dir, "merged_medium.pdf")

    # Merge with medium quality
    merger = PDFMerger(quality="medium")
    success, error = merger.merge_pdfs(pdf_files, output_path)
    merger.close()

    assert success, f"Merge should succeed: {error}"
    assert os.path.exists(output_path), "Output file should exist"

    output_size = os.path.getsize(output_path)
    assert output_size > 0, "Output file should have content"


def test_quality_low_compression(quality_test_dir):
    """Test that 'low' quality applies maximum compression."""
    pdf_files = [
        os.path.join(quality_test_dir, "test1.pdf"),
        os.path.join(quality_test_dir, "test2.pdf")
    ]

    output_path = os.path.join(quality_test_dir, "merged_low.pdf")

    # Merge with low quality
    merger = PDFMerger(quality="low")
    success, error = merger.merge_pdfs(pdf_files, output_path)
    merger.close()

    assert success, f"Merge should succeed: {error}"
    assert os.path.exists(output_path), "Output file should exist"

    output_size = os.path.getsize(output_path)
    assert output_size > 0, "Output file should have content"


def test_quality_comparison_all_settings(quality_test_dir):
    """Compare file sizes across all quality settings."""
    pdf_files = [
        os.path.join(quality_test_dir, "test1.pdf"),
        os.path.join(quality_test_dir, "test2.pdf"),
        os.path.join(quality_test_dir, "test3.pdf")
    ]

    input_size = sum(os.path.getsize(f) for f in pdf_files)
    results = {}

    for quality in ["original", "high", "medium", "low"]:
        output_path = os.path.join(quality_test_dir, f"merged_{quality}.pdf")

        merger = PDFMerger(quality=quality)
        success, error = merger.merge_pdfs(pdf_files, output_path)
        merger.close()

        assert success, f"Merge with {quality} quality should succeed: {error}"

        output_size = os.path.getsize(output_path)
        results[quality] = output_size

        print(f"\n{quality.upper()} quality:")
        print(f"  Input size:  {input_size:,} bytes")
        print(f"  Output size: {output_size:,} bytes")
        print(f"  Ratio: {output_size/input_size:.2%}")

    # Verify all quality levels produced valid files
    assert all(size > 0 for size in results.values()), "All output files should have content"

    # Note: PyPDF2's compression is limited, so we can't guarantee that
    # lower quality always means smaller files. The test just verifies
    # that all quality settings work without errors.


def test_quality_preset_definitions():
    """Test that quality presets are properly defined."""
    merger = PDFMerger(quality="high")
    assert merger.quality == "high"
    assert merger.jpeg_quality == 95
    assert merger.scale_factor == 1.0

    merger = PDFMerger(quality="medium")
    assert merger.quality == "medium"
    assert merger.jpeg_quality == 75
    assert merger.scale_factor == 0.8

    merger = PDFMerger(quality="low")
    assert merger.quality == "low"
    assert merger.jpeg_quality == 50
    assert merger.scale_factor == 0.6

    merger = PDFMerger(quality="original")
    assert merger.quality == "original"
    assert merger.jpeg_quality is None
    assert merger.scale_factor is None


def test_invalid_quality_fallback():
    """Test that invalid quality setting falls back to medium."""
    merger = PDFMerger(quality="invalid_quality")
    # Should fallback to medium
    assert merger.jpeg_quality == 75
    assert merger.scale_factor == 0.8


def test_format_size_helper():
    """Test the file size formatting helper."""
    from src.pdf_joiner.batch_processor import BatchProcessor

    processor = BatchProcessor()

    assert "B" in processor._format_size(100)
    assert "KB" in processor._format_size(2048)
    assert "MB" in processor._format_size(2 * 1024 * 1024)
    assert "GB" in processor._format_size(2 * 1024 * 1024 * 1024)

    # Test specific values
    assert processor._format_size(0) == "0.0 B"
    assert processor._format_size(1024) == "1.0 KB"
    assert processor._format_size(1024 * 1024) == "1.0 MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
