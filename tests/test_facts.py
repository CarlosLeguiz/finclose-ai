"""Unit tests for data_generator.facts module."""

import pytest
from collections import defaultdict

from data_generator.dimensions import (
    generate_accounts,
    generate_cost_centers,
    generate_periods,
)
from data_generator.facts import (
    generate_journal_entries,
    generate_journal_lines,
    generate_budgets,
)
from data_generator.config import (
    NUM_JOURNAL_ENTRIES_PER_MONTH,
    LINES_PER_ENTRY_MIN,
    LINES_PER_ENTRY_MAX,
)


# =============================================================================
# Shared fixtures (used across multiple test classes)
# =============================================================================

@pytest.fixture(scope="module")
def accounts():
    """Generate accounts once per module, not per test (faster)."""
    return generate_accounts()


@pytest.fixture(scope="module")
def cost_centers():
    """Generate cost centers once per module."""
    return generate_cost_centers()


@pytest.fixture(scope="module")
def periods():
    """Generate periods once per module."""
    return generate_periods()


@pytest.fixture(scope="module")
def journal_entries(periods):
    """Generate journal entries once per module."""
    return generate_journal_entries(periods)


@pytest.fixture(scope="module")
def journal_lines(journal_entries, accounts, cost_centers):
    """Generate journal lines once per module."""
    return generate_journal_lines(journal_entries, accounts, cost_centers)


@pytest.fixture(scope="module")
def budgets(accounts, cost_centers, periods):
    """Generate budgets once per module."""
    return generate_budgets(accounts, cost_centers, periods)


# =============================================================================
# Tests for generate_journal_entries()
# =============================================================================

class TestGenerateJournalEntries:
    """Tests for the generate_journal_entries function."""

    def test_correct_count_per_period(self, journal_entries, periods):
        """Should generate NUM_JOURNAL_ENTRIES_PER_MONTH entries per period."""
        expected_total = NUM_JOURNAL_ENTRIES_PER_MONTH * len(periods)
        assert len(journal_entries) == expected_total

    def test_je_ids_are_unique(self, journal_entries):
        """All journal entry IDs must be unique."""
        ids = [je.je_id for je in journal_entries]
        assert len(ids) == len(set(ids))

    def test_je_id_format(self, journal_entries):
        """Journal entry IDs must follow JE###### format."""
        for je in journal_entries:
            assert je.je_id.startswith("JE")
            assert len(je.je_id) == 8
            assert je.je_id[2:].isdigit()

    def test_status_is_valid(self, journal_entries):
        """Status must be Posted, Draft, or Reversed."""
        valid_statuses = {"Posted", "Draft", "Reversed"}
        for je in journal_entries:
            assert je.status in valid_statuses

    def test_source_system_is_valid(self, journal_entries):
        """Source system must be one of the configured values."""
        valid_sources = {"ERP", "Manual", "Adjustment"}
        for je in journal_entries:
            assert je.source_system in valid_sources

    def test_entry_date_within_period(self, journal_entries, periods):
        """entry_date must fall within its assigned period's start/end dates."""
        period_lookup = {p.period_id: p for p in periods}
        for je in journal_entries:
            p = period_lookup[je.period_id]
            assert p.start_date <= je.entry_date <= p.end_date

    def test_posted_entries_have_posted_at(self, journal_entries):
        """Only Posted entries should have posted_at; others should be None."""
        for je in journal_entries:
            if je.status == "Posted":
                assert je.posted_at is not None
            else:
                assert je.posted_at is None


# =============================================================================
# Tests for generate_journal_lines() — THE MOST CRITICAL TESTS
# =============================================================================

