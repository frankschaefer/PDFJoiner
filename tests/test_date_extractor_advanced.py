"""Advanced tests for Date Extractor with special characters."""

import pytest
from datetime import datetime
from src.pdf_joiner.date_extractor import DateExtractor


class TestDateExtractorAdvanced:
    """Advanced test cases for DateExtractor with special characters."""

    @pytest.fixture
    def extractor(self):
        """Create DateExtractor instance."""
        return DateExtractor()

    def test_extract_from_filename_with_emoji(self, extractor):
        """Test date extraction from filename with emoji."""
        filename = "  Akzeptieren Sie beliebte Zahlungsmethoden ✅ _29-07-2025.pdf"
        date = extractor.extract_date_from_filename(filename)

        assert date is not None, "Should extract date from filename with emoji"
        assert date.year == 2025
        assert date.month == 7
        assert date.day == 29

    def test_extract_from_filename_with_leading_spaces(self, extractor):
        """Test date extraction from filename with leading spaces."""
        filename = "  Geben Sie Ihrer Kundschaft flexible Zahlungsmöglichkeiten_17-07-2025.pdf"
        date = extractor.extract_date_from_filename(filename)

        assert date is not None, "Should extract date from filename with leading spaces"
        assert date.year == 2025
        assert date.month == 7
        assert date.day == 17

    def test_extract_from_filename_with_umlauts(self, extractor):
        """Test date extraction from filename with German umlauts."""
        filename = "Geschäftsführung_Bürgermeister_25-12-2025.pdf"
        date = extractor.extract_date_from_filename(filename)

        assert date is not None, "Should extract date from filename with umlauts"
        assert date.year == 2025
        assert date.month == 12
        assert date.day == 25

    def test_extract_from_filename_with_multiple_spaces(self, extractor):
        """Test date extraction from filename with multiple spaces."""
        filename = "  Steigern Sie Ihre Umsätze mit unserem Checkout_25-07-2025.pdf"
        date = extractor.extract_date_from_filename(filename)

        assert date is not None, "Should extract date from filename with multiple spaces"
        assert date.year == 2025
        assert date.month == 7
        assert date.day == 25

    def test_extract_from_filename_with_special_chars(self, extractor):
        """Test date extraction from filename with various special characters."""
        test_cases = [
            ("File & Document_15-03-2025.pdf", datetime(2025, 3, 15)),
            ("Report (Final)_20-06-2025.pdf", datetime(2025, 6, 20)),
            ("Data@Company_10-09-2025.pdf", datetime(2025, 9, 10)),
            ("File#123_05-11-2025.pdf", datetime(2025, 11, 5)),
        ]

        for filename, expected_date in test_cases:
            date = extractor.extract_date_from_filename(filename)
            assert date is not None, f"Should extract date from: {filename}"
            assert date.year == expected_date.year
            assert date.month == expected_date.month
            assert date.day == expected_date.day

    def test_extract_date_formats_with_special_chars(self, extractor):
        """Test various date formats in filenames with special characters."""
        test_cases = [
            "Invoice ✓_13-11-2025.pdf",
            "Report ★_2025-11-13.pdf",
            "Document ●_13.11.2025.pdf",
            # Note: Slash format (31/12/2025) may not be recognized by all date parsers
            # as it's commonly used in paths and could be ambiguous
        ]

        for filename in test_cases:
            date = extractor.extract_date_from_filename(filename)
            assert date is not None, f"Should extract date from: {filename}"
            assert isinstance(date, datetime)

    def test_no_date_in_special_filename(self, extractor):
        """Test filename with special chars but no date."""
        filename = "  Important Document ✅ Final Version.pdf"
        date = extractor.extract_date_from_filename(filename)

        assert date is None, "Should return None when no date found"

    def test_extract_from_full_path_with_special_chars(self, extractor):
        """Test date extraction from full path with special characters."""
        filepath = "/Users/test/Desktop/Folder ✅/  Document_29-07-2025.pdf"
        date = extractor.extract_date_from_filename(filepath)

        assert date is not None, "Should extract date from path with special chars"
        assert date.year == 2025
        assert date.month == 7
        assert date.day == 29

    def test_unicode_normalization(self, extractor):
        """Test that Unicode characters don't interfere with date extraction."""
        test_cases = [
            "Café Menu_15-01-2025.pdf",
            "Résumé_20-02-2025.pdf",
            "Naïve Approach_25-03-2025.pdf",
            "Zürich Report_30-04-2025.pdf",
        ]

        for filename in test_cases:
            date = extractor.extract_date_from_filename(filename)
            assert date is not None, f"Should extract date from: {filename}"
            assert isinstance(date, datetime)

    def test_real_world_filenames(self, extractor):
        """Test with actual filenames from the test files."""
        real_filenames = [
            "  Akzeptieren Sie beliebte Zahlungsmethoden ✅ _29-07-2025.pdf",
            "  Geben Sie Ihrer Kundschaft flexible Zahlungsmöglichkeiten_17-07-2025.pdf",
            "  Steigern Sie Ihre Umsätze mit unserem Checkout_25-07-2025.pdf",
        ]

        expected_dates = [
            datetime(2025, 7, 29),
            datetime(2025, 7, 17),
            datetime(2025, 7, 25),
        ]

        for filename, expected_date in zip(real_filenames, expected_dates):
            date = extractor.extract_date_from_filename(filename)
            assert date is not None, f"Should extract date from: {filename}"
            assert date.year == expected_date.year
            assert date.month == expected_date.month
            assert date.day == expected_date.day

    def test_sorting_with_special_chars(self, extractor):
        """Test that files with special chars can be sorted by date."""
        filenames = [
            "  File C ✅_25-07-2025.pdf",
            "  File A ★_17-07-2025.pdf",
            "  File B ●_29-07-2025.pdf",
        ]

        # Extract dates and sort
        files_with_dates = []
        for filename in filenames:
            date = extractor.extract_date_from_filename(filename)
            files_with_dates.append((filename, date))

        # Sort by date (newest first)
        sorted_files = sorted(files_with_dates, key=lambda x: x[1] if x[1] else datetime.min, reverse=True)

        # Verify order
        assert "29-07-2025" in sorted_files[0][0]
        assert "25-07-2025" in sorted_files[1][0]
        assert "17-07-2025" in sorted_files[2][0]
