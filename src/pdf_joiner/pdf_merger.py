"""PDF merging functionality."""

from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from typing import List
import io
from PIL import Image


class PDFMerger:
    """Handles PDF file merging operations."""

    # Quality presets: (jpeg_quality, scale_factor, description)
    QUALITY_PRESETS = {
        "high": (95, 1.0, "High Quality (larger file size)"),
        "medium": (75, 0.8, "Medium Quality (balanced)"),
        "low": (50, 0.6, "Low Quality (smaller file size)"),
        "original": (None, None, "Original (no compression)")
    }

    def __init__(self, quality: str = "medium"):
        """
        Initialize PDFMerger with quality setting.

        Args:
            quality: Quality preset - "high", "medium", "low", or "original"
        """
        self.quality = quality
        self.jpeg_quality, self.scale_factor, _ = self.QUALITY_PRESETS.get(
            quality, self.QUALITY_PRESETS["medium"]
        )

    def _compress_image(self, image_data: bytes, width: int, height: int) -> bytes:
        """
        Compress image data.

        Args:
            image_data: Original image bytes
            width: Image width
            height: Image height

        Returns:
            Compressed image bytes
        """
        if self.jpeg_quality is None:
            return image_data

        try:
            # Open image from bytes
            img = Image.open(io.BytesIO(image_data))

            # Verify image has valid dimensions
            if img.size[0] <= 0 or img.size[1] <= 0:
                return image_data

            # Convert problematic modes to RGB
            if img.mode in ('RGBA', 'LA', 'P', 'PA', 'L', '1'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))

                # Handle palette mode
                if img.mode == 'P':
                    img = img.convert('RGBA')
                # Handle grayscale with alpha
                elif img.mode == 'PA':
                    img = img.convert('RGBA')
                # Handle single channel modes
                elif img.mode in ('L', '1'):
                    img = img.convert('RGB')

                # Paste with transparency mask if applicable
                if img.mode in ('RGBA', 'LA'):
                    try:
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    except Exception:
                        # If masking fails, just convert directly
                        img = img.convert('RGB')
            elif img.mode != 'RGB':
                # Convert any other mode to RGB
                img = img.convert('RGB')

            # Resize if scale factor is set
            if self.scale_factor and self.scale_factor < 1.0:
                new_width = max(1, int(width * self.scale_factor))
                new_height = max(1, int(height * self.scale_factor))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Compress to JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=self.jpeg_quality, optimize=True)
            return output.getvalue()

        except Exception as e:
            # Silently return original data if compression fails
            return image_data

    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> bool:
        """
        Merge multiple PDF files into a single PDF with optional image compression.

        Args:
            pdf_files: List of paths to PDF files to merge
            output_path: Path where the merged PDF will be saved

        Returns:
            True if successful, False otherwise
        """
        try:
            writer = PdfWriter()

            for pdf_file in pdf_files:
                if not Path(pdf_file).exists():
                    raise FileNotFoundError(f"File not found: {pdf_file}")

                reader = PdfReader(pdf_file)

                # Add all pages from this PDF
                for page in reader.pages:
                    # Note: Image compression is disabled for now due to PyPDF2 compatibility issues
                    # The compression feature will be re-enabled in a future version with better
                    # PyPDF2 integration
                    writer.add_page(page)

            # Write the merged PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            return True

        except Exception as e:
            print(f"Error merging PDFs: {e}")
            return False

    def close(self):
        """Clean up resources."""
        # PdfWriter doesn't need explicit closing
        pass
