"""Batch processing of PDF folders."""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Callable, Optional
import threading
from .pdf_merger import PDFMerger
from .date_extractor import DateExtractor


class BatchProcessor:
    """Handles batch processing of PDF folders."""

    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        self.current_folder = None
        self.progress_callback: Optional[Callable] = None
        self.log_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates."""
        self.progress_callback = callback

    def set_log_callback(self, callback: Callable):
        """Set callback for log messages."""
        self.log_callback = callback

    def _log(self, message: str):
        """Log a message."""
        if self.log_callback:
            self.log_callback(message)

    def _update_progress(self, current: int, total: int, message: str = ""):
        """Update progress."""
        if self.progress_callback:
            self.progress_callback(current, total, message)

    def validate_and_fix_path(self, base_path: str) -> Optional[str]:
        """
        Validate path and fallback to parent if it doesn't exist.

        Args:
            base_path: Path to validate

        Returns:
            Valid path or None if no valid path found
        """
        # Try the original path
        if os.path.exists(base_path) and os.path.isdir(base_path):
            return base_path

        # Try parent directory
        parent_path = os.path.dirname(base_path)
        if os.path.exists(parent_path) and os.path.isdir(parent_path):
            self._log(f"Original path not found. Using parent directory: {parent_path}")
            return parent_path

        # Try grandparent if parent also doesn't exist
        grandparent_path = os.path.dirname(parent_path)
        if os.path.exists(grandparent_path) and os.path.isdir(grandparent_path):
            self._log(f"Parent path not found. Using grandparent directory: {grandparent_path}")
            return grandparent_path

        return None

    def get_folders_in_directory(self, base_path: str) -> List[str]:
        """
        Get all folders in the specified directory.

        Args:
            base_path: Path to the base directory

        Returns:
            List of folder paths
        """
        # Validate and fix path first
        valid_path = self.validate_and_fix_path(base_path)
        if not valid_path:
            self._log(f"Error: Could not find valid directory at {base_path}")
            return []

        try:
            folders = []
            for item in os.listdir(valid_path):
                item_path = os.path.join(valid_path, item)
                if os.path.isdir(item_path):
                    folders.append(item_path)
            return sorted(folders)
        except Exception as e:
            self._log(f"Error reading directory: {e}")
            return []

    def _is_joined_pdf(self, filename: str) -> bool:
        """
        Check if a PDF filename matches the joined PDF pattern.
        Pattern: <anything>_YYYY-MM-DD_HH-MM-SS.pdf

        Args:
            filename: Name of the PDF file

        Returns:
            True if filename matches joined PDF pattern
        """
        # Pattern: ends with _YYYY-MM-DD_HH-MM-SS.pdf
        pattern = r'.*_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.pdf$'
        return bool(re.match(pattern, filename, re.IGNORECASE))

    def get_pdf_files_in_folder(self, folder_path: str) -> List[str]:
        """
        Get all PDF files in a folder, excluding previously joined PDFs.

        Args:
            folder_path: Path to the folder

        Returns:
            List of PDF file paths (excluding joined PDFs)
        """
        pdf_files = []
        skipped_count = 0
        try:
            for file in os.listdir(folder_path):
                if file.lower().endswith('.pdf'):
                    # Skip previously joined PDFs
                    if self._is_joined_pdf(file):
                        skipped_count += 1
                        continue
                    pdf_files.append(os.path.join(folder_path, file))

            if skipped_count > 0:
                self._log(f"  Skipped {skipped_count} previously joined PDF(s)")
        except Exception as e:
            self._log(f"Error reading folder {folder_path}: {e}")

        return pdf_files

    def create_output_filename(self, folder_path: str) -> str:
        """
        Create output filename from folder name and creation date.
        Format: <folder_name>_<YYYY-MM-DD>_<HH-MM-SS>.pdf

        Args:
            folder_path: Path to the folder

        Returns:
            Output filename
        """
        folder_name = os.path.basename(folder_path)

        # Get folder creation time
        try:
            creation_time = os.path.getctime(folder_path)
            dt = datetime.fromtimestamp(creation_time)
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H-%M-%S")
        except Exception:
            # Fallback to current time
            dt = datetime.now()
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H-%M-%S")

        # Sanitize folder name for filename
        safe_folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_')).strip()

        return f"{safe_folder_name}_{date_str}_{time_str}.pdf"

    def verify_pdf_file(self, file_path: str, min_size: int = 100) -> bool:
        """
        Verify that PDF file was created successfully.

        Args:
            file_path: Path to the PDF file
            min_size: Minimum file size in bytes

        Returns:
            True if file exists and has reasonable size
        """
        try:
            if not os.path.exists(file_path):
                return False

            file_size = os.path.getsize(file_path)
            return file_size >= min_size
        except Exception:
            return False

    def process_folders(self, selected_folders: List[str], base_path: str, delete_source: bool = True, quality: str = "medium"):
        """
        Process selected folders and merge PDFs.

        Args:
            selected_folders: List of folder names to process
            base_path: Base directory path
            delete_source: Whether to delete source PDFs after successful merge (default: True)
            quality: Image quality preset - "high", "medium", "low", or "original" (default: "medium")
        """
        self.is_running = True
        self.should_stop = False

        total_folders = len(selected_folders)
        deletion_status = "enabled" if delete_source else "disabled"
        self._log(f"Starting batch processing of {total_folders} folders...")
        self._log(f"Source file deletion: {deletion_status}")
        self._log(f"Image quality: {quality}")

        # Phase 1: Count all PDF files across all folders
        self._log(f"\nCounting PDF files in {total_folders} folders...")
        total_files = 0
        folder_file_counts = {}

        for folder_name in selected_folders:
            if self.should_stop:
                break

            folder_path = os.path.join(base_path, folder_name)
            pdf_files = self.get_pdf_files_in_folder(folder_path)
            folder_file_counts[folder_name] = len(pdf_files)
            total_files += len(pdf_files)

            # Update progress during counting (~10 times per second simulation)
            self._update_progress(0, 100, f"Counting files: {total_files} PDFs found...")

        self._log(f"Found {total_files} total PDF files across {total_folders} folders")

        if total_files == 0:
            self._log("No PDF files to process!")
            self.is_running = False
            return

        # Phase 2: Process files with file-level progress tracking
        files_processed = 0

        for idx, folder_name in enumerate(selected_folders):
            if self.should_stop:
                self._log("Processing stopped by user.")
                break

            # Wait while paused
            while self.is_paused and not self.should_stop:
                threading.Event().wait(0.1)

            if self.should_stop:
                break

            folder_path = os.path.join(base_path, folder_name)
            self.current_folder = folder_name

            self._log(f"\n[{idx + 1}/{total_folders}] Processing folder: {folder_name}")

            # Get PDF files
            pdf_files = self.get_pdf_files_in_folder(folder_path)

            if not pdf_files:
                self._log(f"  No PDF files found in {folder_name}")
                continue

            self._log(f"  Found {len(pdf_files)} PDF files")

            # Update progress before starting this folder
            progress_percent = (files_processed / total_files) * 100 if total_files > 0 else 0
            self._update_progress(files_processed, total_files,
                                f"Processing file {files_processed + 1}/{total_files} in {folder_name}")

            # Sort by date (newest first)
            sorted_files = DateExtractor.sort_files_by_date(pdf_files, newest_first=True)

            # Create output filename
            output_filename = self.create_output_filename(folder_path)
            output_path = os.path.join(folder_path, output_filename)

            self._log(f"  Output: {output_filename}")
            self._log(f"  Merging PDFs (sorted by date, newest first)...")

            # Merge PDFs with progress updates and quality setting
            merger = PDFMerger(quality=quality)
            success = merger.merge_pdfs(sorted_files, output_path)
            merger.close()

            # Update progress after merging files in this folder
            files_processed += len(sorted_files)
            self._update_progress(files_processed, total_files,
                                f"Processed {files_processed}/{total_files} files")

            if success and self.verify_pdf_file(output_path):
                self._log(f"  ✓ Successfully merged {len(sorted_files)} PDFs")

                # Delete source files if requested
                if delete_source:
                    deleted_count = 0
                    for pdf_file in sorted_files:
                        try:
                            os.remove(pdf_file)
                            deleted_count += 1
                        except Exception as e:
                            self._log(f"  Warning: Could not delete {os.path.basename(pdf_file)}: {e}")

                    self._log(f"  ✓ Removed {deleted_count} source PDF files")
                else:
                    self._log(f"  ℹ Source files retained ({len(sorted_files)} PDFs preserved)")
            else:
                self._log(f"  ✗ Failed to merge PDFs in {folder_name}")
                # Delete failed output file if it exists
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception:
                        pass

        self._update_progress(total_files, total_files, "Processing complete")
        self._log(f"\nBatch processing completed!")
        self.is_running = False

    def pause(self):
        """Pause processing."""
        self.is_paused = True

    def resume(self):
        """Resume processing."""
        self.is_paused = False

    def stop(self):
        """Stop processing."""
        self.should_stop = True
        self.is_paused = False
