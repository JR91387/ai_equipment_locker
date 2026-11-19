# SPDX-License-Identifier: MIT
"""Gradients: ten valid squares, and every tool gets a stable one."""
import unittest
import xml.etree.ElementTree as ET

import helpers

from equipment_locker.api import GRADIENTS, gradient_for

DIR = helpers.ROOT / "src" / "equipment_locker" / "web" / "gradients"


class TestGradients(unittest.TestCase):
    def test_ten_square_svgs(self):
        files = sorted(DIR.glob("g*.svg"))
        self.assertEqual([f.name for f in files], [f"g{n:02d}.svg" for n in range(1, GRADIENTS + 1)])
        for f in files:
            root = ET.parse(f).getroot()
            self.assertEqual((root.get("width"), root.get("height")), ("512", "512"), f.name)

    def test_assignment_is_stable_and_in_range(self):
        codes = ["claude-code", "codex", "cursor", "ollama", "other", "x" * 40]
        first = [gradient_for(c) for c in codes]
        self.assertEqual(first, [gradient_for(c) for c in codes])
        self.assertTrue(all(1 <= g <= GRADIENTS for g in first))
        self.assertGreater(len({gradient_for(f"tool-{n}") for n in range(60)}), 6)


if __name__ == "__main__":
    unittest.main()
