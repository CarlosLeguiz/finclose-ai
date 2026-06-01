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

@dataclass
class JournalEntry:
    """Header of an accounting journal entry.

    Each row represents a single economic event (payment, sale, adjustment).
    Monetary amounts live in fact_journal_lines, not here.
    """
    je_id: str                       # "JE000001"
    period_id: str                   # FK to dim_periods: "2024-03"
    entry_date: date                 # actual document date
    description: str                 # short business description
    source_system: str               # ERP / Manual / Adjustment / Reversal
    created_by: str                  # user who loaded the entry
    status: str                      # Draft / Posted / Reversed
    created_at: datetime             # when the row was created
    posted_at: datetime | None       # when posted to ledger (None if not posted)

@dataclass
class JournalLine:
    """Single line of a journal entry (debit or credit).

    Each line belongs to exactly one JournalEntry (parent) and references
    one Account. The parent entry's lines must satisfy double-entry rule:
    SUM(debit_amount) == SUM(credit_amount).
    """
    je_line_id: str                    # "JEL0000001"
    je_id: str                          # FK to fact_journal_entries
    line_number: int                    # order within the entry (1, 2, ...)
    account_id: str                     # FK to dim_accounts
    cost_center_id: str | None          # FK to dim_cost_centers (NULL for Asset/Liability/Equity)
    debit_amount: float                 # debit value (0.00 if this is a credit line)
    credit_amount: float                # credit value (0.00 if this is a debit line)
    currency: str                       # ISO 4217: "ARS", "USD"
    description: str | None             # optional line-specific description
    created_at: datetime

@dataclass
class Budget:
    """Budgeted amount for a (account, cost_center, period) intersection.

    Only Revenue and Expense accounts are budgeted, since Asset/Liability/Equity
    accounts represent state rather than performance targets.
    Multiple versions can exist; is_active flags the current one.
    """
    budget_id: str                # "BUD000001"
    account_id: str               # FK to dim_accounts
    cost_center_id: str           # FK to dim_cost_centers (NOT NULL)
    period_id: str                # FK to dim_periods: "2024-03"
    budgeted_amount: float        # planned amount in `currency`
    currency: str                 # ISO 4217: typically "ARS"
    budget_version: str           # "v1_original", "v2_revised", etc.
    is_active: bool               # True for the currently active version
    created_at: datetime