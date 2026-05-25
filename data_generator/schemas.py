"""
Data class definitions for the 7 tables in FinClose AI.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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
    parent_account_id: Optional[str]
    is_active: bool
    created_at: datetime