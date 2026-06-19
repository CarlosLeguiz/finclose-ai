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

**2. Storage Layer** — DuckDB serves as the analytical warehouse — an embedded OLAP engine optimized for analytical workloads (zero cost, no infrastructure). The architecture is warehouse-agnostic: dbt abstracts SQL dialects, so migrating to Snowflake, BigQuery, or Redshift is a matter of swapping the adapter and updating `profiles.yml`.

**3. Transformation Layer** — dbt models data in three layers: `staging` (raw cleaned), `intermediate` (business logic), and `marts` (final tables for consumption). Includes 92 automated data tests.

**4. Orchestration Layer** — Apache Airflow orchestrates the pipeline on a monthly schedule with automatic retries, timeouts, and failure callbacks.

**5. Consumption Layer** — Two parallel outputs:
   - **Streamlit dashboard** with 5 pages for interactive exploration of P&L, variances, and journal lines
   - **LangChain + OpenAI** agent that generates executive-level variance commentary in natural language

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.10 |
| **Dependency Management** | Poetry |
| **Data Generation** | Faker |
| **Warehouse (dev)** | DuckDB |
| **Transformation** | dbt-core 1.11.11 + dbt-duckdb 1.10.1 |
| **Orchestration** | Apache Airflow 3.1.1 |
| **Dashboard** | Streamlit + Plotly |
| **AI Layer** | LangChain + OpenAI gpt-4o-mini |
| **Containerization** | Docker Compose |
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
| dbt data tests | 92 (89 generic + 3 singular business rule tests) |
| Python unit tests | 51 (84% coverage on data_generator) |
| Synthetic rows processed | 23,000+ |

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
- [x] **Weeks 10-11:** Airflow orchestration and Streamlit dashboard
- [x] **Weeks 12-14:** LangChain-based AI variance analysis agent
- [x] **Weeks 15-16:** CI/CD with GitHub Actions and final documentation

---

## Getting Started

### Prerequisites

- Linux / macOS / WSL2 (Ubuntu 22.04)
- Python 3.10+
- Poetry
- Docker (for Airflow orchestration)

### Quick start (manual)

```bash
# Clone the repo
git clone https://github.com/CarlosLeguiz/finclose-ai.git
cd finclose-ai

# Install dependencies
poetry install

# Set up environment
cp .env.example .env

# Generate synthetic data
poetry run python -m data_generator.main

# Load data into DuckDB
poetry run python -m data_generator.load_to_duckdb

# Run the dbt pipeline
cd dbt_project
poetry run dbt build
```

### Running with Airflow (recommended)

For production-style orchestration with scheduling, retries, and observability:

```bash
# Build the custom Airflow image (first time only)
cd airflow
docker compose build

# Start all Airflow services
docker compose up -d

# Access the UI at http://localhost:8080 (login: airflow / airflow)
# Trigger the DAG manually or wait for the @monthly schedule

# Stop Airflow when done
docker compose down
```

The DAG `finclose_pipeline` runs the full pipeline in 5 sequential tasks:
`generate_synthetic_data` → `load_to_duckdb` → `dbt_run` → `dbt_test` → `notify_success`.

Each task has automatic retries (2 attempts, 2 min delay), a 15-minute execution timeout, and a failure callback that logs incidents to `logs/airflow_failures.log`.

See [`docs/decisions/0005-orchestrate-pipeline-with-airflow.md`](./docs/decisions/0005-orchestrate-pipeline-with-airflow.md) for design rationale.

### Running the dashboard

```bash
poetry run streamlit run dashboard/Summary.py
```

The dashboard has 5 pages: Summary, Variance Analysis, Journal Lines, P&L Statement, and AI Insights. The AI Insights page exposes the LangChain agent for free-form questions and structured variance explanations.

---

## Project Structure
finclose-ai/

├── data_generator/      # Python scripts: synthetic data + DuckDB loader

├── dbt_project/         # dbt transformations (14 models, 92 tests)

│   ├── models/

│   │   ├── staging/     # 7 stg_* models (1:1 with source)

│   │   ├── intermediate/# 2 int_* models (business logic)

│   │   └── marts/       # 5 dim_* / fct_* models (consumption-ready)

│   └── tests/           # 3 singular business rule tests

├── airflow/             # Airflow DAGs, Dockerfile, docker-compose

├── dashboard/           # Streamlit dashboard (5 pages)

├── ai_layer/            # LangChain SQL agent with FP&A-aware prompts

├── data/                # Local data files (gitignored)

├── docs/                # Architecture and design documentation

│   └── decisions/       # 5 ADRs (Architectural Decision Records)

└── tests/               # 51 pytest unit tests for data_generator

## About

Built by **Carlos Leguizamon Guillaumet** as a portfolio project combining accounting expertise (CPA background) with modern data engineering and AI.

- Córdoba, Argentina
- [LinkedIn](https://www.linkedin.com/in/carlos-guillaumet)
- carlosleguizamonguillaumet1998@gmail.com

---

## License

MIT