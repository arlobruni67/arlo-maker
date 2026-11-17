"""Render good-looking demo footage and music for the ARLO STUDIO screenshots on the site.

Same file roles as ArloStudio/tools/make_testmedia.py, but pretty: sunset beach, blue sky,
neon bokeh, northern lights, a city at dusk, a balloon photo, a mountain lake, a drum loop
and a piano melody. names.json maps the test-media names to the pretty file names.

Usage: D:/ArloStudio/.venv/Scripts/python.exe tools/make_showcase_media.py
Writes to tools/media/. Needs ffmpeg on PATH.
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import cv2
import numpy as np

OUT = Path(__file__).resolve().parent / "media"
OUT.mkdir(exist_ok=True)
SR = 48000
rng = np.random.default_rng(7)

NAMES = {
    "clip_1080p30.mp4": "Sunset Beach.mp4",
    "clip_720p60.mov": "Blue Sky.mov",
    "clip_bars.webm": "Neon Lights.webm",
    "clip_small.avi": "Northern Lights.avi",
    "clip_noaudio.mkv": "City Dusk.mkv",
    "tone.wav": "Piano.wav",
    "beats.mp3": "Drum Loop.mp3",
    "still.png": "Balloon.png",
    "still.jpg": "Mountain Lake.jpg",
    "speech.wav": "speech.wav",
    "Bars insert": "Neon insert",
}


# ---------------------------------------------------------------- helpers
def grid(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    return x / w, y / h


def lerp_stops(t, stops):
    """t: array 0..1, stops: [(pos, (r,g,b)), ...] -> HxWx3 float 0..1"""
    pos = np.array([p for p, _ in stops], np.float32)
    cols = np.array([c for _, c in stops], np.float32) / 255.0
    out = np.empty(t.shape + (3,), np.float32)
    for k in range(3):
        out[..., k] = np.interp(t, pos, cols[:, k])
    return out


def to8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def encode(path, frames, w, h, fps, vargs, audio=None, aargs=()):
    """frames: generator of HxWx3 uint8 RGB at w x h."""
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-"]
    if audio is not None:
        cmd += ["-i", str(audio)]
    cmd += list(vargs) + list(aargs) + ["-shortest" if audio is not None else "-an", str(path)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f"ffmpeg failed for {path}")
    print("ok", path.name)


def render(fn, w, h, n, scale=2):
    """Render at reduced size and upscale (soft gradients look the same, 4x faster)."""
    lw, lh = w // scale, h // scale
    x, y = grid(lw, lh)
    for i in range(n):
        img = fn(x, y, i / n, lw, lh)
        if scale != 1:
            img = cv2.resize(img, (w, h), interpolation=cv2.INTER_CUBIC)
        # tiny grain so it reads as footage, not a flat render
        yield to8(img + rng.normal(0, 0.008, (h, w, 1)).astype(np.float32))


# ---------------------------------------------------------------- scenes
def sunset(x, y, t, w, h):
    hor = 0.6
    sky = lerp_stops(y / hor, [(0, (58, 34, 110)), (0.45, (190, 70, 130)), (0.8, (250, 140, 90)), (1, (255, 205, 130))])
    sx, sy, sr = 0.5 + 0.03 * t, 0.47 + 0.06 * t, 0.075
    d = np.hypot((x - sx) * w / h, y - sy)
    sky += np.exp(-(d / 0.22) ** 2)[..., None] * np.array([1, .55, .3], np.float32) * 0.55
    sky = np.where((d < sr)[..., None], np.array([1, .93, .75], np.float32), sky)
    # clouds: soft horizontal streaks
    streak = np.sin(y * 28 + np.sin(x * 4 + t * 2) * 1.2) * 0.5 + 0.5
    sky += (streak ** 6 * np.exp(-((y - 0.3) / 0.1) ** 2))[..., None] * np.array([.12, .06, .08], np.float32)
    sea_t = np.clip((y - hor) / (1 - hor), 0, 1)
    sea = lerp_stops(sea_t, [(0, (205, 100, 120)), (0.25, (90, 50, 110)), (1, (20, 18, 50))])
    shimmer = np.sin(sea_t ** 0.6 * 140 + np.sin(x * 25 + t * 12) * 1.5 - t * 25) * 0.5 + 0.5
    width = 0.03 + sea_t * 0.18
    glint = np.exp(-((x - sx) / width) ** 2) * shimmer ** 3 * (1 - sea_t * 0.6)
    sea += glint[..., None] * np.array([1, .75, .45], np.float32) * 0.9
    img = np.where((y < hor)[..., None], sky, sea)
    # palm silhouettes left and right
    for px, lean in ((0.08, 0.12), (0.93, -0.1)):
        trunk = np.abs(x - (px + lean * (1 - y) ** 2)) < 0.006 + 0.004 * y
        img[(trunk & (y > 0.25))] *= 0.08
        for a in np.linspace(0, np.pi * 2, 7, endpoint=False):
            cx, cy = px + lean * 0.56, 0.27
            ang = a + 0.06 * np.sin(t * 6 + a)
            r = np.hypot((x - cx) * w / h, y - cy)
            th = np.arctan2(y - cy, (x - cx) * w / h)
            droop = th - ang - 0.9 * (r / 0.16) ** 2 * np.cos(ang)
            leaf = (np.abs(np.angle(np.exp(1j * droop))) < 0.22 * (1 - r / 0.17)) & (r < 0.17)
            img[leaf] *= 0.08
    v = 1 - 0.35 * (((x - .5) * 1.4) ** 2 + ((y - .5) * 1.2) ** 2)
    return img * v[..., None]


def sky_clouds(x, y, t, w, h):
    img = lerp_stops(y, [(0, (90, 170, 230)), (0.55, (165, 215, 245)), (1, (225, 242, 252))])
    ar = w / h
    for k in range(9):
        cx = ((k * 0.23 + t * (0.08 + 0.02 * (k % 3))) % 1.4) - 0.2
        cy = 0.12 + (k * 0.137 % 0.4)
        for j in range(5):
            bx, by = cx + (j - 2) * 0.045, cy + (0.02 if j % 2 else -0.01)
            r = 0.05 + 0.02 * ((j * 7 + k) % 3)
            d = np.hypot((x - bx) * ar, y - by)
            a = np.clip(1 - d / r, 0, 1) ** 0.6
            img = img * (1 - a[..., None]) + a[..., None] * np.array([1, 1, 1], np.float32)
    hills = (((120, 165, 210), 0.6, 0.12, 6), ((90, 160, 150), 0.7, 0.08, 9), ((70, 145, 95), 0.82, 0.06, 13))
    for layer, (col, base, amp, f) in enumerate(hills):
        ridge = base - amp * (np.sin(x * f + layer) * 0.6 + np.sin(x * f * 2.3 + 1.7) * 0.3 + np.abs(np.sin(x * f * 0.5)) * 0.4)
        c = np.array(col, np.float32) / 255
        img = np.where((y > ridge)[..., None], c * (1.05 - 0.25 * (y - ridge))[..., None], img)
    return img


BOKEH = [(rng.random(), rng.random(), 0.02 + rng.random() * 0.07, rng.random() * 6.28, rng.integers(0, 3)) for _ in range(46)]


def neon(x, y, t, w, h):
    img = lerp_stops(y, [(0, (14, 10, 40)), (1, (30, 16, 60))])
    pal = np.array([[0.3, 0.85, 1.0], [1.0, 0.35, 0.8], [0.6, 0.45, 1.0]], np.float32)
    ar = w / h
    for bx, by, r, ph, c in BOKEH:
        cx = (bx + 0.05 * np.sin(t * 6.28 + ph)) % 1
        cy = (by - t * 0.1) % 1
        d = np.hypot((x - cx) * ar, y - cy)
        a = np.clip((r - d) / 0.006, 0, 1) * (0.35 + 0.25 * np.sin(t * 12 + ph))
        img += a[..., None] * pal[c]
    return img


STARS = rng.random((260, 3))


def aurora(x, y, t, w, h):
    img = lerp_stops(y, [(0, (6, 10, 30)), (0.7, (14, 30, 60)), (1, (20, 40, 60))])
    for sx, sy, b in STARS:
        d = np.hypot((x - sx) * w, (y - sy * 0.7) * h)
        img += (np.exp(-d * d / 1.2) * (0.4 + 0.6 * b))[..., None]
    for k, (col, off) in enumerate((((0.2, 1.0, 0.6), 0.0), ((0.4, 0.6, 1.0), 1.7), ((0.8, 0.4, 1.0), 3.1))):
        center = 0.32 + 0.08 * np.sin(x * 5 + t * 4 + off) + 0.04 * np.sin(x * 13 - t * 6 + off)
        curtain = np.exp(-((y - center) / 0.05) ** 2) + 0.5 * np.clip((center - y) / 0.25, 0, 1) * (y < center)
        rays = 0.6 + 0.4 * np.sin(x * 90 + np.sin(x * 9 + t * 5) * 3) ** 2
        img += (curtain * rays * (0.55 if k == 0 else 0.3))[..., None] * np.array(col, np.float32)
    # pine trees
    for k in range(18):
        tx, th, tw = k / 17 + 0.02 * np.sin(k * 3), 0.25 + 0.12 * ((k * 5) % 3) / 2, 0.035
        tree = (y > 1 - th) & (np.abs(x - tx) < tw * (y - (1 - th)) / th * 1.0)
        img[tree] = np.array([0.02, 0.04, 0.06], np.float32)
    img[y > 0.93] = np.array([0.02, 0.04, 0.06], np.float32)
    return img


def city(x, y, t, w, h):
    img = lerp_stops(y, [(0, (40, 60, 120)), (0.5, (230, 120, 140)), (0.75, (255, 190, 140)), (1, (60, 50, 80))])
    for layer, (dark, n) in enumerate(((0.45, 14), (0.15, 22))):
        idx = np.floor(x * n + layer * 0.5)
        hgt = 0.45 + 0.25 * ((np.sin(idx * 12.9898 + layer) * 43758.5453) % 1)
        bldg = y > 1 - hgt * (0.7 + 0.3 * layer)
        img[bldg] = img[bldg] * dark
        if layer == 1:
            win = bldg & ((np.floor(x * n * 6) % 2) == 0) & ((np.floor(y * 60) % 2) == 0)
            lit = ((np.sin(np.floor(x * n * 6) * 7.1 + np.floor(y * 60) * 3.3) * 999) % 1) > 0.55 + 0.1 * np.sin(t * 6)
            img[win & lit] = np.array([1, .85, .5], np.float32)
    return img


# ---------------------------------------------------------------- stills
def balloon_photo():
    w = h = 1000
    x, y = grid(w, h)
    img = lerp_stops(y, [(0, (110, 190, 240)), (1, (215, 238, 252))])
    d = np.hypot(x - 0.5, (y - 0.4) * 0.85)
    ball = d < 0.22
    stripe = (np.floor((np.arctan2(y - 0.4, x - 0.5) + 3.15) / 0.35) % 2) == 0
    cols = np.where(stripe[..., None], np.array([1, .45, .45], np.float32), np.array([1, .85, .35], np.float32))
    shade = (1 - 0.6 * np.clip((x - 0.42) / 0.3, 0, 1))[..., None]
    img = np.where(ball[..., None], cols * shade, img)
    basket = (np.abs(x - 0.5) < 0.05) & (y > 0.68) & (y < 0.75)
    img[basket] = np.array([0.45, 0.28, 0.15], np.float32)
    for sx in (-1, 1):
        rope = (np.abs(x - (0.5 + sx * (0.045 + (0.68 - y) * 0.6))) < 0.003) & (y > 0.58) & (y < 0.68)
        img[rope] = 0.2
    pol = np.ones_like(img)
    m = 0.06
    inner = (x > m) & (x < 1 - m) & (y > m) & (y < 0.8)
    pol[inner] = img[inner]
    return to8(pol)


def lake_photo():
    w, h = 1600, 900
    x, y = grid(w, h)
    top = int(h * 0.62)
    xt, yt = grid(w, top)
    sky = sky_clouds(xt, yt * 0.95, 0.3, w, top)
    refl = np.flipud(sky)[: h - top] * np.array([0.75, 0.88, 0.95], np.float32)
    ripple = 1 + 0.04 * np.sin(np.arange(h - top)[:, None] * 0.9)
    img = np.vstack([sky, refl * ripple[..., None]])
    return to8(img)


# ---------------------------------------------------------------- audio
def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def note(f, sec, decay=1.6):
    t = t_axis(sec)
    env = np.exp(-t * decay) * np.clip(t / 0.01, 0, 1)
    return env * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t))


def piano(sec=8):
    out = np.zeros(int(sec * SR))
    mel = [523, 659, 784, 659, 587, 698, 880, 698, 523, 659, 784, 1047, 988, 784, 659, 587]
    step = sec / len(mel)
    for i, f in enumerate(mel):
        s = int(i * step * SR)
        n = note(f, min(2.0, sec - i * step), 2.2)
        out[s:s + len(n)] += 0.25 * n
        if i % 4 == 0:
            n = note(f / 2, min(2.5, sec - i * step), 1.2)
            out[s:s + len(n)] += 0.2 * n
    return out * 0.8


def drums(sec=12, bpm=100):
    out = np.zeros(int(sec * SR))
    beat = 60 / bpm
    t = t_axis(0.4)
    kick = np.sin(2 * np.pi * (50 + 120 * np.exp(-t * 30)) * t) * np.exp(-t * 9)
    snare = rng.normal(0, 1, len(t)) * np.exp(-t * 18) * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 20) * 0.4
    hat = rng.normal(0, 1, int(0.06 * SR)) * np.exp(-np.arange(int(0.06 * SR)) / SR * 60)
    hat = np.diff(hat, prepend=0)
    i = 0
    while i * beat / 2 < sec - 0.4:
        s = int(i * beat / 2 * SR)
        if i % 4 == 0 or i % 8 == 5:
            out[s:s + len(kick)] += 0.8 * kick
        if i % 4 == 2:
            out[s:s + len(snare)] += 0.55 * snare
        out[s:s + len(hat)] += 0.25 * hat
        i += 1
    return out * 0.9


def ambient(sec, chord=(220, 277, 330, 415), waves=True):
    t = t_axis(sec)
    pad = sum(np.sin(2 * np.pi * f * t + np.sin(t * 0.7 + f) * 0.4) for f in chord) / len(chord)
    pad *= 0.25 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 3.3))
    if waves:
        noise = rng.normal(0, 1, len(t))
        noise = np.convolve(noise, np.ones(40) / 40, "same")
        pad += noise * 1.6 * (0.2 + 0.8 * np.clip(np.sin(2 * np.pi * t / 4.2), 0, 1) ** 2)
    fade = np.clip(t / 0.5, 0, 1) * np.clip((sec - t) / 0.5, 0, 1)
    return pad * fade


# ---------------------------------------------------------------- build
def main():
    tmp = OUT / "_a.wav"
    H264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"]

    write_wav(tmp, ambient(10))
    encode(OUT / NAMES["clip_1080p30.mp4"], render(sunset, 1920, 1080, 300, 3), 1920, 1080, 30, H264, tmp, ["-c:a", "aac"])
    write_wav(tmp, ambient(6, (262, 330, 392, 494), waves=False) + 0.3 * piano(6))
    encode(OUT / NAMES["clip_720p60.mov"], render(sky_clouds, 1280, 720, 360, 2), 1280, 720, 60, H264, tmp, ["-c:a", "aac"])
    encode(OUT / NAMES["clip_bars.webm"], render(neon, 1280, 720, 125, 2), 1280, 720, 25,
           ["-c:v", "libvpx-vp9", "-b:v", "2M", "-deadline", "realtime", "-cpu-used", "8"])
    write_wav(tmp, ambient(4, (196, 247, 294), waves=True) * 0.8)
    encode(OUT / NAMES["clip_small.avi"], render(aurora, 640, 480, 96, 1), 640, 480, 24,
           ["-c:v", "mpeg4", "-q:v", "3"], tmp, ["-c:a", "pcm_s16le"])
    encode(OUT / NAMES["clip_noaudio.mkv"], render(city, 1920, 1080, 96, 3), 1920, 1080, 24, H264)
    tmp.unlink()

    write_wav(OUT / NAMES["tone.wav"], piano(8))
    write_wav(tmp, drums(12))
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(tmp), "-c:a", "libmp3lame", "-b:a", "192k",
                    str(OUT / NAMES["beats.mp3"])], check=True)
    tmp.unlink()
    cv2.imwrite(str(OUT / NAMES["still.png"]), cv2.cvtColor(balloon_photo(), cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(OUT / NAMES["still.jpg"]), cv2.cvtColor(lake_photo(), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
    speech = Path(r"D:\ArloStudio\testmedia\speech.wav")
    if speech.exists():
        (OUT / "speech.wav").write_bytes(speech.read_bytes())
    (OUT / "names.json").write_text(json.dumps(NAMES, indent=2))
    print("done", OUT)


if __name__ == "__main__":
    sys.exit(main())
