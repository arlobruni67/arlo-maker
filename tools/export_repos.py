"""Export a clean copy of each app's code (same filter as the source zips, plus LICENSE and
NOTICE) into build/repos/<app>/, ready to commit and push to its GitHub repo.

Usage: D:/ArloStudio/.venv/Scripts/python.exe tools/export_repos.py
The app folders themselves are not touched. An existing .git folder in the export is kept,
so re-running and committing gives a normal update.
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_sources import APPS, GPL, SITE, notice, walk  # noqa: E402

OUT = SITE / "build" / "repos"

DOCS = SITE / "repo-docs"   # README and user guides, copied over each export


def main():
    for slug, app in APPS.items():
        dst = OUT / slug
        dst.mkdir(parents=True, exist_ok=True)
        for p in dst.iterdir():                 # clear everything but git history
            if p.name != ".git":
                shutil.rmtree(p) if p.is_dir() else p.unlink()
        n = 0
        for p, rel in walk(app["root"]):
            t = dst / rel
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, t)
            n += 1
        (dst / "LICENSE.txt").write_text(GPL, encoding="utf-8")
        (dst / "NOTICE.txt").write_text(notice(app), encoding="utf-8")
        extra = DOCS / slug
        if extra.is_dir():
            shutil.copytree(extra, dst, dirs_exist_ok=True)
        print(f"{slug}: {n} files -> {dst}")


if __name__ == "__main__":
    main()
