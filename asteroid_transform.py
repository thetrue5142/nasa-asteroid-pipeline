
import json
import math
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://ssd-api.jpl.nasa.gov/cad.api?limit=100"
OUTPUT = Path("asteroids_clean.json")

REQUIRED_FIELDS = {"des", "jd", "cd", "dist", "v_rel"}


def extract():
    request = Request(URL, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(request, timeout=30) as response:
        payload = json.load(response)

    version = payload.get("signature", {}).get("version")

    if version != "1.5":
        raise ValueError(f"Unsupported API version: {version}")

    return payload


def transform(record):
    designation = str(record.get("des") or "").strip()
    julian_date = str(record.get("jd") or "").strip()

    if not designation or not julian_date:
        raise ValueError("Missing asteroid identifier")

    close_approach = datetime.strptime(
        record["cd"], "%Y-%b-%d %H:%M"
    )

    distance = float(record["dist"])
    velocity = float(record["v_rel"])

    if not math.isfinite(distance) or distance <= 0:
        raise ValueError("Invalid distance")

    if not math.isfinite(velocity) or velocity < 0:
        raise ValueError("Invalid velocity")

    raw_h = record.get("h")
    magnitude = float(raw_h) if raw_h not in (None, "") else None

    if magnitude is not None and not math.isfinite(magnitude):
        raise ValueError("Invalid magnitude")

    return {
        "designation": designation,
        "julian_date_tdb": julian_date,
        "close_approach_tdb": close_approach.isoformat(timespec="minutes"),
        "distance_au": distance,
        "velocity_km_s": velocity,
        "absolute_magnitude_h": magnitude
    }


def main():
    payload = extract()
    fields = payload.get("fields", [])
    rows = payload.get("data", [])

    if not REQUIRED_FIELDS.issubset(set(fields)):
        raise ValueError("Required API fields are missing")

    cleaned = []
    rejected = []
    seen = set()

    for index, row in enumerate(rows, start=1):
        try:
            if len(row) != len(fields):
                raise ValueError("Field count mismatch")

            record = dict(zip(fields, row))
            asteroid = transform(record)

            key = (
                asteroid["designation"],
                asteroid["julian_date_tdb"]
            )

            if key in seen:
                raise ValueError("Duplicate close approach")

            seen.add(key)
            cleaned.append(asteroid)

        except (ValueError, TypeError, KeyError) as error:
            rejected.append({
                "row": index,
                "reason": str(error)
            })

    OUTPUT.write_text(
        json.dumps(cleaned, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Extracted: {len(rows)}")
    print(f"Valid: {len(cleaned)}")
    print(f"Rejected: {len(rejected)}")
    print(f"Saved to: {OUTPUT.resolve()}")

    for error in rejected:
        print(f"Rejected row {error['row']}: {error['reason']}")

    if cleaned:
        print("\nFirst cleaned record:")
        print(json.dumps(cleaned[0], indent=2))
        print(f"\nDistance Python type: {type(cleaned[0]['distance_au']).__name__}")


if __name__ == "__main__":
    main()
