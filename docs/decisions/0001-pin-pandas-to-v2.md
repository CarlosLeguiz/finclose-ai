# ADR 0001 — Pin pandas to v2.x

**Status:** Accepted
**Date:** 2026-05-26
**Author:** Carlos Leguizamon Guillaumet

---

## Context

When trying to add pandas via `poetry add pandas`, Poetry refused to resolve dependencies because pandas 3.0.x requires Python >= 3.11, while this project runs on Python 3.10.12 (an LTS version supported until October 2026).

## Decision

Pin pandas to v2.x by adding it as `pandas = "^2.2"` in pyproject.toml.

## Rationale

- pandas 2.x covers 100% of the functionality required for this project: DataFrame construction, `to_csv()`, and `to_parquet()` for the data generator output.
- Upgrading Python 3.10 → 3.11+ would require recreating the Poetry virtualenv and reinstalling all dependencies, with no functional benefit at the current project stage.
- Python 3.10 is still officially supported and widely used in production environments. Pinning pandas to 2.x is a deliberate choice to defer the upgrade, not a workaround for an outdated setup.

## Consequences

**Positive:**
- Unblocked CSV persistence work in the data generator package.
- Avoided risk of breaking the Poetry virtualenv during a Python upgrade.
- The project remains installable for anyone with Python 3.10+ (lower entry barrier).

**Negative:**
- No access to pandas 3.x features (none required for current project scope).
- Creates technical debt that must be revisited if any downstream dependency requires pandas 3.x.

## Revisit when

- A downstream dependency (e.g., Airflow, dbt-core, or LangChain) requires pandas 3.x.
- Python 3.10 approaches its End of Life (October 2026).
- A specific pandas 3.x feature becomes relevant to the project scope.