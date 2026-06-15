"""Unit tests for data_generator.dimensions module."""

import pytest

from data_generator.dimensions import generate_accounts
from data_generator.config import ACCOUNT_DISTRIBUTION, ACCOUNT_TYPE_RANGES


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def accounts():
    """Generate the default set of accounts once per test that needs it.

    Using a fixture avoids regenerating accounts in every test, which keeps
    the test suite fast and ensures all tests work with the same data.
    """
    return generate_accounts()


# =============================================================================
# Tests for generate_accounts()
# =============================================================================

class TestGenerateAccounts:
    """Tests for the generate_accounts function."""

    def test_returns_correct_total_count(self, accounts):
        """The total number of accounts must match ACCOUNT_DISTRIBUTION sum."""
        expected_total = sum(ACCOUNT_DISTRIBUTION.values())
        assert len(accounts) == expected_total

    def test_returns_correct_count_per_type(self, accounts):
        """Each account_type must have exactly the count from ACCOUNT_DISTRIBUTION."""
        for account_type, expected_count in ACCOUNT_DISTRIBUTION.items():
            actual_count = sum(1 for a in accounts if a.account_type == account_type)
            assert actual_count == expected_count, (
                f"Expected {expected_count} accounts for type {account_type}, "
                f"got {actual_count}"
            )

    def test_account_ids_are_unique(self, accounts):
        """No two accounts may share the same account_id."""
        ids = [a.account_id for a in accounts]
        assert len(ids) == len(set(ids))

    def test_account_codes_are_unique(self, accounts):
        """No two accounts may share the same account_code."""
        codes = [a.account_code for a in accounts]
        assert len(codes) == len(set(codes))

    def test_account_id_format(self, accounts):
        """Account IDs must follow the pattern ACCnnn (3-digit zero-padded)."""
        for a in accounts:
            assert a.account_id.startswith("ACC"), f"Bad prefix: {a.account_id}"
            assert len(a.account_id) == 6, f"Bad length: {a.account_id}"
            numeric_part = a.account_id[3:]
            assert numeric_part.isdigit(), f"Non-numeric suffix: {a.account_id}"

    def test_account_codes_within_type_ranges(self, accounts):
        """Each account code must fall within the range defined for its type."""
        for a in accounts:
            min_code, max_code = ACCOUNT_TYPE_RANGES[a.account_type]
            code_int = int(a.account_code)
            assert min_code <= code_int <= max_code, (
                f"Account {a.account_id} ({a.account_type}) has code {code_int}, "
                f"expected in range [{min_code}, {max_code}]"
            )

    def test_no_null_names(self, accounts):
        """All accounts must have a non-empty name."""
        for a in accounts:
            assert a.account_name is not None
            assert len(a.account_name.strip()) > 0

    def test_account_type_is_valid(self, accounts):
        """account_type must be one of the 5 valid values."""
        valid_types = {"Asset", "Liability", "Equity", "Revenue", "Expense"}
        for a in accounts:
            assert a.account_type in valid_types, (
                f"Invalid account_type: {a.account_type}"
            )

    def test_all_accounts_are_active_by_default(self, accounts):
        """Generated accounts default to is_active=True."""
        for a in accounts:
            assert a.is_active is True

    def test_no_parent_account_id_by_default(self, accounts):
        """Generated accounts have no parent (flat structure by default)."""
        for a in accounts:
            assert a.parent_account_id is None

# =============================================================================
# Tests for generate_periods()
# =============================================================================

from data_generator.dimensions import generate_periods, generate_cost_centers
from data_generator.config import START_YEAR, END_YEAR


@pytest.fixture
def periods():
    """Generate the default set of periods."""
    return generate_periods()


