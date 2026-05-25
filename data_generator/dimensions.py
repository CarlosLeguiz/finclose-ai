"""
Generators for the 4 dimension tables (accounts, cost centers, periods, exchange rates).
"""

from datetime import datetime
from typing import List
from faker import Faker

from data_generator.config import NUM_ACCOUNTS, FAKER_LOCALE, RANDOM_SEED
from data_generator.schemas import Account

ACCOUNT_TYPES = ["Asset", "Liability", "Equity", "Revenue", "Expense"]

def generate_accounts(num_accounts: int = NUM_ACCOUNTS) -> List[Account]:
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

    for i in range(num_accounts):
        account = Account(
            account_id=f"ACC{i:03d}",
            account_code=f"{5000 + i}",
            account_name=fake.bs().capitalize(),
            account_type=fake.random_element(elements=ACCOUNT_TYPES),
            parent_account_id=None,
            is_active=True,
            created_at=datetime.now(),
        )
        accounts.append(account)
        
    return accounts