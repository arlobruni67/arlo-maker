"""Build a ready-to-run ARLO STUDIO folder: its own Python runtime, only the packages the
app really loads (from studio_modules.py), the app itself and the ARLO STUDIO.exe launcher.

Usage: D:/ArloStudio/.venv/Scripts/python.exe tools/build_studio_app.py
Output: build/ARLO STUDIO/  (zip it with package_sources.py)
"""
import os
import shutil
import stat
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "build" / "ARLO STUDIO"
STUDIO = Path(r"D:\ArloStudio")
BASE = Path(sys.base_prefix)  # the Python install behind ARLO STUDIO's venv (run this with the venv python)
SITES = [STUDIO / ".venv" / "Lib" / "site-packages", BASE / "Lib" / "site-packages"]  # venv wins

# top-level packages ARLO STUDIO loads (tools/studio_modules.json, minus pytest and .pth helpers)
PACKAGES = """PIL _cffi_backend anyio av certifi charset_normalizer click colorama ctranslate2 cv2
faster_whisper filelock h11 h2 hpack httpcore httpx huggingface_hub hyperframe idna numpy onnxruntime
pygments rich scipy sniffio tokenizers tqdm typing_extensions yaml zstandard
OpenGL PySide6 shiboken6 sounddevice _sounddevice _sounddevice_data""".split()
# packages whose metadata other packages read with importlib.metadata
DIST_NAMES = {"PIL": "pillow", "cv2": "opencv_python", "yaml": "PyYAML", "OpenGL": "PyOpenGL",
              "_sounddevice_data": None, "_sounddevice": None, "_cffi_backend": "cffi"}

STD_SKIP = {"site-packages", "test", "idlelib", "turtledemo", "ensurepip", "tkinter", "lib2to3"}
DLL_SKIP = ("_tkinter", "tcl", "tk")
IGNORE = shutil.ignore_patterns("tests", "test", "*.pdb", "*.lib", "include")


def find(name):
    for site in SITES:
        for cand in (site / name, *site.glob(name + ".py"), *site.glob(name + ".*.pyd"), *site.glob(name + ".pyd")):
            if cand.exists():
                return site, cand
    raise SystemExit(f"package not found: {name}")


def dist_info(site, name):
    dn = DIST_NAMES.get(name, name)
    if dn is None:
        return []
    key = dn.lower().replace("-", "_")
    return [p for p in site.glob("*.dist-info") if p.name.lower().replace("-", "_").startswith(key + "-")]


def copy(src: Path, dst: Path, ignore=None):
    if src.is_dir():
        shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


QT_KEEP = {"QtCore", "QtGui", "QtWidgets", "QtSvg", "QtOpenGL", "QtOpenGLWidgets"}


def pe_imports(path: Path):
    """DLL names a PE file imports (lower case)."""
    import struct
    d = path.read_bytes()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    nsec, optsz = struct.unpack_from("<H", d, pe + 6)[0], struct.unpack_from("<H", d, pe + 20)[0]
    opt = pe + 24
    rva = struct.unpack_from("<I", d, opt + 120)[0]
    secs = [struct.unpack_from("<8sIIII", d, opt + optsz + i * 40) for i in range(nsec)]

    def off(r):
        for _n, vs, va, rs, rp in secs:
            if va <= r < va + max(vs, rs):
                return r - va + rp
    out, o = set(), off(rva)
    while o is not None:
        e = struct.unpack_from("<5I", d, o)
        if e[3] == 0:
            break
        no = off(e[3])
        out.add(d[no:d.index(b"\0", no)].decode().lower())
        o += 20
    return out


def trim(sp: Path):
    """Drop Qt parts and OpenCV video IO that ARLO STUDIO never uses."""
    for f in sp.glob("cv2/opencv_videoio_ffmpeg*.dll"):
        f.unlink()
    q = sp / "PySide6"
    for d in ("qml", "translations", "resources", "examples", "glue", "include", "typesystems", "scripts"):
        shutil.rmtree(q / d, ignore_errors=True)
    for f in q.glob("*.exe"):
        f.unlink()
    for f in list(q.glob("Qt*.pyd")) + list(q.glob("Qt*.pyi")):
        if f.name.split(".")[0] not in QT_KEEP:
            f.unlink()
    for plug in list((q / "plugins").iterdir()):
        if plug.name not in ("platforms", "imageformats", "styles", "iconengines", "platformthemes"):
            shutil.rmtree(plug)
    # keep only Qt6*.dll reachable from what is left (plus the software OpenGL fallback)
    roots = [*q.glob("*.pyd"), *(q / "plugins").rglob("*.dll"), *(sp / "shiboken6").glob("*.pyd")]
    dlls = {p.name.lower(): p for p in q.glob("*.dll")}
    keep, todo = set(), list(roots)
    while todo:
        for name in pe_imports(todo.pop()):
            if name in dlls and name not in keep:
                keep.add(name)
                todo.append(dlls[name])
    for name, p in dlls.items():
        if name.startswith("qt6") and name not in keep:
            p.unlink()


def _force(func, path, _exc):
    """rmtree error handler: clear read-only and try once more."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def wipe(path: Path):
    """Delete a folder even while antivirus or the indexer briefly holds files in it.
    The old build is renamed aside first, so the new build never trips over it."""
    for old in path.parent.glob(path.name + ".old-*"):
        shutil.rmtree(old, onexc=_force)
    if not path.exists():
        return
    aside = path.with_name(f"{path.name}.old-{int(time.time())}")
    for _ in range(10):
        try:
            path.rename(aside)
            break
        except OSError:
            time.sleep(1)
    else:
        raise SystemExit(f"{path} is in use. Close ARLO STUDIO (and any Explorer window inside it), then run again.")
    for _ in range(5):
        shutil.rmtree(aside, onexc=_force)
        if not aside.exists():
            return
        time.sleep(1)
    print(f"note: could not fully delete {aside.name}; it will be removed on the next build")


def main():
    wipe(OUT)
    rt = OUT / "runtime"
    # 1. Python runtime
    for f in ("python.exe", "pythonw.exe", "python3.dll", "python313.dll", "vcruntime140.dll",
              "vcruntime140_1.dll", "LICENSE.txt"):
        copy(BASE / f, rt / f)
    for p in (BASE / "DLLs").iterdir():
        if not p.name.lower().startswith(DLL_SKIP):
            copy(p, rt / "DLLs" / p.name)
    for p in (BASE / "Lib").iterdir():
        if p.name not in STD_SKIP:
            copy(p, rt / "Lib" / p.name)
    # 2. packages
    sp = rt / "Lib" / "site-packages"
    for name in PACKAGES:
        site, src = find(name)
        copy(src, sp / src.name, IGNORE if src.is_dir() else None)
        libs = site / (name + ".libs")
        if libs.is_dir():
            copy(libs, sp / libs.name)
        for d in dist_info(site, name):
            copy(d, sp / d.name)
    trim(sp)
    # 3. the app
    copy(STUDIO / "arlo", OUT / "arlo", shutil.ignore_patterns("__pycache__", "*.pyc"))
    copy(STUDIO / "native" / "arlo-export" / "dist", OUT / "native" / "arlo-export" / "dist")
    copy(HERE / "launcher" / "ARLO STUDIO.exe", OUT / "ARLO STUDIO.exe")
    copy(STUDIO / "README.md", OUT / "docs" / "README.md")
    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"built {OUT}  {size / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
