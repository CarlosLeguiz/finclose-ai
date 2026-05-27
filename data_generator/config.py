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

# =======  ACCOUNT TYPE RANGES =======

ACCOUNT_TYPE_RANGES = { 
    "Asset":     (1000, 1999),
    "Liability": (2000, 2999),
    "Equity":    (3000, 3999),
    "Revenue":   (4000, 4999),
    "Expense":   (5000, 5999),
}

ACCOUNT_DISTRIBUTION = { 
    "Asset":     15,
    "Liability": 10,
    "Equity":     5,
    "Revenue":   15,
    "Expense":   35,
}

# ======= COST CENTERS  =======

COST_CENTERS = [ ## hardcoded for more realistic naming  
    # (code, name, department, manager_name)
    ("100", "Executive Office", "G&A", "Carlos Mendoza"),
    ("110", "Finance & Accounting", "G&A", "Laura Pereyra"),
    ("120", "Human Resources", "G&A", "Diego Romero"),
    ("130", "IT & Systems", "G&A", "Sofía Castro"),
    ("200", "Sales - Domestic", "Sales", "Martín Álvarez"),
    ("210", "Sales - Export", "Sales", "Andrea López"),
    ("300", "Marketing Digital", "Marketing", "Lucía Fernández"),
    ("310", "Marketing Traditional", "Marketing", None),
    ("400", "Production - Córdoba Plant", "Operations", "Roberto Silva"),
    ("410", "Production - Buenos Aires Plant", "Operations", "Mariana Torres"),
    ("420", "Logistics & Warehouse", "Operations", "Federico Ruiz"),
    ("430", "Quality Control", "Operations", None),
]