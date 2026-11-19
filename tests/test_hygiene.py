# SPDX-License-Identifier: MIT
"""Repo hygiene: no environment-specific strings, and the project's code-size limits."""
import ast
import os
import unittest
from pathlib import Path

from helpers import ROOT

# One string per line; absent = test skipped. Keep it OUTSIDE the repo (env var) so it never ships.
DENYLIST = Path(os.environ.get("EQUIPMENT_LOCKER_DENYLIST", ROOT / ".local_denylist"))
SOURCES = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in {".py", ".sql", ".md", ".toml", ".txt", ".svg", ".js", ".html", ".css"}
           and "__pycache__" not in p.parts and p != DENYLIST]


class TestHygiene(unittest.TestCase):
    @unittest.skipUnless(DENYLIST.exists(), "no local denylist")
    def test_no_denylisted_strings(self):
        words = [w.strip().lower() for w in DENYLIST.read_text().splitlines() if w.strip() and not w.startswith("#")]
        hits = [(p.relative_to(ROOT), w) for p in SOURCES for w in words if w in p.read_text().lower()]
        self.assertEqual(hits, [])

    def test_file_length(self):
        long = [(p.relative_to(ROOT), n) for p in SOURCES if p.suffix in {".py", ".sql", ".js"}
                and (n := len(p.read_text().splitlines())) > 200]
        self.assertEqual(long, [])

    def test_function_length_and_params(self):
        bad = []
        for path in (p for p in SOURCES if p.suffix == ".py"):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines = node.end_lineno - node.lineno + 1
                    params = len(node.args.args) - (1 if node.args.args and node.args.args[0].arg == "self" else 0)
                    if lines > 50 or params > 4:
                        bad.append(f"{path.relative_to(ROOT)}:{node.name} lines={lines} params={params}")
        self.assertEqual(bad, [])

    def test_spdx_header(self):
        missing = [p.relative_to(ROOT) for p in SOURCES if p.suffix in {".py", ".sql", ".js"}
                   and "SPDX-License-Identifier: MIT" not in p.read_text()[:300]]
        self.assertEqual(missing, [])
