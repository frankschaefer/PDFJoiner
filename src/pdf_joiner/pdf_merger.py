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

            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize if scale factor is set
            if self.scale_factor and self.scale_factor < 1.0:
                new_width = int(width * self.scale_factor)
                new_height = int(height * self.scale_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Compress to JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=self.jpeg_quality, optimize=True)
            return output.getvalue()

        except Exception as e:
            print(f"Warning: Could not compress image: {e}")
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
                    # Compress images in page if quality setting is not "original"
                    if self.jpeg_quality is not None and hasattr(page, 'images'):
                        try:
                            for image in page.images:
                                # Get image data
                                image_data = image.data
                                if hasattr(image, 'width') and hasattr(image, 'height'):
                                    # Compress the image
                                    compressed_data = self._compress_image(
                                        image_data,
                                        image.width,
                                        image.height
                                    )
                                    # Replace image data
                                    if len(compressed_data) < len(image_data):
                                        image._data = compressed_data
                        except Exception as e:
                            # If compression fails, continue with original page
                            print(f"Warning: Could not compress images in page: {e}")

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
