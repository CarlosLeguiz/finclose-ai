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
    CURRENCY_PAIRS,
    USD_ARS_ANCHORS,
    EUR_USD_RATIO,
    EXCHANGE_RATE_SOURCE,
    RATE_MONTHLY_VOLATILITY
)
from data_generator.schemas import Account, CostCenter, Period, ExchangeRate


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

def _find_anchors(year: int, month: int, anchors: dict) -> tuple:
    """Find the two anchor points that surround a given (year, month).

    Returns:
        Tuple ((y1, m1, rate1), (y2, m2, rate2)) where the target is between them.
    """
    target_index = year * 12 + month  # convert (year, month) to a single number
    sorted_anchors = sorted(anchors.items())  # sort by (year, month)

    prev_anchor = sorted_anchors[0]
    next_anchor = sorted_anchors[-1]

    for (y, m), rate in sorted_anchors:
        anchor_index = y * 12 + m
        if anchor_index <= target_index:
            prev_anchor = ((y, m), rate)
        if anchor_index >= target_index and next_anchor == sorted_anchors[-1]:
            next_anchor = ((y, m), rate)
            break

    return prev_anchor, next_anchor


def _interpolate_rate(year: int, month: int, anchors: dict) -> float:
    """Linear interpolation between the two nearest anchors.

    Args:
        year, month: target month to compute rate for
        anchors: dict {(year, month): rate}

    Returns:
        Interpolated rate value.
    """
    prev_anchor, next_anchor = _find_anchors(year, month, anchors)
    (y1, m1), rate1 = prev_anchor
    (y2, m2), rate2 = next_anchor

    # If exact anchor, return its value
    if (y1, m1) == (y2, m2):
        return rate1

    # Linear interpolation formula
    target_index = year * 12 + month
    idx1 = y1 * 12 + m1
    idx2 = y2 * 12 + m2

    progress = (target_index - idx1) / (idx2 - idx1)
    return rate1 + (rate2 - rate1) * progress

def generate_exchange_rates() -> list[ExchangeRate]:
    """Generate exchange rate dimension records.

    Creates monthly rates for each currency pair defined in CURRENCY_PAIRS.
    USD/ARS rates are interpolated from historical anchors with small
    random volatility. EUR/ARS rates are derived from USD/ARS * EUR_USD_RATIO.

    Returns:
        List of ExchangeRate instances ready to be loaded into dim_exchange_rates.
    """
    import random
    random.seed(RANDOM_SEED)

    rates = []
    rate_counter = 0

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            # Last day of the month is the reference rate_date
            _, last_day = monthrange(year, month)
            rate_date = date(year, month, last_day)

            # Compute USD/ARS base rate with volatility
            base_usd_ars = _interpolate_rate(year, month, USD_ARS_ANCHORS)
            noise = random.uniform(-RATE_MONTHLY_VOLATILITY, RATE_MONTHLY_VOLATILITY)
            usd_ars_rate = round(base_usd_ars * (1 + noise), 2)

            # USD → ARS
            rates.append(
                ExchangeRate(
                    rate_id=f"RATE{rate_counter:04d}",
                    from_currency="USD",
                    to_currency="ARS",
                    rate_date=rate_date,
                    rate=usd_ars_rate,
                    source=EXCHANGE_RATE_SOURCE,
                    created_at=datetime.now(),
                )
            )
            rate_counter += 1

            # EUR → ARS (derived from USD/ARS)
            eur_ars_rate = round(usd_ars_rate * EUR_USD_RATIO, 2)
            rates.append(
                ExchangeRate(
                    rate_id=f"RATE{rate_counter:04d}",
                    from_currency="EUR",
                    to_currency="ARS",
                    rate_date=rate_date,
                    rate=eur_ars_rate,
                    source=EXCHANGE_RATE_SOURCE,
                    created_at=datetime.now(),
                )
            )
            rate_counter += 1

    return rates