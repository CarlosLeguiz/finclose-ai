# ADR 0003 — Pin Black to v24.x to resolve pathspec conflict with dbt-core

**Status:** Accepted
**Date:** 2026-06-02
**Author:** Carlos Leguizamon Guillaumet

---

## Context

When adding `dbt-core ^1.10` and `dbt-duckdb ^1.10` to the project, Poetry's dependency resolver failed with a conflict. Both Black and dbt-core depend on the `pathspec` package, but each requires incompatible version ranges:

- `dbt-core 1.x` requires `pathspec >= 0.9, < 0.13`
- `black 26.x` requires `pathspec >= 1.0.0`

Since both packages need different versions of the same transitive dependency, Poetry could not produce a valid dependency graph.

## Decision

Pin Black to `^24.0` (the latest 24.x release line), which uses a `pathspec` version compatible with dbt-core 1.x. dbt-core remains pinned to `^1.10` (latest stable, avoiding the unstable 2.0.0a1 alpha).

## Rationale

- Black is a code formatter; its behavior is essentially stable across recent major versions. Pinning to 24.x does not lose any feature relevant to this project.
- dbt-core 1.x is the production-stable release. Downgrading dbt to match Black's newer dependencies would mean using dbt 2.0 alpha, which is not appropriate for portfolio code.
- `pathspec` is a low-level transitive dependency; the conflict is purely about version metadata, not actual feature use.
- The Poetry resolver enforces dependency compatibility at install time, surfacing this conflict immediately rather than failing at runtime.

## Consequences

**Positive:**
- Unblocked dbt-core 1.x installation for the project's transformation layer (weeks 5-9).
- Black continues to format code consistently; no developer-facing change.
- Dependency graph is now resolvable and reproducible via poetry.lock.

**Negative:**
- Cannot use Black 26.x features (none relevant to this project).
- Creates a constraint that must be revisited if dbt-core 2.x becomes stable and adopts the newer pathspec range.

## Revisit when

- dbt-core 2.x reaches stable release (non-alpha) and the project decides to upgrade.
- A specific Black 26.x feature becomes relevant.
- The `pathspec` package versions converge in upstream packages.