# Custom Airflow image with Poetry and project dependencies installed.
# Built on top of the official Airflow 3.1.1 image.

FROM apache/airflow:3.1.1

# Switch to root to install system packages
USER root

# Install system tools needed for builds
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user for pip installations
USER airflow

# Install Poetry (used by the data_generator scripts)
RUN pip install --no-cache-dir poetry==2.4.1

# Install dbt-core + dbt-duckdb directly with pip (avoids Poetry env issues
# inside the container; dbt runs as a CLI tool from the system path)
RUN pip install --no-cache-dir \
    dbt-core==1.11.11 \
    dbt-duckdb==1.10.1

# Install the project's Python dependencies that the DAG will need
RUN pip install --no-cache-dir \
    "faker>=40.19,<41.0" \
    "duckdb>=1.4,<2.0" \
    "pandas>=2.2.0,<3.0.0" \
    "pyarrow>=21.0,<22.0"

# Configure Poetry to not create virtual envs inside the container
# (we're already isolated by Docker; nested venvs cause issues with paths)
RUN poetry config virtualenvs.create false