"""
Test helper functions.

Provides common test helper functions to eliminate duplication
across test files.
"""

import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.rag.generic_data_processor import DataSchema


def create_test_csv(
    headers: List[str],
    rows: List[List[str]] = None,
    suffix: str = '.csv'
) -> str:
    """
    Create a temporary CSV file for testing.
    
    Args:
        headers: List of column headers
        rows: List of data rows (optional)
        suffix: File suffix (default: '.csv')
        
    Returns:
        str: Path to the temporary CSV file
    """
    if rows is None:
        rows = []
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        # Write headers
        f.write(",".join(f'"{header}"' for header in headers) + "\n")
        # Write data rows
        for row in rows:
            f.write(",".join(f'"{str(cell)}"' for cell in row) + "\n")
        return f.name


def get_test_data_schema(
    required_columns: List[str],
    sensitive_columns: List[str] = None,
    date_columns: List[str] = None,
    text_columns: List[str] = None,
    metadata_columns: List[str] = None,
    id_column: str = None
) -> DataSchema:
    """
    Create a test data schema with configurable fields.
    
    Args:
        required_columns: List of required column names
        sensitive_columns: List of sensitive column names
        date_columns: List of date column names
        text_columns: List of text column names
        metadata_columns: List of metadata column names
        id_column: Primary ID column name
        
    Returns:
        DataSchema: Configured data schema for testing
    """
    if sensitive_columns is None:
        sensitive_columns = []
    if date_columns is None:
        date_columns = []
    if text_columns is None:
        text_columns = []
    if metadata_columns is None:
        metadata_columns = []
    if id_column is None:
        id_column = required_columns[0] if required_columns else "ID"
    
    return DataSchema(
        required_columns=required_columns,
        sensitive_columns=sensitive_columns,
        date_columns=date_columns,
        text_columns=text_columns,
        metadata_columns=metadata_columns,
        id_column=id_column
    )


def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up a temporary file.
    
    Args:
        file_path: Path to the file to delete
    """
    try:
        Path(file_path).unlink()
    except FileNotFoundError:
        pass  # File already deleted or doesn't exist
