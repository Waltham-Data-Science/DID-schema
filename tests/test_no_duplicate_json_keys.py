"""No JSON file under schemas/ repeats a key inside one object.

Python's json module keeps the LAST of two equal keys without a word, so a
merge that fuses two objects (as happened to carry-167 and carry-168 in the
carry register, did-schema #268) reads as valid JSON with one row silently
gone. This test reads every file with a hook that refuses a repeated key.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _refuse_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"repeated key {key!r}")
        seen[key] = value
    return seen


class TestNoDuplicateJsonKeys(unittest.TestCase):
    def test_every_schema_json_has_unique_keys(self):
        files = sorted((ROOT / "schemas").rglob("*.json"))
        # denominator first: a scan that read nothing proves nothing
        self.assertGreater(len(files), 100, f"only {len(files)} JSON files found under schemas/")
        bad = []
        for path in files:
            try:
                json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_refuse_duplicates)
            except ValueError as exc:
                bad.append(f"{path.relative_to(ROOT)}: {exc}")
        self.assertEqual(bad, [], f"{len(bad)} of {len(files)} files repeat a key:\n" + "\n".join(bad))


if __name__ == "__main__":
    unittest.main()
