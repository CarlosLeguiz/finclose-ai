"""Persistence layer for the data generator.

Functions in this module convert generated data objects into
files on disk (CSV initially, Parquet later).
"""

from dataclasses import asdict
from pathlib import Path

import pandas as pd

from data_generator.schemas import Account


def save_accounts_to_csv(accounts: list[Account], output_path: Path) -> None:
    """Save a list of Account instances to a CSV file.

    Args:
        accounts: List of Account dataclass instances.
        output_path: Destination path for the CSV file.
    """
    # Convert each Account dataclass to a dictionary
    accounts_as_dicts = [asdict(account) for account in accounts]

    # Build the DataFrame from the list of dicts
    df = pd.DataFrame(accounts_as_dicts)

    # Ensure the parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to CSV without the pandas index column
    df.to_csv(output_path, index=False)

    print(f"Saved {len(accounts)} accounts to {output_path}")