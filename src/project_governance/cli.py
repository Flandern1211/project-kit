"""Command-line interface for Project Governance Kit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from .checks import run_checks
from .git_context import inspect_git
from .handoff import update_handoff
from .records import create_record, update_work_index
from .scaffold import adopt_project, init_project


def _root(value: str) -> Path:
    return Path(value).resolve()


def _emit(value: Any, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                print(f"{key}: {json.dumps(item, ensure_ascii=False, sort_keys=True)}")
            else:
                print(f"{key}: {item}")
    else:
        print(value)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pgk", description="Project Governance Kit")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create missing governance files")
    init.add_argument("--root", default=".")
    init.add_argument("--project-name")
    init.add_argument("--profile", default="standard")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--json", action="store_true")

    for name, help_text in (("adopt", "inspect an existing project"), ("doctor", "inspect project health"), ("check", "validate records and links")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--root", default=".")
        command.add_argument("--json", action="store_true")

    new = commands.add_parser("new", help="create a governance record")
    new.add_argument("kind", choices=("requirement", "design", "decision", "task", "bug", "verification"))
    new.add_argument("record_id")
    new.add_argument("title")
    new.add_argument("--root", default=".")
    new.add_argument("--status", default="draft")
    new.add_argument("--related", action="append", default=[])
    new.add_argument("--dry-run", action="store_true")
    new.add_argument("--json", action="store_true")

    index = commands.add_parser("index", help="update the generated work index")
    index.add_argument("--root", default=".")
    index.add_argument("--dry-run", action="store_true")
    index.add_argument("--json", action="store_true")

    handoff = commands.add_parser("handoff", help="update a task handoff section")
    handoff.add_argument("task_id")
    handoff.add_argument("--root", default=".")
    handoff.add_argument("--next-action", required=True)
    handoff.add_argument("--status")
    handoff.add_argument("--verification")
    handoff.add_argument("--blocker", action="append", default=[])
    handoff.add_argument("--dry-run", action="store_true")
    handoff.add_argument("--json", action="store_true")
    return parser


def _doctor(root: Path) -> dict[str, object]:
    checks = run_checks(root).as_dict()
    adoption = adopt_project(root).as_dict()
    try:
        git = inspect_git(root)
        git_value = {
            "branch": git.branch,
            "head": git.head,
            "dirty": git.dirty,
            "recent_commits": list(git.recent_commits),
        }
    except ValueError as exc:
        git_value = {"available": False, "error": str(exc)}
    return {"checks": checks, "adoption": adoption, "git": git_value}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    root = _root(args.root)
    try:
        if args.command == "init":
            result = init_project(root, project_name=args.project_name, profile=args.profile, dry_run=args.dry_run)
            _emit(result.as_dict(), as_json=args.json)
            return 0
        if args.command == "adopt":
            _emit(adopt_project(root).as_dict(), as_json=args.json)
            return 0
        if args.command == "check":
            result = run_checks(root)
            _emit(result.as_dict(), as_json=args.json)
            return 0 if result.ok else 1
        if args.command == "doctor":
            result = _doctor(root)
            _emit(result, as_json=args.json)
            return 0 if bool(result["checks"]["ok"]) else 1
        if args.command == "new":
            path = create_record(root, args.kind, args.record_id, args.title, status=args.status, related=args.related, dry_run=args.dry_run)
            _emit({"path": path.relative_to(root).as_posix(), "id": args.record_id}, as_json=args.json)
            return 0
        if args.command == "index":
            path = update_work_index(root, dry_run=args.dry_run)
            _emit({"path": path.relative_to(root).as_posix()}, as_json=args.json)
            return 0
        if args.command == "handoff":
            path = update_handoff(root, args.task_id, next_action=args.next_action, status=args.status, verification=args.verification, blockers=args.blocker, dry_run=args.dry_run)
            _emit({"path": path.relative_to(root).as_posix(), "task_id": args.task_id}, as_json=args.json)
            return 0
        parser.error(f"unknown command: {args.command}")
    except (OSError, ValueError) as exc:
        print(f"pgk: {exc}", file=__import__("sys").stderr)
        return 2
    return 2


__all__ = ["main"]
