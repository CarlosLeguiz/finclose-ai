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


# ======= EXCHANGE RATES =======

# Currency pairs to generate rates for (from_currency, to_currency)
CURRENCY_PAIRS = [
    ("USD", "ARS"),
    ("EUR", "ARS"),
]

# Historical anchor rates for USD/ARS (real BCRA data + projections)
# Format: {(year, month): rate}
USD_ARS_ANCHORS = {
    (2024, 1): 820.0,
    (2024, 6): 910.0,
    (2024, 12): 1020.0,
    (2025, 6): 1150.0,
    (2025, 12): 1280.0,
    (2026, 5): 1380.0,
    (2026, 12): 1500.0,   # year-end projection
}

# EUR/ARS = USD/ARS * EUR/USD ratio (~1.08 average)
#For multi-currency modeling, I anchored to USD/ARS (the primary reference for Argentine accounting) and derived EUR/ARS from the USD/EUR cross-rate. This is the standard approach in BCRA reporting.
EUR_USD_RATIO = 1.08 

# Source label for the rates
EXCHANGE_RATE_SOURCE = "BCRA"

# Volatility: monthly random variation around the interpolated rate
RATE_MONTHLY_VOLATILITY = 0.02  # ±2% noise

# ======= JOURNAL ENTRIES =======

# Distribution of entry statuses (must sum to 1.0)
STATUS_DISTRIBUTION = {
    "Posted":   0.95,
    "Draft":    0.03,
    "Reversed": 0.02,
}

# Distribution of source systems
SOURCE_SYSTEM_DISTRIBUTION = {
    "ERP":        0.80,
    "Manual":     0.15,
    "Adjustment": 0.05,
}

# Realistic description templates (Spanish)
ENTRY_DESCRIPTIONS = [
    "Pago a proveedores - {month_name}",
    "Facturación de ventas - {month_name}",
    "Cobranza de clientes - {month_name}",
    "Pago de honorarios profesionales",
    "Liquidación de sueldos - {month_name}",
    "Pago de servicios públicos",
    "Reclasificación contable",
    "Ajuste de inventario",
    "Provisión de gastos - {month_name}",
    "Depreciación mensual de bienes de uso",
    "Pago de impuestos - {month_name}",
    "Compra de mercaderías",
    "Reintegro de gastos",
    "Devengamiento de intereses",
    "Pago de alquiler - {month_name}",
    "Compra de insumos",
    "Pago de comisiones bancarias",
    "Reembolso de gastos a empleados",
    "Ajuste de cierre - {month_name}",
    "Revaluación de tipo de cambio",
]

# Users that load entries into the system
USERS = [
    "ana.gomez",
    "carlos.diaz",
    "lucia.fernandez",
    "diego.romero",
    "automated_erp",
    "system_batch",
]

# ======= JOURNAL LINES =======

# Number of lines per journal entry (uniform random in this range)
LINES_PER_ENTRY_MIN = 2
LINES_PER_ENTRY_MAX = 5

# Monetary amount range per debit line (ARS)
LINE_AMOUNT_MIN = 1000
LINE_AMOUNT_MAX = 500000

# Currency distribution for journal lines
CURRENCY_DISTRIBUTION = {
    "ARS": 0.85,
    "USD": 0.15,
}

# Account type weights for debit lines
# (most debits are Expense, some Asset)
DEBIT_ACCOUNT_TYPE_WEIGHTS = {
    "Expense": 0.70,
    "Asset":   0.30,
}

# Account type weights for credit lines (the balancing line)
# (most credits go to Asset:Caja/Banco or Liability)
CREDIT_ACCOUNT_TYPE_WEIGHTS = {
    "Asset":     0.60,
    "Liability": 0.30,
    "Revenue":   0.10,
}

# ======= BUDGETS =======

# How many cost centers each budgetable account is allocated to
# (not all accounts apply to all centers — realism)
CENTERS_PER_BUDGETED_ACCOUNT_MIN = 2
CENTERS_PER_BUDGETED_ACCOUNT_MAX = 5

# Monthly budgeted amount range (ARS)
BUDGET_AMOUNT_MIN = 50000
BUDGET_AMOUNT_MAX = 800000

# Budget version label (single active version for simplicity)
BUDGET_VERSION = "v1_original"

# Currency for budgets (most companies budget in local currency)
BUDGET_CURRENCY = "ARS"