"""
Configuration constants for FinClose AI data generation.
"""

from datetime import date

# =======  COMPANY CONFIGURATION =======
COMPANY_NAME = "Acme Manufacturing"
HOME_CURRENCY = "ARS"
REPORTING_CURRENCIES = ["USD", "EUR", "BRL"]


# =======  TIME RANGE =======

START_YEAR = 2024
END_YEAR = 2026
NUM_PERIODS = (END_YEAR - START_YEAR + 1) * 12  # 36 monthly periods

# =======  DATA VOLUMES =======

NUM_ACCOUNTS = 80
NUM_COST_CENTERS = 12
NUM_JOURNAL_ENTRIES_PER_MONTH = 100
AVG_LINES_PER_ENTRY = 4

# =======  FAKER CONFIGURATION =======

FAKER_LOCALE = "es_AR"
RANDOM_SEED = 42