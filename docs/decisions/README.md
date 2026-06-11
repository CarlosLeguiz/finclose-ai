# FinClose AI

**Automated Financial Close & Variance Analysis Platform**

End-to-end data pipeline that automates the monthly financial close process and generates AI-powered executive variance analysis.

## The Problem

Finance teams at mid-size companies spend 3-5 days each month manually:
- Reconciling accounts and journal entries
- Calculating budget vs. actual variances
- Writing executive commentary on those variances
- Producing financial reports in Excel

This process is slow, error-prone, and pulls senior finance analysts away from higher-value work.

## The Solution

FinClose AI automates the entire workflow:

1. **Ingests** journal entries, budgets, and chart of accounts data
2. **Transforms** raw accounting data into dimensional models (fact tables, dimensions)
3. **Calculates** P&L statements and budget variances automatically
4. **Generates** executive-level variance commentary using AI
5. **Visualizes** results in an interactive dashboard

The goal: reduce a 3-5 day manual close to a 30-minute automated process.

## Architecture

The pipeline follows a modern modular data stack:

**1. Ingestion Layer** — Python scripts using Faker generate realistic synthetic accounting data (journal entries, budgets, chart of accounts).

**2. Storage Layer** — DuckDB serves as the analytical warehouse during development (zero cost, embedded). Snowflake is used in week 16 for cloud validation.

**3. Transformation Layer** — dbt models data in three layers: `staging` (raw cleaned), `intermediate` (business logic), and `marts` (final tables for consumption). Includes automated tests and documentation.

**4. Orchestration Layer** — Apache Airflow schedules and orchestrates the entire pipeline with daily runs.

**5. Consumption Layer** — Two parallel outputs:
   - **Streamlit dashboard** for interactive exploration of P&L, variances, and trends
   - **LangChain + Anthropic Claude** agent that generates executive-level variance commentary in natural language

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.10 |
| **Dependency Management** | Poetry |
| **Data Generation** | Faker |
| **Warehouse (dev)** | DuckDB |
| **Warehouse (validation)** | Snowflake |
| **Transformation** | dbt (dbt-duckdb, dbt-snowflake) |
| **Orchestration** | Apache Airflow |
| **Dashboard** | Streamlit |
| **AI Layer** | LangChain + Anthropic Claude |
| **Containerization** | Docker |
| **Environment** | WSL2 / Ubuntu 22.04 |

---

## Data Model

The pipeline operates on a dimensional data model with 7 tables (4 dimensions + 3 facts) designed to represent the accounting reality of a mid-size manufacturing company.

![Data Model](./docs/data_model.png)

See [`docs/data_model.md`](./docs/data_model.md) for full details, including column definitions, business rules, and design rationale.

---

## Data Pipeline (dbt)

The transformation layer is built with dbt, following a 3-layer architecture: **staging → intermediate → marts**. The full lineage graph below shows how raw tables flow through staging models, business logic in intermediate models, and finally into dimension and fact tables ready for consumption.

![dbt DAG](./docs/dbt_dag_full.png)

### Pipeline metrics

| Metric | Value |
|--------|-------|
| Total dbt models | 14 |
| Staging models | 7 |
| Intermediate models | 2 |
| Mart models | 5 (3 dimensions + 2 facts) |
| Data tests | 92 (89 generic + 3 singular business rule tests) |
| Synthetic rows processed | 23,159 |

### Key design decisions

- **Materializations:** staging and intermediate as `view` (always fresh, no storage cost); marts as `table` (fast consumption for dashboards).
- **Double-entry integrity:** preserved end-to-end through aggregations and validated with a singular test (`assert_journal_entries_balanced`).
- **FULL OUTER JOIN** in `fct_budget_vs_actual` to preserve unbudgeted actuals and unused budgets — both critical for FP&A variance analysis.
- **Derived analytical columns** in dim tables (`normal_balance`, `is_balance_sheet`, `department_group`, `signed_amount`) that encode accounting domain knowledge once and let downstream consumers reuse it.

---

## Project Roadmap (16 weeks)

- [x] **Week 1:** Environment setup and project scaffolding
- [x] **Week 2:** Accounting data model design (7 core tables)
- [x] **Weeks 3-4:** Synthetic data generation with Python + Faker
- [x] **Weeks 5-7:** dbt staging and intermediate models
- [x] **Weeks 8-9:** dbt marts and data quality tests
- [ ] **Weeks 10-11:** Airflow DAGs and Streamlit dashboard
- [ ] **Weeks 12-14:** LangChain-based AI variance analysis agent
- [ ] **Weeks 15-16:** Documentation, deploy, and Snowflake validation

---

## Getting Started

> Project under active development. Setup instructions will be completed as the project progresses.

### Prerequisites
- Linux / macOS / WSL2 (Ubuntu 22.04)
- Python 3.10+
- Poetry
- Docker (for Airflow)

### Quick start
```bash