class TestGenerateJournalLines:
    """Tests for the generate_journal_lines function.

    These are the most critical tests in the suite because they verify
    the double-entry bookkeeping principle, which is the foundation
    of accounting integrity.
    """

    def test_total_lines_within_expected_range(
        self, journal_lines, journal_entries
    ):
        """Total lines should be between (entries * MIN) and (entries * MAX)."""
        num_entries = len(journal_entries)
        min_expected = num_entries * LINES_PER_ENTRY_MIN
        max_expected = num_entries * LINES_PER_ENTRY_MAX
        assert min_expected <= len(journal_lines) <= max_expected

    def test_je_line_ids_are_unique(self, journal_lines):
        """All journal line IDs must be unique."""
        ids = [jl.je_line_id for jl in journal_lines]
        assert len(ids) == len(set(ids))

    def test_every_line_belongs_to_an_entry(
        self, journal_lines, journal_entries
    ):
        """Every line's je_id must reference an existing journal entry."""
        valid_je_ids = {je.je_id for je in journal_entries}
        for jl in journal_lines:
            assert jl.je_id in valid_je_ids

    def test_double_entry_balanced(self, journal_lines):
        """For every journal entry, sum(debits) must equal sum(credits).

        This is the foundational accounting invariant: every transaction
        must balance. Violating this would invalidate the entire dataset.
        """
        debits_by_entry = defaultdict(float)
        credits_by_entry = defaultdict(float)

        for jl in journal_lines:
            debits_by_entry[jl.je_id] += jl.debit_amount
            credits_by_entry[jl.je_id] += jl.credit_amount

        for je_id in debits_by_entry:
            total_debit = round(debits_by_entry[je_id], 2)
            total_credit = round(credits_by_entry[je_id], 2)
            assert total_debit == total_credit, (
                f"Entry {je_id} unbalanced: "
                f"debits={total_debit}, credits={total_credit}"
            )

    def test_line_has_either_debit_or_credit_not_both(self, journal_lines):
        """Each line must have ONE of debit/credit > 0, not both."""
        for jl in journal_lines:
            has_debit = jl.debit_amount > 0
            has_credit = jl.credit_amount > 0
            assert has_debit != has_credit, (
                f"Line {jl.je_line_id} has both/neither debit and credit"
            )

    def test_cost_center_required_for_revenue_expense(
        self, journal_lines, accounts
    ):
        """Revenue and Expense accounts must have a cost_center_id."""
        account_type_lookup = {a.account_id: a.account_type for a in accounts}
        for jl in journal_lines:
            account_type = account_type_lookup[jl.account_id]
            if account_type in ("Revenue", "Expense"):
                assert jl.cost_center_id is not None, (
                    f"Line {jl.je_line_id} for {account_type} account "
                    f"is missing cost_center_id"
                )

    def test_cost_center_null_for_balance_sheet(
        self, journal_lines, accounts
    ):
        """Asset, Liability, and Equity accounts must NOT have a cost_center_id."""
        account_type_lookup = {a.account_id: a.account_type for a in accounts}
        for jl in journal_lines:
            account_type = account_type_lookup[jl.account_id]
            if account_type in ("Asset", "Liability", "Equity"):
                assert jl.cost_center_id is None, (
                    f"Line {jl.je_line_id} for {account_type} account "
                    f"should have NULL cost_center_id"
                )


# =============================================================================
# Tests for generate_budgets()
# =============================================================================

class TestGenerateBudgets:
    """Tests for the generate_budgets function."""

    def test_budget_ids_are_unique(self, budgets):
        """All budget IDs must be unique."""
        ids = [b.budget_id for b in budgets]
        assert len(ids) == len(set(ids))

    def test_only_revenue_and_expense_accounts(self, budgets, accounts):
        """Budgets should only exist for Revenue and Expense accounts."""
        account_type_lookup = {a.account_id: a.account_type for a in accounts}
        for b in budgets:
            account_type = account_type_lookup[b.account_id]
            assert account_type in ("Revenue", "Expense"), (
                f"Budget {b.budget_id} references {account_type} account "
                f"(should only be Revenue/Expense)"
            )

    def test_all_budgets_have_positive_amounts(self, budgets):
        """Budgeted amounts must be positive (zero or negative makes no sense)."""
        for b in budgets:
            assert b.budgeted_amount > 0

    def test_all_budgets_have_cost_center(self, budgets):
        """Every budget row must have a cost_center_id (Revenue/Expense require it)."""
        for b in budgets:
            assert b.cost_center_id is not None

    def test_all_budgets_are_active(self, budgets):
        """All generated budgets default to is_active=True."""
        for b in budgets:
            assert b.is_active is True