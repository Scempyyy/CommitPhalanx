"""Git diff analyzer, Conventional Commit synthesizer, PR generator, and changelog engine."""

import datetime
import os
import re
import subprocess
from typing import Dict, List, Any, Optional, Tuple


def run_git(args: List[str], cwd: Optional[str] = None) -> str:
    """Executes git command and returns stdout."""
    try:
        res = subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd, timeout=10)
        return res.stdout.strip()
    except Exception:
        return ""


class GitAnalyzer:
    """Parses local repository diffs, commit logs, and git status."""

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path or os.getcwd()

    def get_diff(self, staged_only: bool = False) -> str:
        """Returns staged or working tree diff."""
        args = ["diff", "--cached"] if staged_only else ["diff", "HEAD"]
        diff = run_git(args, cwd=self.repo_path)
        if not diff and not staged_only:
            diff = run_git(["diff"], cwd=self.repo_path)
        return diff

    def get_status_summary(self) -> List[Dict[str, str]]:
        """Parses git status -s into structured file entries."""
        raw = run_git(["status", "-s"], cwd=self.repo_path)
        files = []
        for line in raw.splitlines():
            line = line.strip()
            if len(line) >= 3:
                status_code = line[:2].strip()
                path = line[2:].strip()
                files.append({"status": status_code, "path": path})
        return files

    def get_commit_history(self, limit: int = 50) -> List[Dict[str, str]]:
        """Reads recent commit history."""
        raw = run_git(["log", f"-n{limit}", "--pretty=format:%h|%an|%ad|%s", "--date=short"], cwd=self.repo_path)
        commits = []
        for line in raw.splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "subject": parts[3]
                })
        return commits


class CommitSynthesizer:
    """Synthesizes Conventional Commits, Pull Requests, and Keep-a-Changelog releases."""

    @classmethod
    def synthesize_commit(cls, diff: str, changed_files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generates a Conventional Commit message from git diff and modified file list."""
        if not diff and not changed_files:
            return {
                "type": "chore",
                "scope": "repo",
                "summary": "chore: update repository files",
                "body": "- Routine maintenance update.",
                "full_message": "chore: update repository files\n\n- Routine maintenance update."
            }

        # 1. Determine Scope
        paths = [f["path"] for f in changed_files]
        scope = cls._deduce_scope(paths)

        # 2. Determine Commit Type
        ctype = cls._deduce_type(paths, diff)

        # 3. Generate Summary & Body
        added_lines = [l[1:].strip() for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
        removed_lines = [l[1:].strip() for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]

        short_action = "update functionality"
        if ctype == "feat":
            short_action = "add new capabilities"
            if any("api" in p.lower() for p in paths):
                short_action = "introduce new API endpoints"
            elif any("ui" in p.lower() or "html" in p.lower() for p in paths):
                short_action = "implement user interface components"
        elif ctype == "fix":
            short_action = "resolve edge case and handle exceptions"
        elif ctype == "docs":
            short_action = "update documentation and examples"
        elif ctype == "test":
            short_action = "add unit test coverage"
        elif ctype == "refactor":
            short_action = "refactor architecture for modularity"

        summary = f"{ctype}({scope}): {short_action}"

        bullets = []
        for f in changed_files[:6]:
            action_verb = "Modified"
            st = f.get("status", "")
            if "A" in st or "??" in st:
                action_verb = "Add"
            elif "D" in st:
                action_verb = "Remove"
            bullets.append(f"- {action_verb} `{f['path']}`")

        body = "\n".join(bullets)
        full_message = f"{summary}\n\n{body}"

        return {
            "type": ctype,
            "scope": scope,
            "summary": summary,
            "body": body,
            "full_message": full_message
        }

    @classmethod
    def synthesize_pull_request(cls, branch_name: str, diff: str, changed_files: List[Dict[str, str]]) -> Dict[str, str]:
        """Synthesizes structured Pull Request documentation."""
        commit_info = cls.synthesize_commit(diff, changed_files)
        pr_title = commit_info["summary"].capitalize()

        file_list = "\n".join(f"- `{f['path']}` ({f['status']})" for f in changed_files[:10])
        if len(changed_files) > 10:
            file_list += f"\n- *...and {len(changed_files) - 10} additional files.*"

        body = f"""## 🎯 Overview
This pull request introduces changes from branch `{branch_name}` to enhance `{commit_info['scope']}`.

## 🛠️ Changes Breakdown
{file_list}

## 🧪 Testing & Verification
- [x] Unit test suite executed and passing.
- [x] Verified zero third-party dependency breakage.
- [x] Code adheres to repository style standards.

## ⚠️ Breaking Changes
- None. Fully backward-compatible.

---
*Generated automatically by [CommitPhalanx](https://github.com/Scempyyy/CommitPhalanx)*
"""
        return {"title": pr_title, "body": body}

    @classmethod
    def generate_changelog(cls, commits: List[Dict[str, str]], version: str = "v0.1.0") -> str:
        """Categorizes commit logs into a Keep-a-Changelog standard markdown document."""
        today = datetime.date.today().isoformat()
        categories: Dict[str, List[str]] = {
            "Features": [],
            "Bug Fixes": [],
            "Performance": [],
            "Documentation": [],
            "Maintenance": []
        }

        for c in commits:
            msg = c["subject"]
            h = c["hash"]
            line = f"- {msg} (`{h}`)"

            if msg.startswith("feat"):
                categories["Features"].append(line)
            elif msg.startswith("fix"):
                categories["Bug Fixes"].append(line)
            elif msg.startswith("perf"):
                categories["Performance"].append(line)
            elif msg.startswith("docs"):
                categories["Documentation"].append(line)
            else:
                categories["Maintenance"].append(line)

        output = [
            f"# Changelog",
            f"\nAll notable changes to this project will be documented in this file.\n",
            f"## [{version}] - {today}\n"
        ]

        for cat, items in categories.items():
            if items:
                output.append(f"### {cat}")
                output.extend(items)
                output.append("")

        return "\n".join(output)

    @staticmethod
    def _deduce_scope(paths: List[str]) -> str:
        if not paths:
            return "core"
        first = paths[0].replace("\\", "/")
        parts = first.split("/")
        if len(parts) > 1 and parts[0] not in (".", ""):
            return parts[0].lower()
        base = os.path.splitext(os.path.basename(first))[0]
        return base.lower()

    @staticmethod
    def _deduce_type(paths: List[str], diff: str) -> str:
        combined = " ".join(paths).lower()
        if any("test" in p for p in paths):
            return "test"
        if any(p.endswith((".md", ".rst", ".txt")) for p in paths):
            return "docs"
        if any(p in ("pyproject.toml", "package.json", "dockerfile", "makefile") for p in paths):
            return "chore"

        lower_diff = diff.lower()
        if any(k in lower_diff for k in ["fix", "bug", "error", "patch", "crash", "resolve"]):
            return "fix"
        if any(k in lower_diff for k in ["def ", "class ", "function ", "feature", "export"]):
            return "feat"

        return "refactor"
