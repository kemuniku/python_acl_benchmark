"""Restore/persist benchmark data without force-pushing or executing benchmarks.

The gh-pages branch is durable storage; GitHub Pages itself is deployed through
the official Pages artifact action. A missing branch is normal on the first run,
but authentication, fetch and push failures are fatal.
"""

from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit


def git_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    token = env.get("GITHUB_TOKEN")
    if token:
        # Keep credentials in the subprocess environment, never command arguments
        # or repository config. Read jobs receive only a read-only token.
        server = env.get("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
        if urlsplit(server).scheme != "https":
            raise ValueError("GITHUB_SERVER_URL must use HTTPS")
        index = int(env.get("GIT_CONFIG_COUNT", "0"))
        env["GIT_CONFIG_COUNT"] = str(index + 1)
        env[f"GIT_CONFIG_KEY_{index}"] = f"http.{server}/.extraheader"
        encoded = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env[f"GIT_CONFIG_VALUE_{index}"] = f"AUTHORIZATION: basic {encoded}"
    return env


def git(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, env=git_environment(), check=check,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def remote_revision(remote: str, ref: str) -> str | None:
    result = git("ls-remote", "--exit-code", "--refs", remote, ref, check=False)
    if result.returncode == 2:
        return None
    result.check_returncode()
    matches = [line.split() for line in result.stdout.splitlines()]
    exact = [sha for sha, name in matches if name == ref]
    if len(exact) != 1:
        raise RuntimeError(f"Expected exactly one remote ref: {ref}")
    return exact[0]


def checkout_branch(remote: str, branch: str, target: Path) -> bool:
    ref = f"refs/heads/{branch}"
    exists = remote_revision(remote, ref) is not None
    git("init", "--quiet", str(target))
    if exists:
        git("fetch", "--quiet", "--depth=1", "--no-tags", remote, ref, cwd=target)
        git("checkout", "--quiet", "-B", branch, "FETCH_HEAD", cwd=target)
    else:
        git("checkout", "--quiet", "--orphan", branch, cwd=target)
    return exists


def validate_tree(path: Path) -> None:
    if not path.is_dir() or path.is_symlink():
        raise ValueError(f"Expected a directory: {path}")
    for child in path.rglob("*"):
        if child.is_symlink() or child.name == ".git":
            raise ValueError(f"Refusing a symlink or nested Git repository: {child}")
        if not child.is_dir() and not child.is_file():
            raise ValueError(f"Refusing a special file: {child}")


def restore(remote: str, branch: str, results: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="acl-results-") as temporary:
        checkout = Path(temporary) / "checkout"
        if not checkout_branch(remote, branch, checkout):
            results.mkdir(parents=True, exist_ok=True)
            print(f"No {branch} branch yet; measuring from scratch.")
            return
        data = checkout / "data"
        if not data.is_dir():
            raise ValueError(f"Existing {branch} branch has no data directory")
        validate_tree(data)
        shutil.copytree(data, results, dirs_exist_ok=True)
        print(f"Restored measurements from {branch}/data.")


def set_published(published: bool) -> None:
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"published={'true' if published else 'false'}\n")


def publish(remote: str, branch: str, site: Path, results: Path,
            source_ref: str | None = None, source_sha: str | None = None) -> bool:
    if bool(source_ref) != bool(source_sha):
        raise ValueError("--source-ref and --source-sha must be supplied together")
    validate_tree(site)
    validate_tree(results)
    if not (site / "index.html").is_file():
        raise ValueError("Site has no index.html; refusing to publish an incomplete report")
    if source_ref and remote_revision(remote, source_ref) != source_sha:
        print("Source branch has advanced; skipping publication of stale results.")
        set_published(False)
        return False

    with tempfile.TemporaryDirectory(prefix="acl-publish-") as temporary:
        checkout = Path(temporary) / "checkout"
        checkout_branch(remote, branch, checkout)
        # The generated site owns this branch. Removing old files also removes
        # graphs and records for deleted cases/implementations.
        for child in checkout.iterdir():
            if child.name == ".git":
                continue
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
        shutil.copytree(site, checkout, dirs_exist_ok=True)
        data = checkout / "data"
        if data.exists():
            shutil.rmtree(data)
        shutil.copytree(results, data)
        (checkout / ".nojekyll").touch()
        git("add", "--all", cwd=checkout)
        changed = git("diff", "--cached", "--quiet", cwd=checkout, check=False)
        if changed.returncode not in (0, 1):
            changed.check_returncode()
        if changed.returncode:
            git("-c", "user.name=github-actions[bot]", "-c",
                "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                "commit", "--quiet", "-m", "Update ACL benchmark results", cwd=checkout)
            # Recheck after creating the commit, and never overwrite a concurrent
            # gh-pages update: a normal push rejects non-fast-forward updates.
            if source_ref and remote_revision(remote, source_ref) != source_sha:
                print("Source branch advanced during publication; skipping stale results.")
                set_published(False)
                return False
            git("push", "--quiet", remote, f"HEAD:refs/heads/{branch}", cwd=checkout)
            print(f"Saved report and measurements to {branch}.")
        else:
            print("Published report and measurements are already current.")
    set_published(True)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("restore", "publish"):
        command = subparsers.add_parser(name)
        command.add_argument("--remote", help="Git remote URL/path (default: origin URL)")
        command.add_argument("--branch", default="gh-pages")
        command.add_argument("--results", type=Path, default=Path("results"))
        if name == "publish":
            command.add_argument("--site", type=Path, default=Path("site"))
            command.add_argument("--source-ref")
            command.add_argument("--source-sha")
    args = parser.parse_args()
    try:
        remote = args.remote or git("remote", "get-url", "origin").stdout.strip()
        git("check-ref-format", f"refs/heads/{args.branch}")
        if args.command == "restore":
            restore(remote, args.branch, args.results)
        else:
            publish(remote, args.branch, args.site, args.results, args.source_ref, args.source_sha)
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        if isinstance(error, subprocess.CalledProcessError):
            parser.exit(1, f"Git operation failed (exit {error.returncode}): {error.stderr}\n")
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
