
import unittest

from asteroid_transform import transform


class TestAsteroidTransform(unittest.TestCase):

    def setUp(self):
        self.record = {
            "des": "433",
            "jd": "2460964.5",
            "cd": "2026-Oct-10 12:30",
            "dist": "0.0123",
            "v_rel": "12.5",
            "h": "20.1"
        }

    def test_valid_record(self):
        result = transform(self.record)

        self.assertEqual(result["designation"], "433")
        self.assertEqual(result["distance_au"], 0.0123)
        self.assertEqual(result["velocity_km_s"], 12.5)
        self.assertIsInstance(result["distance_au"], float)

    def test_negative_distance(self):
        self.record["dist"] = "-1"

        with self.assertRaises(ValueError):
            transform(self.record)

    def test_missing_designation(self):
        self.record["des"] = ""

        with self.assertRaises(ValueError):
            transform(self.record)

    def test_optional_magnitude(self):
        self.record["h"] = ""

        result = transform(self.record)

        self.assertIsNone(result["absolute_magnitude_h"])


if __name__ == "__main__":
    unittest.main()
