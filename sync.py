#!/usr/bin/env python3
"""Sync skills/<name>/ from each upstream repo, so this collection never drifts from the source.

    python sync.py            pull every upstream at its default branch, copy skills/<name>/ and
                              docs/<name>.png here, and write skills.lock.json
    python sync.py --check    exit 1 if a sync would change anything (CI)
    python sync.py --local    copy from sibling checkouts (../<name>) instead of cloning

Each upstream repo is the source of truth. Edit skills there, not here. Stdlib + git only.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "skills.lock.json"
UPSTREAM = ["skill-rollcall", "mcp-rollcall", "settings-effective", "git-attribution"]
OWNER = "Londopy"


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, encoding="utf-8", check=True).stdout.strip()


def fetch(name: str, local: bool, tmp: Path) -> Path:
    if local:
        p = ROOT.parent / name
        if not (p / "skills" / name / "SKILL.md").exists():
            sys.exit(f"--local: {p} is not a checkout of {name}")
        return p
    dest = tmp / name
    subprocess.run(["git", "clone", "--quiet", "--depth", "1", f"https://github.com/{OWNER}/{name}.git", str(dest)], check=True)
    return dest


def version_of(src: Path) -> str:
    try:
        return json.loads((src / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("version", "?")
    except (OSError, ValueError):
        return "?"


def tree_differs(a: Path, b: Path) -> bool:
    if not a.exists() or not b.exists():
        return True
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__", ".DS_Store"])
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return True
    return any(tree_differs(a / d, b / d) for d in cmp.common_dirs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report drift, change nothing, exit 1 if any")
    ap.add_argument("--local", action="store_true", help="use ../<name> checkouts instead of cloning")
    a = ap.parse_args()

    old_lock = json.loads(LOCK.read_text(encoding="utf-8")) if LOCK.exists() else {}
    new_lock: dict = {}
    changed: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in UPSTREAM:
            src = fetch(name, a.local, Path(tmp))
            sha = git("rev-parse", "HEAD", cwd=src)
            skill_src, skill_dst = src / "skills" / name, ROOT / "skills" / name
            demo_src, demo_dst = src / "docs" / "demo.png", ROOT / "docs" / f"{name}.png"
            drift = tree_differs(skill_src, skill_dst) or not demo_dst.exists() or not filecmp.cmp(demo_src, demo_dst, shallow=False)
            new_lock[name] = {"repo": f"{OWNER}/{name}", "commit": sha, "version": version_of(src),
                              "synced": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
            if drift:
                changed.append(f"{name} @ {sha[:7]} (v{new_lock[name]['version']})")
                if not a.check:
                    if skill_dst.exists():
                        shutil.rmtree(skill_dst)
                    shutil.copytree(skill_src, skill_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                    demo_dst.parent.mkdir(exist_ok=True)
                    shutil.copy2(demo_src, demo_dst)
            elif name in old_lock:
                new_lock[name]["synced"] = old_lock[name].get("synced", new_lock[name]["synced"])

    if a.check:
        if changed:
            print("out of sync with upstream:\n  " + "\n  ".join(changed) + "\nrun: python sync.py")
            return 1
        print(f"in sync: {', '.join(UPSTREAM)}")
        return 0
    LOCK.write_text(json.dumps(new_lock, indent=2) + "\n", encoding="utf-8")
    print(("synced:\n  " + "\n  ".join(changed)) if changed else "nothing changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
