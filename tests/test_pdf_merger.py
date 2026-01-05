"""Tests for PDF merger functionality."""

import pytest
from pathlib import Path
from src.pdf_joiner.pdf_merger import PDFMerger


def test_pdf_merger_initialization():
    """Test that PDFMerger initializes correctly."""
    merger = PDFMerger()
    assert merger is not None
    merger.close()


def test_merge_pdfs_with_nonexistent_file():
    """Test that merge fails gracefully with nonexistent files."""
    merger = PDFMerger()
    result = merger.merge_pdfs(
        ["nonexistent1.pdf", "nonexistent2.pdf"],
        "output.pdf"
    )
    assert result is False
    merger.close()
