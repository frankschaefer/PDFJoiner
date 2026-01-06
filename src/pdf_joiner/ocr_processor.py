"""OCR processing for PDF files using OCRmyPDF."""

import subprocess
import os
from pathlib import Path
from typing import Tuple, Optional, Callable
import shutil


class OCRProcessor:
    """Handles OCR processing of PDF files."""

    def __init__(self, language: str = "deu"):
        """
        Initialize OCR processor.

        Args:
            language: Tesseract language code (deu, eng, fra, etc.)
        """
        self.language = language
        self.log_callback: Optional[Callable] = None

    def set_log_callback(self, callback: Callable):
        """Set callback for log messages."""
        self.log_callback = callback

    def _log(self, message: str):
        """Log a message."""
        if self.log_callback:
            self.log_callback(message)

    def _get_ocrmypdf_path(self) -> Optional[str]:
        """
        Get the path to ocrmypdf executable.

        Returns:
            Path to ocrmypdf or None if not found
        """
        # Check standard PATH first
        standard_path = shutil.which('ocrmypdf')
        if standard_path:
            return standard_path

        # Check common Homebrew paths (macOS)
        homebrew_paths = [
            '/opt/homebrew/bin/ocrmypdf',  # Apple Silicon
            '/usr/local/bin/ocrmypdf',      # Intel Mac
        ]

        for path in homebrew_paths:
            if os.path.exists(path):
                return path

        return None

    def is_ocrmypdf_available(self) -> bool:
        """
        Check if ocrmypdf is installed and available.

        Returns:
            True if ocrmypdf is available
        """
        return self._get_ocrmypdf_path() is not None

    def process_pdf(
        self,
        input_path: str,
        output_path: str,
        optimize_level: int = 0,
        skip_text: bool = True,
        force_ocr: bool = False,
        timeout: int = 300
    ) -> Tuple[bool, str]:
        """
        Add OCR text layer to a PDF file.

        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF with OCR
            optimize_level: Optimization level (0=none, 1=lossless, 2=lossy, 3=aggressive)
            skip_text: Skip pages that already have text
            force_ocr: Force OCR even if text exists
            timeout: Timeout in seconds (default: 5 minutes)

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        if not self.is_ocrmypdf_available():
            return False, "OCRmyPDF ist nicht installiert. Bitte installieren: brew install ocrmypdf"

        input_file = Path(input_path)
        if not input_file.exists():
            return False, f"Eingabedatei nicht gefunden: {input_path}"

        # Check file size (warn for large files)
        file_size_mb = input_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 100:
            self._log(f"  ⚠ Große Datei ({file_size_mb:.1f} MB) - OCR kann lange dauern")

        try:
            # Get ocrmypdf path
            ocrmypdf_path = self._get_ocrmypdf_path()
            if not ocrmypdf_path:
                return False, "OCRmyPDF ist nicht installiert. Bitte installieren: brew install ocrmypdf"

            # Build ocrmypdf command
            cmd = [
                ocrmypdf_path,
                '-l', self.language,
                '--optimize', str(optimize_level),
            ]

            if skip_text:
                cmd.append('--skip-text')

            if force_ocr:
                cmd.append('--force-ocr')

            # Add input and output paths
            cmd.extend([input_path, output_path])

            # Run OCR with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                return True, ""
            else:
                # Parse common error messages
                error_output = result.stderr.lower()

                if "password" in error_output or "encrypted" in error_output:
                    return False, "PDF ist passwortgeschützt"
                elif "not a valid pdf" in error_output:
                    return False, "Ungültige oder beschädigte PDF"
                elif "no text found" in error_output and skip_text:
                    # This is actually success - no OCR needed
                    return True, "Seiten enthalten bereits Text"
                else:
                    # Return first line of error
                    error_lines = result.stderr.strip().split('\n')
                    error_msg = error_lines[0] if error_lines else "Unbekannter Fehler"
                    return False, f"OCR fehlgeschlagen: {error_msg[:100]}"

        except subprocess.TimeoutExpired:
            return False, f"OCR-Timeout nach {timeout} Sekunden"
        except Exception as e:
            return False, f"OCR-Fehler: {str(e)[:100]}"

    def process_pdf_inplace(
        self,
        pdf_path: str,
        backup: bool = False,
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Process PDF with OCR in-place (replaces original).

        Args:
            pdf_path: Path to PDF file
            backup: Create backup before processing
            **kwargs: Additional arguments for process_pdf

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        pdf_file = Path(pdf_path)
        temp_output = pdf_file.with_suffix('.ocr.pdf')
        backup_path = pdf_file.with_suffix('.bak.pdf')

        try:
            # Create backup if requested
            if backup:
                shutil.copy2(pdf_path, backup_path)

            # Process with OCR
            success, error = self.process_pdf(pdf_path, str(temp_output), **kwargs)

            if success and temp_output.exists():
                # Replace original with OCR version
                os.replace(str(temp_output), pdf_path)
                return True, ""
            else:
                # Cleanup temp file on error
                if temp_output.exists():
                    temp_output.unlink()
                return False, error

        except Exception as e:
            # Restore backup on error
            if backup and backup_path.exists():
                os.replace(str(backup_path), pdf_path)
            return False, f"Fehler: {str(e)[:100]}"
        finally:
            # Cleanup backup if not needed
            if not backup and backup_path.exists():
                backup_path.unlink()

    def batch_process(
        self,
        pdf_files: list[str],
        optimize_level: int = 0,
        skip_text: bool = True,
        inplace: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> Tuple[int, int, list[str]]:
        """
        Process multiple PDF files with OCR.

        Args:
            pdf_files: List of PDF file paths
            optimize_level: Optimization level
            skip_text: Skip pages with text
            inplace: Replace original files
            progress_callback: Callback(current, total, filename)

        Returns:
            Tuple of (success_count, failed_count, failed_files)
        """
        success_count = 0
        failed_count = 0
        failed_files = []

        for idx, pdf_file in enumerate(pdf_files):
            if progress_callback:
                progress_callback(idx + 1, len(pdf_files), Path(pdf_file).name)

            self._log(f"  OCR: {Path(pdf_file).name}")

            if inplace:
                success, error = self.process_pdf_inplace(
                    pdf_file,
                    optimize_level=optimize_level,
                    skip_text=skip_text
                )
            else:
                output = Path(pdf_file).with_suffix('.ocr.pdf')
                success, error = self.process_pdf(
                    pdf_file,
                    str(output),
                    optimize_level=optimize_level,
                    skip_text=skip_text
                )

            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_files.append(f"{Path(pdf_file).name}: {error}")
                self._log(f"    ⚠ OCR fehlgeschlagen: {error}")

        return success_count, failed_count, failed_files


def check_ocr_installation() -> Tuple[bool, str]:
    """
    Check if OCR tools are properly installed.

    Returns:
        Tuple of (is_installed: bool, message: str)
    """
    # Helper to find ocrmypdf
    def find_ocrmypdf():
        # Check standard PATH
        path = shutil.which('ocrmypdf')
        if path:
            return path
        # Check Homebrew paths
        for homebrew_path in ['/opt/homebrew/bin/ocrmypdf', '/usr/local/bin/ocrmypdf']:
            if os.path.exists(homebrew_path):
                return homebrew_path
        return None

    # Check ocrmypdf
    ocrmypdf_path = find_ocrmypdf()
    if not ocrmypdf_path:
        return False, "OCRmyPDF nicht gefunden. Installation: brew install ocrmypdf"

    # Check tesseract
    if not shutil.which('tesseract'):
        return False, "Tesseract nicht gefunden. Installation: brew install tesseract"

    # Try to get version
    try:
        result = subprocess.run(
            [ocrmypdf_path, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        version = result.stdout.strip()
        return True, f"OCRmyPDF installiert: {version}"
    except Exception as e:
        return False, f"OCR-Tools gefunden, aber nicht funktionsfähig: {e}"


def get_installed_languages() -> list[str]:
    """
    Get list of installed Tesseract languages.

    Returns:
        List of language codes
    """
    try:
        result = subprocess.run(
            ['tesseract', '--list-langs'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # Parse output (skip first line "List of available languages")
            lines = result.stdout.strip().split('\n')[1:]
            return [line.strip() for line in lines if line.strip()]
        else:
            return ['eng']  # Fallback to English

    except Exception:
        return ['eng']  # Fallback
