# Arlo Maker

The home of every app made by Arlo: **ARLO STUDIO** (video editor) and **EBS** (screen and game recorder).

Website: https://arlobruni67.github.io/arlo-maker/

Downloads (Windows app zips and source code) are on the
[downloads release](https://github.com/arlobruni67/arlo-maker/releases/tag/downloads).
All apps are open source under GPL-3.0-or-later.

## How the site works

A static site with no build step: `index.html`, `styles.css`, `main.js` and `apps.js`.
`apps.js` lists the apps; add an entry there to add an app.

## Making new downloads

```
D:/ArloStudio/.venv/Scripts/python.exe tools/build_studio_app.py
D:/ArloStudio/.venv/Scripts/python.exe tools/package_sources.py
gh release upload downloads downloads/*.zip --clobber
git add downloads/manifest.json && git commit -m "Update download sizes" && git push
```
