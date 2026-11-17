"""Record which top-level Python packages ARLO STUDIO really loads.

Imports every arlo module, the speech-model stack, then runs the test suite, and writes
the top-level module names plus where they came from to tools/studio_modules.json.
Run with ARLO STUDIO's venv python from D:/ArloStudio.
"""
import importlib
import json
import os
import pkgutil
import sys
from pathlib import Path

os.environ.setdefault("ARLO_NO_AUDIO", "1")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.getcwd())
OUT = Path(__file__).with_name("studio_modules.json")

import arlo  # noqa: E402

failed = []
for m in pkgutil.walk_packages(arlo.__path__, "arlo."):
    try:
        importlib.import_module(m.name)
    except Exception as e:  # report, keep going
        failed.append(f"{m.name}: {e}")
for extra in ("faster_whisper", "ctranslate2", "faster_whisper.vad", "onnxruntime", "OpenGL.GL", "OpenGL.WGL",
              "sounddevice", "scipy.signal", "cv2", "av", "PySide6.QtSvg", "PySide6.QtOpenGL",
              "PySide6.QtOpenGLWidgets", "PySide6.QtMultimedia"):
    try:
        importlib.import_module(extra)
    except Exception as e:
        failed.append(f"{extra}: {e}")

if "--tests" in sys.argv:
    import pytest
    pytest.main(["tests", "-q", "-p", "no:cacheprovider"])

tops = {}
for name, mod in list(sys.modules.items()):
    top = name.split(".")[0]
    f = getattr(mod, "__file__", None)
    if top in tops or not f:
        continue
    tops[top] = f
OUT.write_text(json.dumps({"modules": tops, "failed": failed}, indent=1))
print(len(tops), "top-level modules;", len(failed), "failed imports")
print("\n".join(failed))
