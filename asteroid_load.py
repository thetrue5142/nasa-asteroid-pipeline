
import json
import os
from datetime import datetime
from pathlib import Path

import psycopg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "asteroids_clean.json"

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

UPSERT_SQL = """
INSERT INTO asteroid_close_approaches AS target (
    designation,
    julian_date_tdb,
    close_approach_tdb,
    distance_au,
    velocity_km_s,
    absolute_magnitude_h
)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (designation, julian_date_tdb)
DO UPDATE SET
    close_approach_tdb = EXCLUDED.close_approach_tdb,
    distance_au = EXCLUDED.distance_au,
    velocity_km_s = EXCLUDED.velocity_km_s,
    absolute_magnitude_h = EXCLUDED.absolute_magnitude_h,
    updated_at = CURRENT_TIMESTAMP
WHERE (
    target.close_approach_tdb,
    target.distance_au,
    target.velocity_km_s,
    target.absolute_magnitude_h
) IS DISTINCT FROM (
    EXCLUDED.close_approach_tdb,
    EXCLUDED.distance_au,
    EXCLUDED.velocity_km_s,
    EXCLUDED.absolute_magnitude_h
)
"""


def main():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing")

    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    if not isinstance(records, list) or not records:
        raise ValueError("No valid records found")

    changed = 0

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            for asteroid in records:
                values = (
                    asteroid["designation"],
                    asteroid["julian_date_tdb"],
                    datetime.fromisoformat(
                        asteroid["close_approach_tdb"]
                    ),
                    asteroid["distance_au"],
                    asteroid["velocity_km_s"],
                    asteroid["absolute_magnitude_h"]
                )

                cursor.execute(UPSERT_SQL, values)
                changed += cursor.rowcount

            cursor.execute(
                "SELECT COUNT(*) FROM asteroid_close_approaches"
            )
            total = cursor.fetchone()[0]

    print(f"Source records: {len(records)}")
    print(f"Inserted or updated: {changed}")
    print(f"Total database records: {total}")
    print("Load completed successfully")


if __name__ == "__main__":
    main()
