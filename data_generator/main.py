"""Main orchestrator for the data generator.

Run with:
    poetry run python -m data_generator.main
"""

from pathlib import Path

from data_generator.schemas import Account, CostCenter
from data_generator.dimensions import generate_accounts, generate_cost_centers
from data_generator.persistence import save_to_csv


def main() -> None:
    """Generate all tables and persist them to disk."""
    output_dir = Path("data/raw")

    # Dimension: accounts
    accounts = generate_accounts()
    save_to_csv(accounts, output_dir / "dim_accounts.csv")

    # Dimension: cost centers
    cost_centers = generate_cost_centers()
    save_to_csv(cost_centers, output_dir / "dim_cost_centers.csv")


if __name__ == "__main__": ##If this file is running directly, call main(). If it's being imported from another file, do nothing.
    main()  

