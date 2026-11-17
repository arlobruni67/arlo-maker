# ARLO STUDIO

A video editor for Windows that mixes simple, CapCut-style editing with pro pages for colour, audio and export.

![ARLO STUDIO](docs/screenshot_theme_blue.png)

* Timeline with Video, Overlay and Sound tracks, nested sequences, markers and snapping
* 54 transitions, 16 effects, green screen, 44 stickers, titles and auto captions
* Colour page with wheels, curves, LUTs and scopes
* Audio page with a mixer, EQ, compressor and limiter
* GPU compositing and NVENC / AMF export with a render queue

## Download

Get the ready-to-run app from **[Arlo Maker](https://arlobruni67.github.io/arlo-maker/)**:
unzip it and double-click `ARLO STUDIO.exe`.

## Documentation

* **[User guide](docs/USER_GUIDE.md)**: install, the pages, editing, captions, colour, audio, export, shortcuts
* [Features](docs/FEATURES.md): everything the app does, how each part is tested, and the known limits
* [Architecture](docs/ARCHITECTURE.md): how the engine is built
* [Project format](docs/PROJECT_FORMAT.md): the `.arlo` file format

## Run from source

Python 3.13 on Windows with PySide6, PyAV, NumPy, SciPy, OpenCV, PyOpenGL, sounddevice and faster-whisper.

```
python -m venv .venv
.venv\Scripts\pip install PySide6-Essentials av numpy scipy opencv-python PyOpenGL sounddevice faster-whisper
.venv\Scripts\python.exe -m arlo.app
```

Tests: `.venv\Scripts\python.exe -m pytest tests` (make the test media first with `tools\make_testmedia.py`).

Icons: [Font Awesome Free](https://fontawesome.com) SVGs in `arlo/ui/assets/fontawesome` (CC BY 4.0).

## Licence

GPL-3.0-or-later. See [LICENSE.txt](LICENSE.txt) and [NOTICE.txt](NOTICE.txt).
