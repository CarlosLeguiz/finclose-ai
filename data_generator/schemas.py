"""
Data class definitions for the 7 tables in FinClose AI.
"""
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class Account:
    """
    Represents a single row in the dim_accounts table.
    
    Each Account is an entry in the chart of accounts, with:
    - A surrogate key (account_id)
    - A business code (account_code)
    - A type that determines its accounting behavior (Asset/Liability/etc.)
    """
    account_id: str
    account_code: str
    account_name: str
    account_type: str
    parent_account_id: str | None
    is_active: bool
    created_at: datetime

@dataclass
class CostCenter:
    cost_center_id: str
    code: str
    name: str
    department: str
    manager_name: str | None
    is_active: bool
    created_at: datetime

@dataclass
class Period:
    period_id: str        # "2024-01", "2024-02", ..., "2026-12"
    year: int             # 2024, 2025, 2026
    month: int            # 1-12
    period_name: str      # "January 2024"
    quarter: int          # 1-4
    start_date: date      # primer día del mes
    end_date: date        # último día del mes
    is_closed: bool       # True past periods, False future periods
    closed_at: datetime | None  # timestamp is close, None is open

@dataclass
class ExchangeRate:
    """Represents a single exchange rate between two currencies on a specific date."""
    rate_id: str
    from_currency: str       # ISO 4217: "USD", "EUR", "ARS"
    to_currency: str
    rate_date: date
    rate: float              # rate value (e.g., 920.50 means 1 USD = 920.50 ARS)
    source: str              # e.g., "BCRA"
    created_at: datetime