"""
Utility functions for saving election results to CSV files.

Provides a helper to write a list of dictionaries to a CSV file with
specified headers.
"""

from pathlib import Path
import csv


def save_csv(data: list[dict], headers: list[str], filename: str) -> None:
    """
    Save a list of dictionaries to a CSV file with specified headers.

    Args:
        data (list[dict]): List of result rows, each as a dictionary.
        headers (list[str]): List of CSV column headers.
        filename (str): Output CSV filename. Extension will be forced
            to .csv.

    Raises:
        RuntimeError: If file writing fails due to OS or CSV error.
    """
    p = Path(filename)
    root = p.stem
    name = f'{root}.csv'
    try:
        with open(name, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, headers)
            writer.writeheader()
            writer.writerows(data)
        print(f'File {name} exported.')
    except (OSError, csv.Error) as e:
        raise RuntimeError(
            f'Error writing CSV file {name}: {e}'
        ) from e
