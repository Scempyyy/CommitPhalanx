# CommitPhalanx ⚡

> **Autonomous Git Commit Synthesizer, PR Generator & Keep-a-Changelog Studio.**
> Built with zero third-party dependencies using standard Python 3.

[![CI](https://github.com/Scempyyy/CommitPhalanx/actions/workflows/ci.yml/badge.svg)](https://github.com/Scempyyy/CommitPhalanx/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)

---

## ⚡ What is CommitPhalanx?

Crafting semantic, conventional git commit messages and PR descriptions is tedious. **CommitPhalanx** inspects your local git repository diffs, staged changes, and commit logs to automatically synthesize:
- **Conventional Commits:** Adhering strictly to `feat(scope): ...`, `fix(scope): ...`, `test(scope): ...`, etc.
- **Pull Request Documentation:** Fully-structured Markdown with change breakdowns, testing checkboxes, and breaking change audits.
- **Keep-a-Changelog Documentation:** Grouping commits into clean categorized releases (Features, Bug Fixes, Documentation, Maintenance).
- **Web Studio:** An embedded local web console with interactive diff viewing, one-click copy, and live synthesis.

---

## 🚀 Quick Start

### 1. Run without installation
```bash
git clone https://github.com/Scempyyy/CommitPhalanx.git
cd CommitPhalanx
chmod +x commitphalanx.py
```

### 2. Synthesize Conventional Commit from current working diff
```bash
./commitphalanx.py generate
```

### 3. Generate Pull Request description
```bash
./commitphalanx.py pr --branch my-feature-branch
```

### 4. Generate Keep-a-Changelog release doc
```bash
./commitphalanx.py changelog --version v1.0.0 --output CHANGELOG.md
```

### 5. Launch the Web Studio
```bash
./commitphalanx.py serve --port 7099
```
Open [http://127.0.0.1:7099](http://127.0.0.1:7099) in your browser.

---

## 🛠️ CLI Reference

```
usage: commitphalanx [-h] {generate,pr,changelog,serve} ...

Subcommands:
  generate    Synthesize Conventional Commit message from local git diff
              Options: --path PATH, --staged
  pr          Generate structured Pull Request documentation
              Options: --path PATH, --branch BRANCH
  changelog   Generate Keep-a-Changelog release documentation
              Options: --path PATH, --version VERSION, --limit LIMIT, --output FILE
  serve       Start the CommitPhalanx Web Studio
              Options: --port PORT, --host HOST, --path PATH
```

---

## 🧪 Testing

Run the zero-dependency test suite:
```bash
python3 -m unittest discover tests -v
```

---

## 📄 License
MIT License. Crafted with precision for high-efficiency development workflows.
