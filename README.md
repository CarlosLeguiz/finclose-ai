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

See `docs/architecture.md` for the detailed diagram (added in Week 2).

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

## Project Roadmap (16 weeks)

- [ ] **Week 1:** Environment setup and project scaffolding
- [ ] **Week 2:** Accounting data model design (7 core tables)
- [ ] **Weeks 3-4:** Synthetic data generation with Python + Faker
- [ ] **Weeks 5-7:** dbt staging and intermediate models
- [ ] **Weeks 8-9:** dbt marts and data quality tests
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

### Quick start (coming soon)
```bash
# Clone the repo
git clone https://github.com/<username>/finclose-ai.git
cd finclose-ai

# Install dependencies
poetry install

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Generate sample data (week 3+)
poetry run python data_generator/generate.py
```

## Project Structure

```
finclose-ai/
├── data_generator/   # Python scripts to generate synthetic accounting data
├── dbt_project/      # dbt transformations (staging → marts)
├── airflow/          # Airflow DAGs and orchestration
├── dashboard/        # Streamlit interactive dashboard
├── ai_layer/         # LangChain-based AI analysis agents
├── data/             # Local data files (gitignored)
├── docs/             # Architecture and design documentation
└── tests/            # Python unit and integration tests
```

## About

Built by **Carlos Leguizamon Guillaumet** as a portfolio project combining accounting expertise (CPA background) with modern data engineering and AI.

- Córdoba, Argentina
- [LinkedIn](https://www.linkedin.com/in/carlos-guillaumet)
- carlosleguizamonguillaumet1998@gmail.com

---

## License

MIT