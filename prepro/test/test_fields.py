"""Round trips of the model editor's widget slots, without Blender.

Needs an MBDyn checkout with contrib/PythonModelBuilder, named by $MBDYN_SRC.
Run from the add-on directory: python3 -m unittest discover -s prepro/test
"""

import glob
import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("prepro_fields", HERE.parent / "fields.py")
fields = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fields)

SOURCE = os.environ.get("MBDYN_SRC")
BUILDER = Path(SOURCE) / "contrib" / "PythonModelBuilder" if SOURCE else None
if BUILDER and BUILDER.is_dir():
    sys.path.insert(0, str(BUILDER))


def round_trip(name, binding, default, value):
    kind = fields.widget(name, binding, default)
    return fields.from_slots(kind, binding, fields.to_slots(kind, binding, value))


@unittest.skipUnless(BUILDER and BUILDER.is_dir(), "set MBDYN_SRC to an MBDyn checkout")
class FieldRoundTrips(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mbdyn_builder.model import BLOCKS
        cls.blocks = BLOCKS

    def check(self, kind, properties):
        spec = self.blocks[kind]
        for name, value in properties.items():
            binding = spec.property_bindings.get(name, {})
            with self.subTest(kind=kind, name=name):
                self.assertEqual(round_trip(name, binding, spec.defaults.get(name), value), value)

    def test_catalog_defaults(self):
        for kind, spec in self.blocks.items():
            if kind != "component":
                self.check(kind, spec.defaults)

    def test_example_documents(self):
        for path in sorted(glob.glob(str(BUILDER / "examples" / "*.json"))):
            for block in json.loads(Path(path).read_text())["blocks"]:
                if block["kind"] != "component":
                    self.check(block["kind"], block["properties"])

    def test_values_an_editor_writes(self):
        position = self.blocks["RevoluteHinge"].property_bindings["position_1"]
        for value in ({"type": "vector", "values": [{"expr": "atan2(L, 1)"}, 0, 1.5],
                       "reference": "node"},
                      {"type": "axes", "first_axis": 1, "first_vector": [1, 0, 0],
                       "second_axis": 2, "second_vector": "guess"},
                      {"raw": "Position(relative_position=eye())"}):
            self.assertEqual(round_trip("position_1", position, None, value), value)
        clamp = self.blocks["Clamp"].property_bindings["position"]
        self.assertEqual(round_trip("position", clamp, None, "node"), "node")
        self.assertEqual(fields.split("a, atan2(b, c), [1, 2]"), ["a", "atan2(b, c)", "[1, 2]"])


if __name__ == "__main__":
    unittest.main()
