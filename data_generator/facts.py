"""
Generators for the 3 fact tables (journal entries, journal lines, budgets).
"""

import random
from datetime import datetime, date, timedelta

from data_generator.config import (
    NUM_JOURNAL_ENTRIES_PER_MONTH,
    RANDOM_SEED,
    STATUS_DISTRIBUTION,
    SOURCE_SYSTEM_DISTRIBUTION,
    ENTRY_DESCRIPTIONS,
    USERS,
    LINES_PER_ENTRY_MIN,
    LINES_PER_ENTRY_MAX,
    LINE_AMOUNT_MIN,
    LINE_AMOUNT_MAX,
    CURRENCY_DISTRIBUTION,
    DEBIT_ACCOUNT_TYPE_WEIGHTS,
    CREDIT_ACCOUNT_TYPE_WEIGHTS,
    CENTERS_PER_BUDGETED_ACCOUNT_MIN,
    CENTERS_PER_BUDGETED_ACCOUNT_MAX,
    BUDGET_AMOUNT_MIN,
    BUDGET_AMOUNT_MAX,
    BUDGET_VERSION,
    BUDGET_CURRENCY,
)
from data_generator.schemas import (
    Period,
    JournalEntry,
    JournalLine,
    Account,
    CostCenter,
    Budget,
)


def _weighted_choice(distribution: dict) -> str:
    """Pick a random key from a dict based on its probability weights.

    Example:
        distribution = {"Posted": 0.95, "Draft": 0.05}
        Returns "Posted" ~95% of the time.

    Args:
        distribution: dict mapping value → probability (must sum to 1.0)

    Returns:
        One of the keys, chosen randomly with respect to weights.
    """
    keys = list(distribution.keys())
    weights = list(distribution.values())
    return random.choices(keys, weights=weights, k=1)[0]


def generate_journal_entries(periods: list[Period]) -> list[JournalEntry]:
    """Generate journal entry header records for the given periods.

    For each period, creates approximately NUM_JOURNAL_ENTRIES_PER_MONTH entries
    with realistic distributions of status, source system, and descriptions.

    Args:
        periods: list of Period instances (from generate_periods()).

    Returns:
        List of JournalEntry instances ready to be loaded into fact_journal_entries.
    """
    random.seed(RANDOM_SEED)

    entries = []
    je_counter = 1

    for period in periods:
        for _ in range(NUM_JOURNAL_ENTRIES_PER_MONTH):
            # Random day within the period
            days_in_period = (period.end_date - period.start_date).days
            random_day_offset = random.randint(0, days_in_period)
            entry_date = period.start_date + timedelta(days=random_day_offset)

            # Status and source system from weighted distributions
            status = _weighted_choice(STATUS_DISTRIBUTION)
            source_system = _weighted_choice(SOURCE_SYSTEM_DISTRIBUTION)

            # Description (some templates have {month_name} placeholder)
            description_template = random.choice(ENTRY_DESCRIPTIONS)
            month_name = period.start_date.strftime("%B")
            description = description_template.format(month_name=month_name)

            # User (humans more likely for Manual, automated for ERP)
            created_by = random.choice(USERS)

            # posted_at only if Posted
            posted_at = datetime.now() if status == "Posted" else None

            entry = JournalEntry(
                je_id=f"JE{je_counter:06d}",
                period_id=period.period_id,
                entry_date=entry_date,
                description=description,
                source_system=source_system,
                created_by=created_by,
                status=status,
                created_at=datetime.now(),
                posted_at=posted_at,
            )
            entries.append(entry)
            je_counter += 1

    return entries

def _pick_account_by_type(accounts: list, type_weights: dict) -> "Account":
    """Pick a random account whose type matches the weighted distribution.

    Args:
        accounts: list of Account instances.
        type_weights: dict mapping account_type → probability weight.

    Returns:
        One Account instance randomly chosen, respecting type weights.
    """
    # First pick the type (weighted)
    chosen_type = _weighted_choice(type_weights)

    # Then pick a random account of that type
    candidates = [acc for acc in accounts if acc.account_type == chosen_type]
    return random.choice(candidates)


