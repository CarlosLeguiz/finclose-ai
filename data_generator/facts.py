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
)
from data_generator.schemas import Period, JournalEntry


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