# Data Model — FinClose AI

This document describes the data model that powers the FinClose AI pipeline, designed to simulate and analyze the monthly financial close process of a mid-size manufacturing company (Acme Manufacturing).

## Overview

The model follows a **dimensional approach** with **conformed dimensions**, optimized for analytical queries and FP&A reporting. It consists of **7 tables**: 4 dimension tables and 3 fact tables.

![Data Model Diagram](./data_model.png)

## Design philosophy

The raw layer (these 7 tables) follows a **3NF-light** structure that simulates output from a typical ERP system. Later in the pipeline, dbt transforms these into denormalized marts optimized for analytics, dashboards, and AI-driven variance analysis.

Key design principles:

- **Surrogate keys** in dimensions (`account_id`, `cost_center_id`, etc.) ensure historical integrity when business codes change
- **Conformed dimensions** shared across fact tables enable unified analytical queries
- **Separated `debit_amount` / `credit_amount` columns** follow accounting conventions (avoiding signed amount semantics)
- **`DECIMAL` precision** for all financial amounts to prevent floating-point accumulation errors
- **Multi-currency support** via ISO 4217 codes and a dedicated exchange rates lookup table
- **Separation of concerns**: budgets and actuals live in separate fact tables, joined via dbt models

## Tables

### Dimension tables

#### `dim_accounts`
Chart of accounts. Self-referencing hierarchy.

| Column | Type | Notes |
|--------|------|-------|
| `account_id` | VARCHAR(20) PK | Surrogate key (immutable) |
| `account_code` | VARCHAR(20) UNIQUE | Business code (may change) |
| `account_name` | VARCHAR(200) | Account description |
| `account_type` | VARCHAR(20) | Asset / Liability / Equity / Revenue / Expense |
| `parent_account_id` | VARCHAR(20) FK | Self-reference for hierarchy |
| `is_active` | BOOLEAN | Currently usable |
| `created_at` | TIMESTAMP | Audit |

Estimated rows: ~80-120

#### `dim_cost_centers`
Organizational units (departments) used for spend analysis by area.

| Column | Type | Notes |
|--------|------|-------|
| `cost_center_id` | VARCHAR(20) PK | Surrogate key |
| `code` | VARCHAR(20) UNIQUE | Business code |
| `name` | VARCHAR(200) | Cost center name |
| `department` | VARCHAR(100) | Grouping (Operations, Marketing, Sales, G&A) |
| `manager_name` | VARCHAR(200) | Responsible person |
| `is_active` | BOOLEAN | Currently active |
| `created_at` | TIMESTAMP | Audit |

Estimated rows: ~10-15

#### `dim_periods`
Monthly accounting periods with closed/open status.

| Column | Type | Notes |
|--------|------|-------|
| `period_id` | VARCHAR(20) PK | Semantic key (e.g., "2026-01") |
| `year` | INTEGER | Year |
| `month` | INTEGER | Month 1-12 |
| `period_name` | VARCHAR(50) | Human readable (e.g., "January 2026") |
| `quarter` | INTEGER | Quarter 1-4 |
| `start_date` | DATE | First day of month |
| `end_date` | DATE | Last day of month |
| `is_closed` | BOOLEAN | Closed periods reject new entries |
| `closed_at` | TIMESTAMP | When the period was closed |

Estimated rows: ~36 (3 years of monthly periods)

#### `dim_exchange_rates`
Currency conversion lookup table (no direct FK to facts).

| Column | Type | Notes |
|--------|------|-------|
| `rate_id` | VARCHAR(20) PK | Unique ID |
| `from_currency` | VARCHAR(3) | ISO 4217 code |
| `to_currency` | VARCHAR(3) | ISO 4217 code |
| `rate_date` | DATE | Effective date |
| `rate` | DECIMAL(18,6) | Conversion rate (extra precision) |
| `source` | VARCHAR(50) | Origin (BCRA, BNA, etc.) |
| `created_at` | TIMESTAMP | Audit |

Estimated rows: ~108 (3 currencies × 36 monthly periods)

### Fact tables

#### `fact_journal_entries`
Journal entry headers — metadata for each accounting transaction.

| Column | Type | Notes |
|--------|------|-------|
| `je_id` | VARCHAR(20) PK | Unique entry ID |
| `period_id` | VARCHAR(20) FK → dim_periods | Assigned period |
| `entry_date` | DATE | Real document date |
| `description` | VARCHAR(500) | Entry description |
| `source_system` | VARCHAR(50) | ERP / Manual / Adjustment / Reversal |
| `created_by` | VARCHAR(100) | User who created the entry |
| `status` | VARCHAR(20) | Draft / Posted / Reversed |
| `created_at` | TIMESTAMP | Audit |
| `posted_at` | TIMESTAMP | When posted to the ledger |

