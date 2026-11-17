// Every app on the site comes from this list. Add a new object to add a new app.
// downloads: files in downloads/. Online, the zips live on the GitHub release below
// (GitHub Pages cannot hold files over 100 MB); sizes come from downloads/manifest.json.
window.ARLO_RELEASE = "https://github.com/arlobruni67/arlo-maker/releases/download/downloads/";
window.ARLO_LICENSE = {
  name: "GPL-3.0",
  file: "downloads/LICENSE-GPL-3.0.txt",
  short: "free to use, change and share",
  summary: "Every app is free to use, change and share. If you share a copy, changed or not, you must share its source code too, under the same licence."
};

window.ARLO_APPS = [
  {
    id: "arlo-studio",
    name: "ARLO STUDIO",
    tagline: "A full video editor with pro pages and a friendly feel.",
    description:
      "ARLO STUDIO is a video editor for Windows. It mixes simple, CapCut-style editing with pro pages for colour, audio and export. Drop clips on the timeline, add transitions, effects, captions and stickers, then grade, mix and render with your graphics card.",
    icon: "assets/studio-icon.png",
    category: "video",
    status: "ready",
    statusLabel: "Ready",
    tech: ["Python", "Qt", "OpenGL", "FFmpeg"],
    started: "2026-11-12",
    stats: [
      { value: 54, label: "transitions" },
      { value: 16, label: "effects" },
      { value: 44, label: "stickers" },
      { value: 210, label: "tests passing" }
    ],
    features: [
      "Pages for Media, Edit, Color, Audio and Export",
      "54 transitions in 6 groups, with resizable badges",
      "Green screen auto key, chroma key and shape masks",
      "Auto captions with Whisper, 10 caption styles and SRT",
      "Colour grading with LUTs and live scopes",
      "Audio mixer with EQ, compressor, pan and limiter",
      "GPU compositing, about 12x faster at 1080p",
      "NVENC and AMF export with a render queue",
      "Motion tracking, speed ramps and freeze frames",
      "Project hub and YouTube resolution presets"
    ],
    downloads: [
      { label: "Download for Windows", file: "downloads/arlo-studio-windows.zip", kind: "app" },
      { label: "Source code", file: "downloads/arlo-studio-source.zip", kind: "source" }
    ],
    links: [
      { label: "User guide", url: "https://github.com/arlobruni67/arlo-studio/blob/main/docs/USER_GUIDE.md", icon: "book" },
      { label: "GitHub", url: "https://github.com/arlobruni67/arlo-studio", icon: "code" }
    ],
    shots: [
      { src: "assets/shots/studio-edit.png", caption: "Edit page with the timeline" },
      { src: "assets/shots/studio-fx.png", caption: "Transitions browser and the Iris wipe" },
      { src: "assets/shots/studio-color.png", caption: "Color page with scopes" },
      { src: "assets/shots/studio-audio.png", caption: "Audio page and mixer" },
      { src: "assets/shots/studio-export.png", caption: "Export page and render queue" },
      { src: "assets/shots/studio-hub.png", caption: "Project hub" }
    ]
  },
  {
    id: "ebs",
    name: "EBS",
    tagline: "A light screen and game recorder, written in Rust, that does not drop frames.",
    description:
      "EBS records your screen, a window or a game with almost no slowdown. It is written in Rust, captures without touching the game, encodes straight on the graphics card and keeps every audio source on its own track. The Optimise button tests your PC and picks the best quality it can handle.",
    icon: "assets/ebs-egg.png",
    category: "recording",
    status: "ready",
    statusLabel: "Ready",
    tech: ["Rust", "egui", "Direct3D 11", "FFmpeg"],
    started: "2026-11-12",
    stats: [
      { value: 60, label: "fps at 1080p" },
      { value: 0, label: "dropped frames" },
      { value: 1, label: "ms max render", prefix: "<" },
      { value: 3, label: "tested presets" }
    ],
    features: [
      "Display, window and game capture, no injection",
      "Zero-copy NVENC encoding, plus x264 and SVT-AV1",
      "Desktop audio and mic, each on its own track",
      "Scenes, nested scenes and scene collections",
      "YouTube Wide and YouTube Short (9:16) modes",
      "Optimise: benchmarks Smooth, Balanced and Quality presets",
      "Pause and resume, MKV recording with MP4 remux",
      "Move, resize and rotate sources in the preview",
      "Encoder checks run in a separate process, so a crash never takes the app down"
    ],
    downloads: [
      { label: "Download for Windows", file: "downloads/ebs-windows.zip", kind: "app" },
      { label: "Source code", file: "downloads/ebs-source.zip", kind: "source" }
    ],
    links: [
      { label: "User guide", url: "https://github.com/arlobruni67/ebs/blob/main/docs/USER_GUIDE.md", icon: "book" },
      { label: "GitHub", url: "https://github.com/arlobruni67/ebs", icon: "code" }
    ],
    shots: []
  }
];
