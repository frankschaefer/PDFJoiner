"""Advanced PDF merging with image compression using pikepdf."""

import pikepdf
from pathlib import Path
from typing import List, Tuple
import io
from PIL import Image
import warnings


class PikePDFMerger:
    """Handles PDF file merging with advanced image compression using pikepdf."""

    # Quality presets: (jpeg_quality, max_dpi, description)
    QUALITY_PRESETS = {
        "high": (85, 300, "High Quality - good compression"),
        "medium": (75, 200, "Medium Quality - balanced"),
        "low": (60, 150, "Low Quality - maximum compression"),
        "ultra-low": (50, 100, "Ultra-Low Quality - aggressive compression"),
        "original": (None, None, "Original - no compression")
    }

    def __init__(self, quality: str = "medium"):
        """
        Initialize PikePDFMerger with quality setting.

        Args:
            quality: Quality preset - "high", "medium", "low", or "original"
        """
        self.quality = quality
        self.jpeg_quality, self.max_dpi, _ = self.QUALITY_PRESETS.get(
            quality, self.QUALITY_PRESETS["medium"]
        )

    def _compress_image_in_page(self, pdf: pikepdf.Pdf, page: pikepdf.Page) -> None:
        """
        Compress all images in a PDF page.

        Args:
            pdf: pikepdf.Pdf object
            page: Page to process
        """
        if self.jpeg_quality is None:
            return  # Original quality, no compression

        try:
            # Check if page has resources with images
            if '/Resources' not in page or '/XObject' not in page.Resources:
                return

            xobjects = page.Resources.XObject

            # Iterate over all XObjects
            for xobj_name in list(xobjects.keys()):
                try:
                    xobj = xobjects[xobj_name]

                    # Check if this is an image
                    if '/Subtype' not in xobj or xobj.Subtype != '/Image':
                        continue

                    # Convert to PdfImage and then PIL
                    pdf_image = pikepdf.PdfImage(xobj)
                    pil_image = pdf_image.as_pil_image()

                    # Skip if image is already small
                    if pil_image.width < 100 or pil_image.height < 100:
                        continue

                    # Calculate target dimensions based on DPI
                    if self.max_dpi:
                        # Assume original is 300 DPI, scale down if needed
                        scale = self.max_dpi / 300.0
                        if scale < 1.0:
                            new_width = max(int(pil_image.width * scale), 100)
                            new_height = max(int(pil_image.height * scale), 100)
                            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Convert to RGB if needed
                    if pil_image.mode in ('RGBA', 'LA', 'P', 'PA'):
                        background = Image.new('RGB', pil_image.size, (255, 255, 255))
                        if pil_image.mode in ('RGBA', 'LA', 'PA'):
                            try:
                                background.paste(pil_image, mask=pil_image.split()[-1])
                                pil_image = background
                            except Exception:
                                pil_image = pil_image.convert('RGB')
                        else:
                            pil_image = pil_image.convert('RGB')
                    elif pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')

                    # Compress to JPEG
                    compressed = io.BytesIO()
                    pil_image.save(compressed, format='JPEG', quality=self.jpeg_quality, optimize=True)
                    compressed.seek(0)
                    compressed_bytes = compressed.read()

                    # Create new image object with compressed data
                    new_image = pikepdf.Stream(pdf, compressed_bytes)
                    new_image.Type = pikepdf.Name.XObject
                    new_image.Subtype = pikepdf.Name.Image
                    new_image.Width = pil_image.width
                    new_image.Height = pil_image.height
                    new_image.ColorSpace = pikepdf.Name.DeviceRGB
                    new_image.BitsPerComponent = 8
                    new_image.Filter = pikepdf.Name.DCTDecode

                    # Replace the image in the page resources
                    xobjects[xobj_name] = new_image

                except Exception as e:
                    # Skip problematic images
                    continue

        except Exception as e:
            # If anything fails, just continue without compressing this page
            pass

    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> Tuple[bool, str]:
        """
        Merge multiple PDF files with image compression.

        Args:
            pdf_files: List of paths to PDF files to merge
            output_path: Path where the merged PDF will be saved

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            # Suppress warnings
            warnings.filterwarnings('ignore')

            # Validate and filter PDF files
            valid_files = []
            skipped_files = []

            for pdf_file in pdf_files:
                file_path = Path(pdf_file)

                # Check if file exists
                if not file_path.exists():
                    error_msg = f"Datei nicht gefunden: {file_path.name} (Pfad: {pdf_file})"
                    print(f"Error: {error_msg}")
                    skipped_files.append((file_path.name, "Datei existiert nicht"))
                    continue

                # Check if file size is 0
                file_size = file_path.stat().st_size
                if file_size == 0:
                    print(f"Skipping empty file: {file_path.name} (0 bytes)")
                    skipped_files.append((file_path.name, "Leere Datei (0 Bytes)"))
                    continue

                # Check if file is too small (less than 100 bytes - likely corrupt)
                if file_size < 100:
                    print(f"Skipping file (too small): {file_path.name} ({file_size} bytes)")
                    skipped_files.append((file_path.name, f"Datei zu klein ({file_size} Bytes)"))
                    continue

                valid_files.append(pdf_file)

            # If no valid files, return error
            if not valid_files:
                skip_summary = "\n".join([f"  - {name}: {reason}" for name, reason in skipped_files])
                error_msg = f"Keine gültigen PDFs gefunden.\nÜbersprungene Dateien:\n{skip_summary}"
                print(f"Error merging PDFs: {error_msg}")
                return False, error_msg

            # Create new PDF
            merged_pdf = pikepdf.Pdf.new()

            for pdf_file in valid_files:
                file_path = Path(pdf_file)

                try:
                    # Open source PDF
                    with pikepdf.Pdf.open(pdf_file, allow_overwriting_input=True) as src_pdf:
                        # Process each page
                        for page in src_pdf.pages:
                            # Compress images if not original quality
                            if self.quality != "original":
                                try:
                                    self._compress_image_in_page(src_pdf, page)
                                except Exception:
                                    # Continue even if compression fails
                                    pass

                            # Add page to merged PDF
                            merged_pdf.pages.append(page)

                except Exception as e:
                    error_type = type(e).__name__
                    error_details = str(e)[:100]

                    # Provide more helpful error messages based on error type
                    if "NullObject" in error_details or "AttributeError" in error_type:
                        error_msg = (f"Korrupte PDF-Struktur in '{file_path.name}'\n"
                                   f"  Pfad: {pdf_file}\n"
                                   f"  Größe: {file_path.stat().st_size:,} Bytes\n"
                                   f"  Problem: PDF enthält ungültige Objekte\n"
                                   f"  Tipp: Datei mit Adobe/Preview reparieren und neu speichern")
                    elif "password" in error_details.lower() or "encrypted" in error_details.lower():
                        error_msg = (f"Geschützte PDF: '{file_path.name}'\n"
                                   f"  Pfad: {pdf_file}\n"
                                   f"  Problem: PDF ist passwortgeschützt")
                    elif "EOF" in error_details or "xref" in error_details.lower():
                        error_msg = (f"Beschädigte PDF-Datei: '{file_path.name}'\n"
                                   f"  Pfad: {pdf_file}\n"
                                   f"  Größe: {file_path.stat().st_size:,} Bytes\n"
                                   f"  Problem: Datei ist unvollständig oder beschädigt")
                    else:
                        error_msg = (f"Fehler beim Lesen von '{file_path.name}'\n"
                                   f"  Pfad: {pdf_file}\n"
                                   f"  Größe: {file_path.stat().st_size:,} Bytes\n"
                                   f"  Fehler: {error_type} - {error_details}")

                    print(f"Error merging PDFs: {error_msg}")
                    skipped_files.append((file_path.name, f"{error_type}: {error_details[:50]}"))

                    # Continue with other files instead of failing completely
                    continue

            # Check if we have any pages
            if len(merged_pdf.pages) == 0:
                skip_summary = "\n".join([f"  - {name}: {reason}" for name, reason in skipped_files])
                error_msg = f"Keine PDFs konnten verarbeitet werden.\nProbleme:\n{skip_summary}"
                print(f"Error merging PDFs: {error_msg}")
                return False, error_msg

            # Save merged PDF
            merged_pdf.save(
                output_path,
                compress_streams=True if self.quality != "original" else False,
                object_stream_mode=pikepdf.ObjectStreamMode.generate if self.quality != "original" else pikepdf.ObjectStreamMode.disable
            )
            merged_pdf.close()

            # Return success with warning if some files were skipped
            if skipped_files:
                skip_summary = ", ".join([name for name, _ in skipped_files])
                warning_msg = f"Erfolgreich, aber {len(skipped_files)} Datei(en) übersprungen: {skip_summary}"
                return True, warning_msg

            return True, ""

        except Exception as e:
            error_msg = f"{str(e)[:100]}"
            print(f"Error merging PDFs: {error_msg}")
            return False, error_msg

    def close(self):
        """Clean up resources."""
        # pikepdf handles cleanup automatically
        pass
