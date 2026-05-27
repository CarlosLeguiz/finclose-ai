"""Persistence layer for the data generator.

Functions in this module convert generated data objects into
files on disk (CSV initially, Parquet later).
"""

from dataclasses import asdict
from pathlib import Path

import pandas as pd

def save_to_csv(data: list, output_path: Path) -> None:
    """Save a list of dataclass instances to a CSV file.

    Args:
        data: List of dataclass instances (Account, CostCenter, Period, etc.).
        output_path: Destination path for the CSV file.
    """
    # Convert each dataclass instance to a dictionary
    data_as_dicts = [asdict(item) for item in data]

    # Build the DataFrame from the list of dicts
    df = pd.DataFrame(data_as_dicts)

    # Ensure the parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to CSV without the pandas index column
    df.to_csv(output_path, index=False)

    print(f"Saved {len(data)} rows to {output_path}")