class TestGeneratePeriods:
    """Tests for generate_periods function."""

    def test_total_count_matches_years_times_months(self, periods):
        """Should generate one period per month between START_YEAR and END_YEAR."""
        expected = (END_YEAR - START_YEAR + 1) * 12
        assert len(periods) == expected

    def test_period_ids_are_unique(self, periods):
        """No two periods share the same period_id."""
        ids = [p.period_id for p in periods]
        assert len(ids) == len(set(ids))

    def test_period_id_format(self, periods):
        """Period IDs must follow YYYY-MM format."""
        for p in periods:
            assert len(p.period_id) == 7
            assert p.period_id[4] == "-"
            year_part, month_part = p.period_id.split("-")
            assert year_part.isdigit() and month_part.isdigit()
            assert 1 <= int(month_part) <= 12

    def test_year_and_month_consistent_with_id(self, periods):
        """The year/month columns must match the period_id."""
        for p in periods:
            year_str, month_str = p.period_id.split("-")
            assert p.year == int(year_str)
            assert p.month == int(month_str)

    def test_quarter_is_correct(self, periods):
        """quarter must be derived correctly from month (Q1=1-3, Q2=4-6, etc.)."""
        for p in periods:
            expected_quarter = (p.month - 1) // 3 + 1
            assert p.quarter == expected_quarter

    def test_start_date_is_first_of_month(self, periods):
        """start_date.day must always be 1."""
        for p in periods:
            assert p.start_date.day == 1

    def test_end_date_after_start_date(self, periods):
        """end_date must come after start_date."""
        for p in periods:
            assert p.end_date >= p.start_date

    def test_years_within_configured_range(self, periods):
        """All years must be between START_YEAR and END_YEAR (inclusive)."""
        for p in periods:
            assert START_YEAR <= p.year <= END_YEAR


# =============================================================================
# Tests for generate_cost_centers()
# =============================================================================

@pytest.fixture
def cost_centers():
    """Generate the default set of cost centers."""
    return generate_cost_centers()


class TestGenerateCostCenters:
    """Tests for generate_cost_centers function."""

    def test_returns_non_empty_list(self, cost_centers):
        """Must produce at least one cost center."""
        assert len(cost_centers) > 0

    def test_cost_center_ids_are_unique(self, cost_centers):
        """No two cost centers share the same cost_center_id."""
        ids = [cc.cost_center_id for cc in cost_centers]
        assert len(ids) == len(set(ids))

    def test_cost_center_id_format(self, cost_centers):
        """Cost center IDs must follow CCnnn format."""
        for cc in cost_centers:
            assert cc.cost_center_id.startswith("CC")
            assert len(cc.cost_center_id) == 5

    def test_codes_are_unique(self, cost_centers):
        """No two cost centers share the same code."""
        codes = [cc.code for cc in cost_centers]
        assert len(codes) == len(set(codes))

    def test_names_are_not_empty(self, cost_centers):
        """All cost centers must have a non-empty name."""
        for cc in cost_centers:
            assert cc.name is not None
            assert len(cc.name.strip()) > 0

    def test_departments_are_not_empty(self, cost_centers):
        """All cost centers must belong to a department."""
        for cc in cost_centers:
            assert cc.department is not None
            assert len(cc.department.strip()) > 0

    def test_all_active_by_default(self, cost_centers):
        """Generated cost centers default to is_active=True."""
        for cc in cost_centers:
            assert cc.is_active is True


# =============================================================================
# Tests for generate_exchange_rates()
# =============================================================================

from data_generator.dimensions import generate_exchange_rates


@pytest.fixture
def exchange_rates():
    """Generate the default set of exchange rates."""
    return generate_exchange_rates()


class TestGenerateExchangeRates:
    """Tests for generate_exchange_rates function."""

    def test_returns_non_empty(self, exchange_rates):
        """Must produce at least one exchange rate."""
        assert len(exchange_rates) > 0

    def test_rate_ids_are_unique(self, exchange_rates):
        """All rate IDs must be unique."""
        ids = [r.rate_id for r in exchange_rates]
        assert len(ids) == len(set(ids))

    def test_rate_id_format(self, exchange_rates):
        """Rate IDs must follow RATEnnnn format."""
        for r in exchange_rates:
            assert r.rate_id.startswith("RATE")

    def test_currencies_are_iso_codes(self, exchange_rates):
        """from_currency and to_currency must be 3-letter ISO codes."""
        for r in exchange_rates:
            assert len(r.from_currency) == 3
            assert len(r.to_currency) == 3
            assert r.from_currency.isupper()
            assert r.to_currency.isupper()

    def test_from_and_to_currency_differ(self, exchange_rates):
        """Conversion rate must be between two different currencies."""
        for r in exchange_rates:
            assert r.from_currency != r.to_currency

    def test_rates_are_positive(self, exchange_rates):
        """Exchange rates must always be positive numbers."""
        for r in exchange_rates:
            assert r.rate > 0

    def test_source_is_not_empty(self, exchange_rates):
        """Every rate must have a source attributed."""
        for r in exchange_rates:
            assert r.source is not None
            assert len(r.source.strip()) > 0