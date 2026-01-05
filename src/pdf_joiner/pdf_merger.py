"""PDF merging functionality."""

from PyPDF2 import PdfMerger
from pathlib import Path
from typing import List


class PDFMerger:
    """Handles PDF file merging operations."""

    def __init__(self):
        self.merger = PdfMerger()

    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> bool:
        """
        Merge multiple PDF files into a single PDF.

        Args:
            pdf_files: List of paths to PDF files to merge
            output_path: Path where the merged PDF will be saved

        Returns:
            True if successful, False otherwise
        """
        try:
            self.merger = PdfMerger()

            for pdf_file in pdf_files:
                if not Path(pdf_file).exists():
                    raise FileNotFoundError(f"File not found: {pdf_file}")
                self.merger.append(pdf_file)

            self.merger.write(output_path)
            self.merger.close()
            return True

        except Exception as e:
            print(f"Error merging PDFs: {e}")
            return False

    def close(self):
        """Clean up resources."""
        if self.merger:
            self.merger.close()
