"""Command Line Interface for CommitPhalanx."""

import argparse
import sys
import os
from .synthesizer import GitAnalyzer, CommitSynthesizer
from .server import run_server


def main():
    parser = argparse.ArgumentParser(
        prog="commitphalanx",
        description="CommitPhalanx: Autonomous Git Commit Synthesizer, PR Generator & Changelog Studio."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Synthesize Conventional Commit message from local git diff")
    gen_parser.add_argument("--path", "-p", default=".", help="Path to git repository")
    gen_parser.add_argument("--staged", "-s", action="store_true", help="Inspect only staged git changes")

    # Command: pr
    pr_parser = subparsers.add_parser("pr", help="Generate structured Pull Request documentation")
    pr_parser.add_argument("--path", "-p", default=".", help="Path to git repository")
    pr_parser.add_argument("--branch", "-b", default="feature-branch", help="Source branch name")

    # Command: changelog
    ch_parser = subparsers.add_parser("changelog", help="Generate Keep-a-Changelog release documentation")
    ch_parser.add_argument("--path", "-p", default=".", help="Path to git repository")
    ch_parser.add_argument("--version", "-v", default="v0.1.0", help="Release version tag")
    ch_parser.add_argument("--limit", "-l", type=int, default=50, help="Number of recent commits to analyze")
    ch_parser.add_argument("--output", "-o", help="Optional output file path to write changelog")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Start the CommitPhalanx Web Studio")
    serve_parser.add_argument("--port", type=int, default=7099, help="Port to listen on (default: 7099)")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    serve_parser.add_argument("--path", "-p", default=".", help="Path to git repository")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    repo_path = os.path.abspath(args.path) if hasattr(args, "path") else os.getcwd()
    analyzer = GitAnalyzer(repo_path)

    if args.command == "generate":
        diff = analyzer.get_diff(staged_only=args.staged)
        files = analyzer.get_status_summary()
        result = CommitSynthesizer.synthesize_commit(diff, files)
        print("\n" + "=" * 60)
        print("  PROPOSED CONVENTIONAL COMMIT")
        print("=" * 60)
        print(f"Summary: {result['summary']}")
        print("-" * 60)
        print(result["full_message"])
        print("=" * 60 + "\n")

    elif args.command == "pr":
        diff = analyzer.get_diff()
        files = analyzer.get_status_summary()
        pr_doc = CommitSynthesizer.synthesize_pull_request(args.branch, diff, files)
        print("\n" + "=" * 60)
        print(f"  PULL REQUEST: {pr_doc['title']}")
        print("=" * 60)
        print(pr_doc["body"])
        print("=" * 60 + "\n")

    elif args.command == "changelog":
        commits = analyzer.get_commit_history(limit=args.limit)
        changelog = CommitSynthesizer.generate_changelog(commits, version=args.version)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(changelog)
            print(f"[*] Changelog saved to {args.output}")
        else:
            print("\n" + changelog + "\n")

    elif args.command == "serve":
        run_server(port=args.port, host=args.host, repo_path=repo_path)


if __name__ == "__main__":
    main()
