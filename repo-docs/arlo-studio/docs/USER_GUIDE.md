# ARLO STUDIO user guide

## 1. Install and start

1. Download `arlo-studio-windows.zip` from [Arlo Maker](https://arlobruni67.github.io/arlo-maker/).
2. Unzip the whole folder anywhere, for example your Desktop.
3. Double-click **ARLO STUDIO.exe**.

You need Windows 10 or 11 (64-bit) and a graphics driver with OpenGL 3.3. An NVIDIA (NVENC) or AMD (AMF)
graphics card makes export fast; without one ARLO STUDIO exports on the CPU.

Your projects, autosaves, caches and logs are kept in the `userdata` folder next to `ARLO STUDIO.exe`.

## 2. The Project Hub

ARLO STUDIO opens on the **Project Hub**:

* **Quick Start**: YouTube Video (1920x1080), YouTube Short (1080x1920) or Square (1080x1080).
* **New Project...** for any size and frame rate.
* **Recent Projects** as cards with a picture, size, frame rate and length. Search, sort, or right-click a card
  to show it in Explorer or remove it from the list.

Closing the editor (X) takes you back to the hub. **File > Exit** quits.

## 3. The pages

The bar at the bottom switches pages. Each page remembers its own panel layout (**View > Reset Layout** restores it).

| Page | Shortcut | What it is for |
|---|---|---|
| Media | Shift+1 | import and organise clips |
| Edit | Shift+2 | the timeline: cut, move, add text, transitions, effects |
| Color | Shift+3 | grade clips, scopes |
| Audio | Shift+4 | mixer, EQ, compressor, limiter |
| Export | Shift+5 | render the video, render queue |

Drag the bars between panels to make the viewer or the timeline bigger.

## 4. Import and edit

* **Import**: drag files or folders from Explorer onto the Media bin, the timeline or the window.
  MP4, MOV, MKV, AVI, WebM, WAV, MP3, FLAC, M4A, OGG, PNG, JPG, BMP, TIFF and WebP work.
* **Place clips**: drag them onto a track. Video and its sound land as a linked pair.
  The main picture track is **Video**, layers above it are **Overlay 1, 2...**, audio tracks are **Sound 1, 2...**
* The first video you place sets the project's frame rate (new projects start at 60 fps).
* **Move** a clip by dragging it; **trim** by dragging its edges (hold Alt to trim one side of a linked pair).
* **Split** with the blade tool (B) or at the playhead (Ctrl+B). **Ripple delete** (Shift+Del) closes the gap.
* **Undo / redo** works for every edit.
* **Inspector**: position, scale, rotation, opacity, volume, speed, reverse and fades for the selected clip.
  Click the diamond next to a setting to add a keyframe; right-click it for Linear, Ease or Hold.
* **Nest** clips into their own sequence with Alt+N; double-click a nested clip (or Alt+O) to open it.

## 5. Text, captions and stickers

* **Add Title** (T), **Lower Third** (Shift+T) or **Text** (Ctrl+T) at the playhead. Edit the text, font, colours,
  outline, shadow and box in the Inspector. Ten style presets are included.
* **Auto captions** (Ctrl+Shift+C) turn what the timeline says into caption clips, with word-by-word effects
  such as karaoke and a highlighted active word. Export or import subtitles as SRT.
  Auto captions need the speech model, see [section 11](#11-auto-captions-speech-model).
* **Stickers**: 44 graphics in the Effects panel. Drag one onto a track, then change colour, size, outline and
  animation in the Inspector.

## 6. Transitions and effects

Open the **Effects** panel. Move the mouse across an entry from left to right to preview it.

* **Transitions** (54 in 6 groups: Basic, Wipes, Shapes, Pans and Motion, 3D, Stylized): drag one onto the cut
  between two clips. Drag the ends of the badge on the timeline to make it longer or shorter.
  Ctrl+Shift+D adds a cross dissolve next to the selected clip.
* **Effects** (16, including Color Adjust, Blur, Glow, Vignette, Chroma Key, Shape Mask and Green Screen): drag one
  onto a clip. Stack, reorder, switch off and keyframe them in the Inspector.
* **Green Screen** finds the screen colour by itself; drop it on a clip shot on green or blue.

## 7. Speed, freeze and tracking

* **Speed ramps**: Inspector or **Timeline > Speed Ramp** (Montage, Hero, Bullet, Jump Cut, Flash In, Flash Out).
  The sound follows the same speed.
* **Freeze Frame** (Shift+F) holds the frame under the playhead for 2 seconds.
* **Track Motion** makes the selected overlay follow what is under its centre in the clips below. It writes
  Position keyframes, so you can still fix them by hand.

## 8. Colour

On the **Color** page, select a clip and use the Lift / Gamma / Gain / Offset wheels, contrast, saturation,
temperature and curves. Load a `.cube` LUT, compare with the grade off, copy and paste grades between clips, or
export a grade as a LUT. The scopes show a waveform, RGB parade, vectorscope and histogram.

## 9. Audio

On the **Audio** page each Sound track has a fader, pan, mute, solo, a 4-band EQ and a compressor. The master
strip has a limiter. Linked sound crossfades under video transitions (switch it off in the transition panel).

## 10. Export

Open the **Export** page (Shift+5 or Ctrl+M):

1. Pick a preset: YouTube 1080p / 4K, Shorts / TikTok / Reels, small 720p, HEVC, ProRes master, WebM, WAV or MP3.
2. Choose the name and folder.
3. Press **Export Now**, or **Add to Render Queue** to export several videos one after another while you keep editing.

Only encoders that pass a real test encode on your computer are offered. **Auto** picks the first working
graphics-card encoder.

## 11. Auto captions speech model

Auto captions use the Whisper `small.en` model (about 460 MB). It is not in the download. To add it, open a
Command Prompt in the ARLO STUDIO folder and run:

```
runtime\python.exe -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-small.en', cache_dir='userdata/models')"
```

Then restart ARLO STUDIO. Captions run on the CPU at about 0.6x real time.

## 12. Saving and recovery

* **Ctrl+S** saves. Saves are atomic and keep a `.bak` copy.
* Autosave runs every 60 seconds when something changed. After a crash ARLO STUDIO offers to recover.
* If media has moved, ARLO STUDIO asks you to relink it (search a folder by name, or pick one file).

## 13. Keyboard shortcuts

| Keys | Action |
|---|---|
| Space | play / pause |
| J / K / L | shuttle back / stop / forward (press again for 2x, 4x, 8x) |
| Home / End | start / end of the sequence |
| , / . | nudge the selected clip |
| B | blade tool |
| Ctrl+B | split at the playhead |
| Delete / Shift+Del | delete / ripple delete |
| Ctrl+D | duplicate |
| M | add a marker |
| N | snapping on / off |
| T / Shift+T / Ctrl+T | title / lower third / text |
| Ctrl+Shift+C | auto captions |
| Ctrl+Shift+D | add a cross dissolve |
| Shift+F | freeze frame |
| Alt+N / Alt+O | nest selected clips / open a nested clip |
| Ctrl+Alt+N | new sequence |
| Ctrl+M | export |
| Shift+1 ... Shift+5 | Media, Edit, Color, Audio, Export page |
| Ctrl + mouse wheel | zoom the timeline |
| Esc | cancel a drag |

## 14. Troubleshooting

* **Nothing happens when I double-click ARLO STUDIO.exe**: keep the `runtime` folder next to the exe. Unzip the
  whole folder, do not run the exe from inside the zip.
* **Playback stutters on heavy effects**: set the viewer Quality to 1/2 or 1/4, or turn on proxies.
* **An encoder is missing in Export**: it failed the test encode on your computer; pick another one or Auto.
* Logs are in `userdata\logs\arlo.log`.

For the full feature list and the known limits, see [FEATURES.md](FEATURES.md).
