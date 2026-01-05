"""Extract dates from PDF filenames."""

import re
from datetime import datetime
from typing import Optional
from dateutil import parser


class DateExtractor:
    """Extract and parse dates from filenames."""

    # Common date patterns in filenames
    DATE_PATTERNS = [
        r'(\d{1,2}[-_.]\d{1,2}[-_.]\d{4})',  # DD-MM-YYYY or DD.MM.YYYY or DD_MM_YYYY
        r'(\d{4}[-_.]\d{1,2}[-_.]\d{1,2})',  # YYYY-MM-DD or YYYY.MM.DD or YYYY_MM_DD
        r'(\d{1,2}[-_.]\d{1,2}[-_.]\d{2})',  # DD-MM-YY or DD.MM.YY or DD_MM_YY
    ]

    @staticmethod
    def extract_date_from_filename(filename: str) -> Optional[datetime]:
        """
        Extract date from filename.

        Args:
            filename: The filename to parse

        Returns:
            datetime object if date found, None otherwise
        """
        # Try each pattern
        for pattern in DateExtractor.DATE_PATTERNS:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1)
                try:
                    # Try to parse the date string
                    # Replace separators with hyphens for consistent parsing
                    date_str_normalized = re.sub(r'[_.]', '-', date_str)

                    # Use dateutil parser which is more flexible
                    date_obj = parser.parse(date_str_normalized, dayfirst=True)
                    return date_obj
                except (ValueError, parser.ParserError):
                    continue

        return None

    @staticmethod
    def sort_files_by_date(file_paths: list[str], newest_first: bool = True) -> list[str]:
        """
        Sort file paths by date extracted from filename.
        Files without dates are placed at the end.

        Args:
            file_paths: List of file paths to sort
            newest_first: If True, newest files first; if False, oldest first

        Returns:
            Sorted list of file paths
        """
        def get_sort_key(filepath: str) -> tuple:
            date = DateExtractor.extract_date_from_filename(filepath)
            if date is None:
                # Files without dates get a far future/past date depending on sort order
                return (datetime.max if newest_first else datetime.min, filepath)
            return (date, filepath)

        sorted_files = sorted(file_paths, key=get_sort_key, reverse=newest_first)
        return sorted_files
