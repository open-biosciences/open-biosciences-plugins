import json
import tempfile
import unittest
from pathlib import Path

from scripts.validators.graph_memory_fragment import validate_graph_memory_fragment
from scripts.validators import Severity


def _temp_json(obj) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(obj, f)
    f.close()
    return Path(f.name)


_GOOD_FRAGMENT = {
    "type": "local_context",
    "source": "A", "target": "B", "edge_type": "relation",
    "valid_at": "2026-07-09T09:00:00-07:00", "fact": "A and B share a bond.",
    "status": "SELF_REPORTED", "provenance": {"edge_uuid": "u1"},
}


class TestGraphMemoryFragment(unittest.TestCase):
    def test_valid_fragment_passes(self):
        path = _temp_json({"graph": "g", "snapshot_at": "2026-07-09", "fragments": [_GOOD_FRAGMENT]})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.PASS)

    def test_empty_fragments_passes(self):
        path = _temp_json({"graph": "g", "snapshot_at": "2026-07-09", "fragments": []})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.PASS)

    def test_missing_fragments_array_blocks(self):
        path = _temp_json({"graph": "g"})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_wrong_type_blocks(self):
        frag = dict(_GOOD_FRAGMENT, type="primary")
        path = _temp_json({"fragments": [frag]})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_missing_required_field_blocks(self):
        frag = dict(_GOOD_FRAGMENT)
        del frag["fact"]
        path = _temp_json({"fragments": [frag]})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_verified_status_blocks(self):
        frag = dict(_GOOD_FRAGMENT, status="VERIFIED")
        path = _temp_json({"fragments": [frag]})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_malformed_json_blocks(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        f.write("{ not json")
        f.close()
        r = validate_graph_memory_fragment(Path(f.name))
        self.assertEqual(r.severity, Severity.BLOCK)


if __name__ == "__main__":
    unittest.main()
