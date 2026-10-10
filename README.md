# NASA Asteroid Data Pipeline

An automated ETL pipeline that collects near-Earth object close-approach records from NASA/JPL, validates and transforms the data with Python, and loads it into PostgreSQL on Neon. GitHub Actions runs the pipeline on a daily schedule and supports manual execution.

## Architecture

```mermaid
flowchart TD
    A[GitHub Actions: scheduled or manual run] --> B[Install Python dependencies]
    B --> C[Run unit tests]
    C -->|Pass| D[NASA/JPL CAD API]
    D --> E[Python: extract and transform]
    E --> F[Validate fields, types, and duplicates]
    F --> G[Temporary JSON file]
    G --> H[Python: PostgreSQL UPSERT]
    H --> I[(Neon PostgreSQL)]
    I --> J[SQL analytics]
    C -->|Fail| K[Stop workflow]
```

## Tech Stack

| Component | Technology |
| --- | --- |
| Data source | NASA/JPL Small-Body Database Close-Approach Data API |
| Extraction and transformation | Python 3.12, standard library |
| Database | PostgreSQL (Neon) |
| Database driver | Psycopg 3 |
| Scheduling and CI | GitHub Actions |
| Unit testing | Python unittest |
| Analytics | PostgreSQL SQL (aggregation, CTEs, window functions) |

## Implemented Features

- Retrieves close-approach records from a public NASA/JPL JSON API without an API key.
- Converts API row arrays into named records using the `fields` metadata.
- Validates required fields, date format, numeric values, and duplicate approach identifiers.
- Writes valid records to a local JSON file; invalid records are counted and reported.
- Loads records into PostgreSQL with an idempotent UPSERT keyed by object designation and Julian close-approach date.
- Updates existing records only when tracked values have changed.
- Runs four automated unit tests before the ETL steps.
- Supports scheduled and manually triggered GitHub Actions runs.

## Project Structure

```text
nasa-asteroid-pipeline/
├── .github/
│   └── workflows/
│       └── asteroid-etl.yml
├── sql/
│   ├── schema.sql
│   └── analysis.sql
├── tests/
│   └── test_transform.py
├── .env.example
├── .gitignore
├── asteroid_extract.py
├── asteroid_transform.py
├── asteroid_load.py
├── requirements.txt
└── README.md
```

The `sql/` files and `.env.example` are included as reproducibility resources. The generated `asteroids_clean.json` and local `.env` file are intentionally excluded from version control.

## Quick Start

### 1. Set up Python

```bash
git clone https://github.com/thetrue5142/nasa-asteroid-pipeline.git
cd nasa-asteroid-pipeline
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Configure PostgreSQL

Create a PostgreSQL database (for example, on Neon), then run `sql/schema.sql` in its SQL editor.

Create a `.env` file in the project root:

```dotenv
DATABASE_URL=postgresql://USER:PASSWORD@HOST/neondb?sslmode=require
```

Use your own credentials. Never commit `.env` or your database password.

### 3. Run the pipeline

```bash
python asteroid_transform.py
python asteroid_load.py
```

`asteroid_extract.py` is an earlier standalone extraction exercise and is not required for the automated ETL workflow.

### 4. Run unit tests

```bash
python -m unittest discover -s tests -v
```

### 5. Query the database

Use the SQL examples in [`sql/analysis.sql`](sql/analysis.sql) to inspect monthly aggregates, close-approach distances, and distance rankings.

## Data Model

The `asteroid_close_approaches` table stores:

| Column | Description |
| --- | --- |
| `designation` | NASA/JPL object designation |
| `julian_date_tdb` | Original Julian close-approach date string (TDB) |
| `close_approach_tdb` | Formatted close-approach time in TDB |
| `distance_au` | Nominal close-approach distance in astronomical units |
| `velocity_km_s` | Relative velocity in kilometers per second |
| `absolute_magnitude_h` | Absolute magnitude, when supplied |
| `loaded_at`, `updated_at` | Database load and update timestamps |

`(designation, julian_date_tdb)` is the composite primary key. The stored close-approach timestamp is TDB, **not** UTC; it must not be interpreted as a local timestamp.

## Verified Run

On October 10, 2026, a GitHub Actions run reported:

| Check | Observed result |
| --- | --- |
| Unit tests | 4 passed |
| Extracted records | 45 |
| Valid records | 45 |
| Rejected records | 0 |
| Records inserted or updated on that run | 0 |
| Total database records after load | 45 |

The `0` changes on the repeat run demonstrate that unchanged rows were not rewritten. Counts can change as the source data changes. This is a recorded run, not a live dashboard.

## Automation

The GitHub Actions workflow supports `workflow_dispatch` and runs daily at **01:17 UTC** (09:17 Taiwan time) using `ubuntu-24.04` and Python 3.12. GitHub scheduled runs may be delayed or occasionally skipped. Add a repository secret named `DATABASE_URL` containing the PostgreSQL connection string before running the workflow.

## Current Limitations and Next Steps

- The current extraction requests at most 100 matching records, rather than performing complete historical backfills or pagination.
- The API's default query focuses on near-Earth object approaches to Earth within 0.05 AU over the next 60 days.
- Unit tests currently cover four core transformation cases; additional integration and failure-recovery tests would improve confidence.
- No public dashboard or alerting system is implemented yet.
- Distance ranking is **not** an impact-risk assessment.

## Data Source

NASA/JPL Small-Body Database Close-Approach Data API: https://ssd-api.jpl.nasa.gov/doc/cad.html

This project is an independent educational portfolio project and is not affiliated with NASA or JPL.