def generate_journal_lines(
    journal_entries: list[JournalEntry],
    accounts: list,
    cost_centers: list,
) -> list[JournalLine]:
    """Generate journal line records for the given journal entries.

    For each entry, creates 2-5 lines following double-entry bookkeeping:
    the sum of debits equals the sum of credits. The last line is calculated
    to cancel the running balance.

    Args:
        journal_entries: list of JournalEntry instances (parent entries).
        accounts: list of Account instances (for FK lookups).
        cost_centers: list of CostCenter instances (for cost center assignment).

    Returns:
        List of JournalLine instances ready to be loaded into fact_journal_lines.
    """
    random.seed(RANDOM_SEED)

    lines = []
    line_counter = 1

    for entry in journal_entries:
        # 1. Decide how many lines this entry will have
        num_lines = random.randint(LINES_PER_ENTRY_MIN, LINES_PER_ENTRY_MAX)

        # 2. Pick one currency for the whole entry (mixed currencies per entry is rare)
        currency = _weighted_choice(CURRENCY_DISTRIBUTION)

        # 3. Generate (N-1) debit lines, track total
        total_debits = 0.0
        for line_num in range(1, num_lines):
            debit_account = _pick_account_by_type(accounts, DEBIT_ACCOUNT_TYPE_WEIGHTS)

            # cost_center is required for Revenue/Expense, NULL otherwise
            if debit_account.account_type in ("Revenue", "Expense"):
                cost_center_id = random.choice(cost_centers).cost_center_id
            else:
                cost_center_id = None

            amount = round(random.uniform(LINE_AMOUNT_MIN, LINE_AMOUNT_MAX), 2)

            line = JournalLine(
                je_line_id=f"JEL{line_counter:07d}",
                je_id=entry.je_id,
                line_number=line_num,
                account_id=debit_account.account_id,
                cost_center_id=cost_center_id,
                debit_amount=amount,
                credit_amount=0.0,
                currency=currency,
                description=None,
                created_at=datetime.now(),
            )
            lines.append(line)
            total_debits += amount
            line_counter += 1

        # 4. Final balancing credit line
        credit_account = _pick_account_by_type(accounts, CREDIT_ACCOUNT_TYPE_WEIGHTS)

        if credit_account.account_type in ("Revenue", "Expense"):
            cost_center_id = random.choice(cost_centers).cost_center_id
        else:
            cost_center_id = None

        credit_line = JournalLine(
            je_line_id=f"JEL{line_counter:07d}",
            je_id=entry.je_id,
            line_number=num_lines,
            account_id=credit_account.account_id,
            cost_center_id=cost_center_id,
            debit_amount=0.0,
            credit_amount=round(total_debits, 2),
            currency=currency,
            description=None,
            created_at=datetime.now(),
        )
        lines.append(credit_line)
        line_counter += 1

    return lines

def generate_budgets(
    accounts: list,
    cost_centers: list,
    periods: list,
) -> list:
    """Generate budget records for the (account, cost_center, period) grid.

    Only Revenue and Expense accounts are budgeted. Each budgetable account
    is allocated to a random subset of cost centers (not all centers budget
    every account). One row per (account, cost_center, period) combination.

    Args:
        accounts: list of Account instances.
        cost_centers: list of CostCenter instances.
        periods: list of Period instances.

    Returns:
        List of Budget instances ready to be loaded into fact_budgets.
    """
    random.seed(RANDOM_SEED)

    budgets = []
    budget_counter = 1

    # 1. Filter budgetable accounts (only Revenue and Expense)
    budgetable_accounts = [
        acc for acc in accounts
        if acc.account_type in ("Revenue", "Expense")
    ]

    # 2. For each budgetable account, decide which cost centers it applies to
    for account in budgetable_accounts:
        num_centers = random.randint(
            CENTERS_PER_BUDGETED_ACCOUNT_MIN,
            CENTERS_PER_BUDGETED_ACCOUNT_MAX,
        )
        assigned_centers = random.sample(cost_centers, num_centers)

        # 3. For each assigned center, generate a budget per period
        for center in assigned_centers:
            for period in periods:
                amount = round(
                    random.uniform(BUDGET_AMOUNT_MIN, BUDGET_AMOUNT_MAX),
                    2,
                )

                budget = Budget(
                    budget_id=f"BUD{budget_counter:06d}",
                    account_id=account.account_id,
                    cost_center_id=center.cost_center_id,
                    period_id=period.period_id,
                    budgeted_amount=amount,
                    currency=BUDGET_CURRENCY,
                    budget_version=BUDGET_VERSION,
                    is_active=True,
                    created_at=datetime.now(),
                )
                budgets.append(budget)
                budget_counter += 1

    return budgets