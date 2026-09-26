"""Exercise publication against local bare repositories, with no network writes."""

from pathlib import Path
import os
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import publish


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="acl-publish-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.remote = self.root / "remote.git"
        self.git("init", "--quiet", "--bare", "--initial-branch=main", str(self.remote))
        self.site = self.root / "site"
        self.site.mkdir()
        (self.site / "index.html").write_text("<h1>Benchmark report</h1>", encoding="utf-8")
        self.results = self.root / "results"
        (self.results / "cpython").mkdir(parents=True)
        (self.results / "cpython" / "dsu.json").write_text('{"result": 1}', encoding="utf-8")
        self.output = self.root / "github-output"
        self.environment = mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(self.output)})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args], cwd=cwd, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        ).stdout.strip()

    def save(self, **kwargs):
        return publish.publish(str(self.remote), "gh-pages", self.site, self.results, **kwargs)

    def revision(self):
        return self.git("--git-dir", str(self.remote), "rev-parse", "refs/heads/gh-pages")

    def test_first_run_restore_has_no_remote_side_effect(self):
        destination = self.root / "restored"
        publish.restore(str(self.remote), "gh-pages", destination)
        self.assertTrue(destination.is_dir())
        self.assertEqual(list(destination.iterdir()), [])
        self.assertIsNone(publish.remote_revision(str(self.remote), "refs/heads/gh-pages"))

    def test_unreachable_remote_is_not_treated_as_first_run(self):
        destination = self.root / "restored"
        with self.assertRaises(subprocess.CalledProcessError):
            publish.restore(str(self.root / "missing.git"), "gh-pages", destination)
        self.assertFalse(destination.exists())

    def test_round_trip_preserves_other_runtime_and_removes_deleted_files(self):
        (self.results / "pypy").mkdir()
        (self.results / "pypy" / "dsu.json").write_text('{"result": 2}', encoding="utf-8")
        (self.site / "deleted.svg").write_text("<svg/>", encoding="utf-8")
        self.assertTrue(self.save())
        before = self.revision()
        (self.site / "deleted.svg").unlink()
        (self.results / "cpython" / "dsu.json").unlink()
        (self.results / "cpython" / "segtree.json").write_text('{"result": 3}', encoding="utf-8")
        self.assertTrue(self.save())
        self.assertEqual(self.git("--git-dir", str(self.remote), "rev-parse", "gh-pages^"), before)
        destination = self.root / "restored"
        publish.restore(str(self.remote), "gh-pages", destination)
        self.assertEqual((destination / "pypy" / "dsu.json").read_text(), '{"result": 2}')
        self.assertFalse((destination / "cpython" / "dsu.json").exists())
        self.assertTrue((destination / "cpython" / "segtree.json").exists())
        files = self.git("--git-dir", str(self.remote), "ls-tree", "-r", "--name-only", "gh-pages").splitlines()
        self.assertNotIn("deleted.svg", files)
        self.assertIn(".nojekyll", files)

    def test_unchanged_results_do_not_create_a_commit(self):
        self.save()
        before = self.revision()
        self.assertTrue(self.save())
        self.assertEqual(self.revision(), before)

    def test_stale_source_skips_publication_and_pages_deployment(self):
        self.save()
        before = self.revision()
        self.assertFalse(self.save(source_ref="refs/heads/main", source_sha="0" * 40))
        self.assertEqual(self.revision(), before)
        self.assertTrue(self.output.read_text().endswith("published=false\n"))

    def test_incomplete_site_does_not_destroy_existing_results(self):
        self.save()
        before = self.revision()
        (self.site / "index.html").unlink()
        with self.assertRaises(ValueError):
            self.save()
        self.assertEqual(self.revision(), before)

    def test_symlink_is_not_published(self):
        (self.site / "outside.txt").symlink_to(self.results / "cpython" / "dsu.json")
        with self.assertRaises(ValueError):
            self.save()
        self.assertIsNone(publish.remote_revision(str(self.remote), "refs/heads/gh-pages"))

    def test_concurrent_update_is_preserved_by_rejected_push(self):
        self.save()
        concurrent = self.root / "concurrent"
        self.git("clone", "--quiet", "--branch", "gh-pages", str(self.remote), str(concurrent))
        (concurrent / "other.txt").write_text("concurrent publication", encoding="utf-8")
        self.git("add", ".", cwd=concurrent)
        self.git("-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "--quiet", "-m", "Concurrent update", cwd=concurrent)
        concurrent_sha = self.git("rev-parse", "HEAD", cwd=concurrent)
        (self.site / "index.html").write_text("<h1>New report</h1>", encoding="utf-8")
        original_git = publish.git

        def race(*args, **kwargs):
            if args[0] == "push":
                self.git("push", "--quiet", "origin", "HEAD:gh-pages", cwd=concurrent)
            return original_git(*args, **kwargs)

        with mock.patch.object(publish, "git", side_effect=race):
            with self.assertRaises(subprocess.CalledProcessError):
                self.save()
        self.assertEqual(self.revision(), concurrent_sha)


if __name__ == "__main__":
    unittest.main()
