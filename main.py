#!/usr/bin/env python
"""Main entry point for PDF Joiner application."""

import sys
from src.pdf_joiner.batch_gui import run_batch_app
from src.pdf_joiner.gui import run_app


def main():
    """Main entry point with mode selection."""
    # Default to batch mode
    if len(sys.argv) > 1 and sys.argv[1] == "--simple":
        # Simple mode: original single-file merger
        run_app()
    else:
        # Batch mode: folder-based batch processing
        run_batch_app()


if __name__ == "__main__":
    main()
