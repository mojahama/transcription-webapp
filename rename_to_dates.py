#!/usr/bin/env python3
"""
Rename output .docx files to date format (YYYYMMDD).
Extracts date from filename and renames to format like 20210709.docx
"""

import os
import re
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = "output"

# Month name to number mapping
MONTHS = {
    'jan': 1, 'january': 1,
    'feb': 2, 'february': 2,
    'mar': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'may': 5,
    'jun': 6, 'june': 6,
    'jul': 7, 'july': 7,
    'aug': 8, 'august': 8,
    'sep': 9, 'sept': 9, 'september': 9,
    'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'dec': 12, 'december': 12
}

def extract_date(filename):
    """
    Extract date from filename and return as YYYYMMDD string.

    Handles formats like:
    - "Something - Mar 31, 2023.docx"
    - "Something - October 18, 2024.docx"
    - "Something - Sep 16, 2022.docx"
    """
    # Pattern: Month Day, Year (e.g., "Mar 31, 2023" or "October 18, 2024")
    pattern = r'(\w+)\s+(\d{1,2}),?\s*(\d{4})'

    match = re.search(pattern, filename)
    if not match:
        return None

    month_str = match.group(1).lower()
    day = int(match.group(2))
    year = int(match.group(3))

    # Get month number
    month = MONTHS.get(month_str)
    if not month:
        return None

    # Format as YYYYMMDD
    return f"{year}{month:02d}{day:02d}"

def main():
    output_path = Path(OUTPUT_DIR)

    if not output_path.exists():
        print(f"Output directory '{OUTPUT_DIR}' not found")
        return

    docx_files = list(output_path.glob("*.docx"))

    if not docx_files:
        print(f"No .docx files found in '{OUTPUT_DIR}/'")
        return

    print(f"Found {len(docx_files)} files to process\n")

    renamed = 0
    skipped = 0
    failed = 0

    for filepath in sorted(docx_files):
        old_name = filepath.name

        # Skip if already in date format
        if re.match(r'^\d{8}\.docx$', old_name):
            print(f"SKIP (already formatted): {old_name}")
            skipped += 1
            continue

        # Extract date from filename
        date_str = extract_date(old_name)

        if not date_str:
            print(f"FAIL (no date found): {old_name}")
            failed += 1
            continue

        new_name = f"{date_str}.docx"
        new_path = filepath.parent / new_name

        # Check for conflicts
        if new_path.exists() and new_path != filepath:
            # Add suffix for duplicates
            counter = 1
            while new_path.exists():
                new_name = f"{date_str}_{counter}.docx"
                new_path = filepath.parent / new_name
                counter += 1

        # Rename the file
        try:
            filepath.rename(new_path)
            print(f"OK: {old_name} -> {new_name}")
            renamed += 1
        except Exception as e:
            print(f"ERROR: {old_name} -> {str(e)}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Renamed: {renamed}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Total: {len(docx_files)}")

if __name__ == "__main__":
    main()
