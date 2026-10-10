
import json
from urllib.request import Request, urlopen

URL = "https://ssd-api.jpl.nasa.gov/cad.api?limit=5"

request = Request(URL, headers={"User-Agent": "Mozilla/5.0"})

with urlopen(request, timeout=30) as response:
    payload = json.load(response)

fields = payload.get("fields", [])
rows = payload.get("data", [])

asteroids = [dict(zip(fields, row)) for row in rows]

print(f"API version: {payload['signature']['version']}")
print(f"Returned records: {len(asteroids)}")
print(f"Available fields: {fields}")

for asteroid in asteroids:
    print(
        f"Asteroid: {asteroid['des']} | "
        f"Close approach: {asteroid['cd']} | "
        f"Distance: {asteroid['dist']} AU | "
        f"Relative velocity: {asteroid['v_rel']} km/s"
    )

if asteroids:
    print("\nFirst record as JSON:")
    print(json.dumps(asteroids[0], indent=2))
