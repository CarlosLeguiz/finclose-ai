"""
Generators for the 4 dimension tables (accounts, cost centers, periods, exchange rates).
"""

from datetime import datetime
from faker import Faker

from data_generator.config import (
    NUM_ACCOUNTS,
    FAKER_LOCALE,
    RANDOM_SEED,
    ACCOUNT_TYPE_RANGES,
    ACCOUNT_DISTRIBUTION,
    COST_CENTERS,
)
from data_generator.schemas import Account, CostCenter


def generate_accounts(num_accounts: int = NUM_ACCOUNTS) -> list[Account]:
    """
    Generate a list of synthetic Account instances for the dim_accounts table.
    
    Args:
        num_accounts: Number of accounts to generate. Defaults to NUM_ACCOUNTS from config.
    
    Returns:
        List of Account instances ready to be loaded into dim_accounts.
    """
     # Initialize Faker with locale and seed for reproducibility
    fake = Faker(FAKER_LOCALE)
    Faker.seed(RANDOM_SEED)

    accounts = []
    account_counter = 0

    for account_type, count in ACCOUNT_DISTRIBUTION.items():
        min_code, max_code = ACCOUNT_TYPE_RANGES[account_type]
        
        for offset in range(count):
            current_code = min_code + offset

            account = Account(
                account_id=f"ACC{account_counter:03d}",
                account_code=f"{current_code}",
                account_name=fake.bs().capitalize(),
                account_type=account_type,
                parent_account_id=None,
                is_active=True,
                created_at=datetime.now(),
            )
            accounts.append(account)
            account_counter += 1
        
    return accounts

def generate_cost_centers() -> list[CostCenter]:
    """Generate cost center dimension records.

    Returns:
        List of CostCenter instances based on the COST_CENTERS config.
    """
    cost_centers = []

    for i, (code, name, department, manager_name) in enumerate(COST_CENTERS):
        cost_center = CostCenter(
            cost_center_id=f"CC{i:03d}",
            code=code,
            name=name,
            department=department,
            manager_name=manager_name,
            is_active=True,
            created_at=datetime.now(),
        )
        cost_centers.append(cost_center)

    return cost_centers