"""The schema supports SQLite 3.38 or later (data model §9): on 3.38 and 3.40 json_valid(NULL) is 0, on 3.46 it is NULL, so a nullable JSON column needs a NULL guard."""
import re

from mb360.db import SCHEMA


def test_every_json_check_allows_null():
    schema = SCHEMA.read_text(encoding="utf-8")
    checks = re.findall(r"CHECK \(([^\n]*json_valid\([^\n]*)\),", schema)
    assert len(checks) == 3
    for check in checks:
        column = re.search(r"json_valid\((\w+)\)", check).group(1)
        assert check.startswith(f"{column} IS NULL OR "), check
