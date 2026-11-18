"""Build the Arlo Maker downloads: a source zip for every app, plus a ready-to-run app zip
where one exists. Everything is licensed GPL-3.0-or-later.

Usage: D:/ArloStudio/.venv/Scripts/python.exe tools/package_sources.py
Writes downloads/<app>-source.zip and downloads/<app>-windows.zip. Build output, virtual
envs, caches, user data, test media and binaries are left out of the source zips.
"""
import fnmatch
import zipfile
from datetime import date
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
DL = SITE / "downloads"
FFMPEG = Path(r"D:\ArloCapture\third_party\ffmpeg")
GPL = (FFMPEG / "LICENSE.txt").read_text(encoding="utf-8")  # the full GPL-3.0 text
assert "GNU GENERAL PUBLIC LICENSE" in GPL and "Version 3" in GPL
YEAR = date.today().year
FFMPEG_VERSION = "n9.0.2-57-gd838f9f9ae (BtbN FFmpeg-Builds, win64 gpl-shared, 2026-11-12)"

SKIP_DIRS = {".venv", ".tmp", "target", "test-out", "__pycache__", ".pytest_cache", ".git",
             "userdata", "userdata_test", "userdata_peek", "testmedia"}
SKIP_FILES = ["*.pyc", "*.exe", "*.dll", "*.pdb", "*.lib", "*.a", "docs/peek*.png", "*.log"]

APPS = {
    "arlo-studio": {
        "root": Path(r"D:\ArloStudio"),
        "name": "ARLO STUDIO",
        "app_dir": SITE / "build" / "ARLO STUDIO",   # made by tools/build_studio_app.py
        "app_files": None,                           # whole folder
        "requires": ("Windows 10 or 11 (64-bit) with an OpenGL 3.3 graphics driver. NVENC (NVIDIA) or\n"
                     "AMF (AMD) makes export fast; it also exports on the CPU.\n\n"
                     "Auto captions need the Whisper small.en speech model (about 460 MB), which is\n"
                     "not included. Everything else works out of the box."),
        "third_party": "arlo/ui/assets/fontawesome: Font Awesome Free icons, CC BY 4.0 "
                       "(see arlo/ui/assets/fontawesome/LICENSE.txt). The app download also bundles "
                       "Python (PSF licence, runtime/LICENSE.txt), PySide6/Qt (LGPL-3.0), PyAV and FFmpeg, "
                       "NumPy, SciPy, OpenCV, faster-whisper, CTranslate2 and ONNX Runtime; each keeps its "
                       "own licence (see the *.dist-info folders in runtime/Lib/site-packages).",
    },
    "ebs": {
        "root": Path(r"D:\EBS-rs"),
        "name": "EBS",
        "app_dir": Path(r"D:\Apps\EBS"),
        "app_files": ["EBS.exe", "ebs.ico", "*.dll"],
        "requires": ("Windows 10 or 11 (64-bit). A graphics card with NVENC (NVIDIA) or AMF (AMD) is\n"
                     "best; EBS also records on the CPU."),
        "third_party": f"EBS uses FFmpeg {FFMPEG_VERSION}, licensed GPL-3.0. "
                       "FFmpeg source: https://ffmpeg.org/download.html and "
                       "https://github.com/BtbN/FFmpeg-Builds (build scripts).",
    },
}


def notice(app):
    return f"""{app['name']}

Copyright (C) {YEAR} Arlo

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See LICENSE.txt for the full text.

In short: you can use it, change it and share it. If you share it (changed or not),
you must share the source code too, under the same licence, and keep this notice.

Third-party parts:
  {app['third_party']}
"""


def readme_app(app, slug):
    return f"""{app['name']} for Windows
{'=' * (len(app['name']) + 12)}

1. Unzip this folder anywhere (for example your Desktop).
2. Double-click {app['name']}.exe to start it.

{app['requires']}

Source code: {slug}-source.zip on Arlo Maker.
Licence: GPL-3.0-or-later (LICENSE.txt). FFmpeg licence: FFmpeg-LICENSE.txt.
FFmpeg version: {FFMPEG_VERSION}
FFmpeg source: https://ffmpeg.org/download.html
"""


def wanted(rel: Path) -> bool:
    s = rel.as_posix()
    return not any(fnmatch.fnmatch(s, pat) or fnmatch.fnmatch(rel.name, pat) for pat in SKIP_FILES)


def walk(root: Path):
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.is_file() and wanted(rel):
            yield p, rel


def report(out, n):
    print(f"{out.name}: {n} files, {out.stat().st_size / 1e6:.1f} MB")


def main():
    for old in DL.glob("LICENSE-PolyForm*"):
        old.unlink()
    (DL / "LICENSE-GPL-3.0.txt").write_text(GPL, encoding="utf-8")
    for slug, app in APPS.items():
        out, top, n = DL / f"{slug}-source.zip", f"{slug}-source", 0
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            z.writestr(f"{top}/LICENSE.txt", GPL)
            z.writestr(f"{top}/NOTICE.txt", notice(app))
            for p, rel in walk(app["root"]):
                z.write(p, f"{top}/{rel.as_posix()}")
                n += 1
        report(out, n)

        if "app_dir" in app:
            out, top, n = DL / f"{slug}-windows.zip", app["name"], 0
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
                z.writestr(f"{top}/LICENSE.txt", GPL)
                z.writestr(f"{top}/FFmpeg-LICENSE.txt", GPL)
                z.writestr(f"{top}/NOTICE.txt", notice(app))
                z.writestr(f"{top}/README.txt", readme_app(app, slug))
                if app["app_files"] is None:
                    files = [(p, p.relative_to(app["app_dir"]).as_posix()) for p in sorted(app["app_dir"].rglob("*"))
                             if p.is_file() and "__pycache__" not in p.parts]
                else:
                    files = [(p, p.name) for p in sorted(app["app_dir"].iterdir()) if p.is_file()
                             and any(fnmatch.fnmatch(p.name, pat) for pat in app["app_files"])]
                for p, rel in files:
                    z.write(p, f"{top}/{rel}")
                    n += 1
            report(out, n)
    # sizes for the site (it cannot ask GitHub for them across sites)
    import json
    sizes = {p.name: p.stat().st_size for p in sorted(DL.glob("*.zip"))}
    (DL / "manifest.json").write_text(json.dumps(sizes, indent=1))
    print("manifest.json:", sizes)


if __name__ == "__main__":
    main()
