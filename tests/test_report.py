import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from benchkit.report import render


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.results = self.root / "results"
        self.site = self.root / "site"

    def result(self, runtime="cpython", **changes):
        record = {
            "schema_version": 1,
            "case": "dsu",
            "title": "DSU",
            "description": "Merge and connectivity queries",
            "runtime": {"id": runtime, "implementation": runtime, "version": "3.11.9", "cpu": "Test CPU", "platform": "Linux"},
            "measured_at": "2026-09-26T10:00:00Z",
            "commit": "abc123",
            "settings": {"repeat": 5, "warmup": 3, "seed": 42},
            "sources": {"example": {"url": "https://example.org/library", "rev": "def456"}},
            "series": [{"id": "example", "label": "Example library", "points": [
                {"size": 100, "median": 0.001, "min": 0.0009, "max": 0.0012},
                {"size": 1000, "median": 0.01, "min": 0.009, "max": 0.012},
            ]}],
        }
        record.update(changes)
        source = self.results / runtime / "dsu.json"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(json.dumps(record), encoding="utf-8")
        return source

    def test_merges_runtimes_and_preserves_provenance_and_raw_data(self):
        cpython = self.result()
        pypy = self.result("pypy", measured_at="2026-09-25T10:00:00Z")
        render(self.results, self.site)
        chart = ET.parse(self.site / "charts/dsu.svg")
        chart_text = " ".join(chart.getroot().itertext())
        self.assertIn("cpython 3.11.9", chart_text)
        self.assertIn("pypy 3.11.9", chart_text)
        self.assertIn("log scale", chart_text)
        self.assertEqual(cpython.read_bytes(), (self.site / "data/cpython/dsu.json").read_bytes())
        self.assertEqual(pypy.read_bytes(), (self.site / "data/pypy/dsu.json").read_bytes())
        page = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertIn("2026-09-26T10:00:00Z", page)
        self.assertIn("2026-09-25T10:00:00Z", page)
        self.assertIn("def456", page)
        self.assertIn("Test CPU", page)
        self.assertIn("![DSU](charts/dsu.svg)", (self.site / "README.md").read_text())
        self.assertTrue((self.site / ".nojekyll").exists())

    def test_escapes_external_text_and_unsafe_source_links(self):
        title = '<script>alert("title")</script>'
        label = '<img src=x onerror="alert(1)">'
        self.result(title=title, description=label,
                    sources={"<script>": {"url": "javascript:alert(1)", "rev": "<script>"}},
                    series=[{"id": "external", "label": label, "points": [{"size": 10, "median": 0.01}]}])
        render(self.results, self.site)
        ET.parse(self.site / "charts/dsu.svg")
        for filename in ("index.html", "charts/dsu.svg", "README.md"):
            content = (self.site / filename).read_text()
            self.assertNotIn("<script>", content)
            self.assertNotIn("<img src=x", content)
        self.assertNotIn('href="javascript:', (self.site / "index.html").read_text())

    def test_zero_timings_and_sizes_use_linear_axes(self):
        self.result(series=[{"id": "zero", "label": "zero", "points": [
            {"size": 0, "median": 0, "min": 0, "max": 0},
            {"size": 10, "median": 0.001, "min": 0, "max": 0.002},
        ]}])
        render(self.results, self.site)
        chart = ET.parse(self.site / "charts/dsu.svg")
        text = " ".join(chart.getroot().itertext())
        self.assertIn("Input size n (linear scale)", text)
        self.assertIn("Elapsed time [ms] (linear scale)", text)

    def test_empty_results_and_removed_cases(self):
        render(self.results, self.site)
        self.assertIn("計測結果はまだありません", (self.site / "index.html").read_text())
        source = self.result()
        render(self.results, self.site)
        self.assertTrue((self.site / "charts/dsu.svg").exists())
        source.unlink()
        render(self.results, self.site)
        self.assertFalse((self.site / "charts/dsu.svg").exists())
        self.assertFalse((self.site / "data/cpython/dsu.json").exists())

    def test_invalid_output_location_does_not_delete_results(self):
        source = self.result()
        with self.assertRaises(ValueError):
            render(self.results, self.results)
        self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
