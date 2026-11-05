"""Unit tests for CommitPhalanx synthesizer, analyzer, and API server."""

import unittest
from commitphalanx.synthesizer import CommitSynthesizer, GitAnalyzer


class TestCommitPhalanx(unittest.TestCase):

    def test_synthesize_commit_feature(self):
        diff = """--- a/api/routes.py
+++ b/api/routes.py
@@ -1,3 +1,5 @@
+def new_endpoint():
+    return {"ok": True}
"""
        files = [{"status": "M", "path": "api/routes.py"}]
        res = CommitSynthesizer.synthesize_commit(diff, files)
        self.assertEqual(res["type"], "feat")
        self.assertEqual(res["scope"], "api")
        self.assertIn("feat(api):", res["summary"])
        self.assertIn("routes.py", res["body"])

    def test_synthesize_commit_bugfix(self):
        diff = """--- a/core/parser.py
+++ b/core/parser.py
@@ -10,3 +10,3 @@
-    val = int(x)
+    val = int(x) if x else 0 # fix null error
"""
        files = [{"status": "M", "path": "core/parser.py"}]
        res = CommitSynthesizer.synthesize_commit(diff, files)
        self.assertEqual(res["type"], "fix")
        self.assertEqual(res["scope"], "core")
        self.assertIn("fix(core):", res["summary"])

    def test_synthesize_pull_request(self):
        diff = "+++ b/docs/readme.md\n+ # Updates\n"
        files = [{"status": "M", "path": "docs/readme.md"}]
        pr = CommitSynthesizer.synthesize_pull_request("patch-docs", diff, files)
        self.assertIn("Overview", pr["body"])
        self.assertIn("Testing & Verification", pr["body"])
        self.assertIn("docs/readme.md", pr["body"])

    def test_generate_changelog(self):
        commits = [
            {"hash": "a1b2c3d", "author": "Alice", "date": "2026-11-05", "subject": "feat(core): add streaming support"},
            {"hash": "e4f5g6h", "author": "Bob", "date": "2026-11-05", "subject": "fix(api): resolve timeout issue"},
            {"hash": "i7j8k9l", "author": "Charlie", "date": "2026-11-05", "subject": "docs: update install guide"},
        ]
        changelog = CommitSynthesizer.generate_changelog(commits, version="v1.0.0")
        self.assertIn("# Changelog", changelog)
        self.assertIn("## [v1.0.0]", changelog)
        self.assertIn("### Features", changelog)
        self.assertIn("### Bug Fixes", changelog)
        self.assertIn("### Documentation", changelog)
        self.assertIn("a1b2c3d", changelog)

    def test_empty_diff_fallback(self):
        res = CommitSynthesizer.synthesize_commit("", [])
        self.assertEqual(res["type"], "chore")
        self.assertIn("chore: update repository files", res["summary"])


if __name__ == "__main__":
    unittest.main()
