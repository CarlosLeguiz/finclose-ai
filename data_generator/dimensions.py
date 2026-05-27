"""
Generators for the 4 dimension tables (accounts, cost centers, periods, exchange rates).
"""

from datetime import datetime, date
from faker import Faker
from calendar import monthrange

from data_generator.config import (
    NUM_ACCOUNTS,
    FAKER_LOCALE,
    RANDOM_SEED,
    ACCOUNT_TYPE_RANGES,
    ACCOUNT_DISTRIBUTION,
    COST_CENTERS,
    START_YEAR,
    END_YEAR,
)
from data_generator.schemas import Account, CostCenter, Period


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

def generate_periods() -> list[Period]:
    """Generate accounting period dimension records.

    Creates one Period per month between START_YEAR and END_YEAR.
    Periods before today are marked as closed.

    Returns:
        List of Period instances ready to be loaded into dim_periods.
    """
    periods = []
    today = date.today()

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            # Calculate last day of the month
            _, last_day = monthrange(year, month)

            start_date = date(year, month, 1)
            end_date = date(year, month, last_day)

            # A period is "closed" if its end_date is in the past
            is_closed = end_date < today
            closed_at = datetime.now() if is_closed else None

            # Month name in English (January, February, etc.)
            month_name = start_date.strftime("%B")

            period = Period(
                period_id=f"{year}-{month:02d}",
                year=year,
                month=month,
                period_name=f"{month_name} {year}",
                quarter=(month - 1) // 3 + 1,
                start_date=start_date,
                end_date=end_date,
                is_closed=is_closed,
                closed_at=closed_at,
            )
            periods.append(period)

    return periods