Estimated rows: ~3,000-5,000

#### `fact_journal_lines`
Journal entry detail — the core fact table where monetary values live.

| Column | Type | Notes |
|--------|------|-------|
| `je_line_id` | VARCHAR(20) PK | Unique line ID |
| `je_id` | VARCHAR(20) FK → fact_journal_entries | Parent entry |
| `line_number` | INTEGER | Order within entry |
| `account_id` | VARCHAR(20) FK → dim_accounts | Account affected |
| `cost_center_id` | VARCHAR(20) FK → dim_cost_centers | NULL for Asset/Liability/Equity |
| `debit_amount` | DECIMAL(18,2) | Debit in original currency |
| `credit_amount` | DECIMAL(18,2) | Credit in original currency |
| `currency` | VARCHAR(3) | ISO 4217 |
| `description` | VARCHAR(500) | Optional line-level description |
| `created_at` | TIMESTAMP | Audit |

Estimated rows: ~15,000-25,000

**Business rule:** Per the double-entry principle, for any given `je_id`:

SUM(debit_amount) = SUM(credit_amount)

This will be enforced via a dbt test in Week 9.

#### `fact_budgets`
Budgeted amounts by account + cost center + period. Versioned.

| Column | Type | Notes |
|--------|------|-------|
| `budget_id` | VARCHAR(20) PK | Unique ID |
| `account_id` | VARCHAR(20) FK → dim_accounts | Budgeted account |
| `cost_center_id` | VARCHAR(20) FK → dim_cost_centers | Required (only Revenue/Expense budgeted) |
| `period_id` | VARCHAR(20) FK → dim_periods | Budgeted period |
| `budgeted_amount` | DECIMAL(18,2) | Budgeted value |
| `currency` | VARCHAR(3) | ISO 4217 |
| `budget_version` | VARCHAR(20) | v1, v2_revised, v3_forecast, etc. |
| `is_active` | BOOLEAN | Only one active version per combination |
| `created_at` | TIMESTAMP | Audit |

Estimated rows: ~5,400 (15 accounts × 10 cost centers × 36 periods)

## Relationships

fact_journal_lines    →    fact_journal_entries  (each line belongs to one entry)
fact_journal_lines    →    dim_accounts          (account affected)
fact_journal_lines    →    dim_cost_centers      (cost center, nullable)
fact_journal_entries  →    dim_periods           (assigned period)
fact_budgets          →    dim_accounts
fact_budgets          →    dim_cost_centers
fact_budgets          →    dim_periods
dim_accounts          →    dim_accounts          (self-reference: parent_account_id)
dim_exchange_rates    →    (no FK; lookup table joined by currency + date)


## Business rules enforced

| # | Rule | Enforcement |
|---|------|-------------|
| 1 | Debits = Credits per entry | dbt test (Week 9) |
| 2 | `account_type` ∈ {Asset, Liability, Equity, Revenue, Expense} | dbt test + CHECK constraint |
| 3 | `status` ∈ {Draft, Posted, Reversed} | dbt test + CHECK constraint |
| 4 | `source_system` ∈ {ERP, Manual, Adjustment, Reversal} | dbt test + CHECK constraint |
| 5 | Only one active budget version per (account, cost_center, period) | UNIQUE index + dbt test |
| 6 | Asset/Liability/Equity lines must have `cost_center_id` NULL | dbt test |
| 7 | Revenue/Expense lines must have `cost_center_id` NOT NULL | dbt test |
| 8 | Closed periods cannot accept new entries | Application logic + dbt test |

## Source files

- **`data_model.dbml`** — DBML source code (used by dbdiagram.io)
- **`data_model.png`** — Rendered diagram (this image)

To regenerate the diagram, paste `data_model.dbml` into [dbdiagram.io](https://dbdiagram.io/d).

## Future evolution

This raw layer feeds the dbt pipeline in Weeks 5-9:

- **Staging models** (`stg_*`) — 1:1 with raw tables, with light cleanup and type casting
- **Intermediate models** (`int_*`) — Business logic, joins, reusable calculations
- **Mart models** (`mart_*`) — Final dimensional tables (e.g., `mart_pnl_monthly`, `mart_variance_analysis`)

Marts will denormalize for analytical performance and serve as the source for the Streamlit dashboard (Week 11) and the LangChain-powered AI variance analysis agent (Weeks 12-14).