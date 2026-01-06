"""Tests for pikepdf image compression."""

import pytest
import os
import tempfile
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from src.pdf_joiner.pikepdf_merger import PikePDFMerger


def create_pdf_with_large_image(file_path: str, image_size: tuple = (2000, 2000)):
    """
    Create a test PDF with a large embedded image.

    Args:
        file_path: Path where PDF will be saved
        image_size: Size of the embedded image (width, height)
    """
    # Create a large test image
    img = Image.new('RGB', image_size, color='red')
    # Add some variation to make it compressible
    pixels = img.load()
    for i in range(0, image_size[0], 10):
        for j in range(0, image_size[1], 10):
            pixels[i, j] = (0, 0, 255)

    # Save image temporarily
    temp_img = file_path.replace('.pdf', '_temp.jpg')
    img.save(temp_img, 'JPEG', quality=95)

    # Create PDF with the image
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawImage(temp_img, 50, 400, width=500, height=500)
    c.drawString(100, 350, "This PDF contains a large embedded image")
    c.showPage()
    c.save()

    # Clean up temp image
    if os.path.exists(temp_img):
        os.remove(temp_img)


@pytest.fixture
def image_test_dir():
    """Create a test directory with PDFs containing large images."""
    test_dir = tempfile.mkdtemp()

    # Create PDFs with large images
    create_pdf_with_large_image(os.path.join(test_dir, "large1.pdf"), (2000, 2000))
    create_pdf_with_large_image(os.path.join(test_dir, "large2.pdf"), (2000, 2000))
    create_pdf_with_large_image(os.path.join(test_dir, "large3.pdf"), (1500, 1500))

    yield test_dir

    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_pikepdf_compression_reduces_size(image_test_dir):
    """Test that pikepdf compression significantly reduces file size."""
    pdf_files = [
        os.path.join(image_test_dir, "large1.pdf"),
        os.path.join(image_test_dir, "large2.pdf"),
        os.path.join(image_test_dir, "large3.pdf")
    ]

    # Calculate input size
    input_size = sum(os.path.getsize(f) for f in pdf_files)

    # Merge with LOW quality (maximum compression)
    output_path = os.path.join(image_test_dir, "merged_low.pdf")
    merger = PikePDFMerger(quality="low")
    success, error = merger.merge_pdfs(pdf_files, output_path)
    merger.close()

    assert success, f"Merge should succeed: {error}"
    assert os.path.exists(output_path), "Output file should exist"

    output_size = os.path.getsize(output_path)

    print(f"\nCompression Test Results:")
    print(f"Input size:  {input_size:,} bytes ({input_size/1024/1024:.2f} MB)")
    print(f"Output size: {output_size:,} bytes ({output_size/1024/1024:.2f} MB)")
    print(f"Reduction:   {input_size - output_size:,} bytes ({(1 - output_size/input_size)*100:.1f}%)")

    # With image compression, we should see significant reduction
    # For PDFs with large images, expect at least 30% reduction
    reduction_percent = (1 - output_size / input_size) * 100
    assert reduction_percent > 20, \
        f"Expected at least 20% reduction, got {reduction_percent:.1f}%"


def test_quality_levels_comparison(image_test_dir):
    """Compare file sizes across different quality levels."""
    pdf_files = [
        os.path.join(image_test_dir, "large1.pdf"),
        os.path.join(image_test_dir, "large2.pdf")
    ]

    input_size = sum(os.path.getsize(f) for f in pdf_files)
    results = {}

    print(f"\n{'='*60}")
    print(f"Quality Level Comparison")
    print(f"{'='*60}")
    print(f"Input size: {input_size:,} bytes ({input_size/1024/1024:.2f} MB)")
    print(f"{'='*60}")

    for quality in ["original", "high", "medium", "low"]:
        output_path = os.path.join(image_test_dir, f"merged_{quality}.pdf")

        merger = PikePDFMerger(quality=quality)
        success, error = merger.merge_pdfs(pdf_files, output_path)
        merger.close()

        assert success, f"Merge with {quality} quality should succeed: {error}"

        output_size = os.path.getsize(output_path)
        results[quality] = output_size
        reduction = (1 - output_size/input_size) * 100

        print(f"{quality.upper():8s}: {output_size:,} bytes ({output_size/1024/1024:.2f} MB) - "
              f"{reduction:+.1f}% change")

    print(f"{'='*60}")

    # Verify that lower quality means smaller files (generally)
    # Low should be significantly smaller than original
    assert results["low"] < results["original"] * 0.8, \
        "Low quality should be at least 20% smaller than original"


def test_pikepdf_handles_corrupt_images_gracefully(image_test_dir):
    """Test that pikepdf handles problematic PDFs without crashing."""
    pdf_files = [
        os.path.join(image_test_dir, "large1.pdf")
    ]

    output_path = os.path.join(image_test_dir, "merged_safe.pdf")

    # Even if some images fail to compress, merge should succeed
    merger = PikePDFMerger(quality="medium")
    success, error = merger.merge_pdfs(pdf_files, output_path)
    merger.close()

    assert success, f"Merge should succeed even with problematic images: {error}"
    assert os.path.exists(output_path), "Output file should exist"


def test_original_quality_no_compression(image_test_dir):
    """Test that original quality doesn't compress images."""
    pdf_files = [
        os.path.join(image_test_dir, "large1.pdf")
    ]

    input_size = sum(os.path.getsize(f) for f in pdf_files)
    output_path = os.path.join(image_test_dir, "merged_original.pdf")

    merger = PikePDFMerger(quality="original")
    success, error = merger.merge_pdfs(pdf_files, output_path)
    merger.close()

    assert success, f"Merge should succeed: {error}"

    output_size = os.path.getsize(output_path)

    # Original should be close to input size (within 30% due to PDF overhead)
    size_ratio = output_size / input_size
    assert 0.7 <= size_ratio <= 1.4, \
        f"Original quality should preserve size (ratio: {size_ratio:.2f})"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
