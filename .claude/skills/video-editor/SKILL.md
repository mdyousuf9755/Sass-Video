---
name: video-editor
description: Build faceless SaaS explainer reels (screen recordings + motion graphics + on-screen Bangla text, music and SFX; no voice-over by default) for Digital Studio by Yousuf Digital Center, or any brand added under brands/. Use when the user wants to edit, make, cut, re-render or review a promo / explainer / Facebook Reel / Short from app screen recordings, write the on-screen Bangla copy for a reel, hide private data in recordings, or export platform-ready MP4s. HyperFrames (installed locally under engine/) is the animation, beat-detection and rendering engine; ffmpeg handles privacy blur, audio and the final mux.
---

# Video editor: faceless SaaS explainer reels

This skill turns screen recordings and a short brief into a finished 9:16 reel.
It adds:
- branded motion graphics,
- browser or device frames,
- zooms, highlight boxes and click ripples,
- kinetic Bangla headlines and on-screen text lines,
- music with every cut snapped to its beat,
- sound effects,
- a CTA end card.

The output is an H.264/AAC MP4 at -14 LUFS, plus an `.srt` file of the
on-screen text and a cover image.

**There is no voice-over.** The user chose music and sound effects only, so
the on-screen Bangla text carries the whole message. Write it to be read
fast. A voice-over can still be switched on for a specific project
(`voiceover.mode`; see `reference/project-schema.md`), but only when the user
asks for one.

**Default project: Digital Studio.** The brand, colours, CTA, privacy and
product rules are in `brands/digital-studio/brand.json`; read it first.
Digital Studio is **web-only**: there is no mobile app yet. Never write
"mobile app", "download the app" or "install" in a script. Say "ব্রাউজারেই
চলে" (runs in the browser) and "কোনো ইনস্টল লাগবে না" (no install needed).

## How it is built

| Layer | Tool | Where |
|---|---|---|
| Edit list (scenes, text, timing, zoom/highlight/click/blur) | `project.json` (you write it) | project folder |
| Privacy blur, trim, speed, freeze-extend of recordings | ffmpeg (baked into the pixels) | `scripts/vedit.py` → `prepare_clip` |
| Music tempo, so cuts land on the beat | **HyperFrames** `beats` | `scripts/vedit.py` → `detect_beats` |
| Motion graphics, frames, text, transitions | **HyperFrames** composition (HTML + GSAP) | `scripts/compose.py` → `build/hf/` |
| Frame rendering | **HyperFrames** CLI, pinned in `engine/package.json` | `engine/node_modules` |
| SFX, music level, loudness (and voice-over if switched on) | ffmpeg (+ edge-tts) | `scripts/vedit.py` |
| Final mux, `.srt`, cover, QA | ffmpeg / ffprobe | `scripts/vedit.py` |

HyperFrames is a local, unmodified npm dependency (`hyperframes@0.8.150`,
upstream `heygen-com/hyperframes`). Telemetry is off: every call sets
`HYPERFRAMES_NO_TELEMETRY=1` and `DO_NOT_TRACK=1`. Do **not** run
`hyperframes init` or `skills add`, because they install global skills outside
this folder. Run `vedit.py setup` instead. Do not send `hyperframes feedback`
reports unless the user asks.

## Setup (once per machine)

```bash
python3 .claude/skills/video-editor/scripts/vedit.py setup   # npm ci in engine/, Chrome check, doctor
pip install pillow
```

You need Node.js 22 or newer, ffmpeg 5 or newer, Python 3.9 or newer and
Pillow. If `HYPERFRAMES_BROWSER_PATH` is set, or `/opt/pw-browsers/chromium`
exists, that Chromium is used. Otherwise `setup` downloads the pinned Chrome
into the HyperFrames cache.

`V=.claude/skills/video-editor/scripts/vedit.py` in the commands below.

## Workflow

Follow these stages in order. Stop at each **⏸ checkpoint** and get the
user's OK. The reasoning behind each stage, adapted from the reference PDF,
is in `reference/workflow.md`.

1. **Brief.** The goal, audience (Bangladeshi shop owners), platform
   (Facebook Reels 9:16), length (45 s), tone (friendly and energetic) and CTA
   are fixed in `brand.json`. Ask only what is new: which features to show,
   any offer, and which music track.
2. **On-screen script.** For each scene, write a **headline** (at most 6–8
   words, with `*word*` as the gold accent) and 1–2 **text lines** (about
   2–5 words each). Follow `reference/script-45s.md`: hook in the first
   3 s, problem, intro, 2–3 features, benefit, CTA. Every feature you name
   must be visible in a recording.
   **⏸ Get the script approved.**
3. **Project and assets.** Run `python3 $V init <dir> --name <Project>`. Put
   the recordings in `recordings/`, the music in `audio/`, and the app logo as
   `logo.png` in the project folder or in `brands/digital-studio/`. Run
   `python3 $V probe recordings/*`. Recordings come from the web app: desktop
   browser recordings use the `browser` frame (the default), mobile-browser
   recordings use the `phone` frame.
4. **Privacy pass (mandatory).** For each recording, run
   `python3 $V frames recordings/x.mp4 --every 0.5` and **look at every
   sheet**. Mark every phone number, email, password, OTP, customer name or
   number, and payment detail as a `blur` box. The shop name and address may
   stay visible. Use moving boxes (`to`, `move_from`, `move_until`) for text
   that scrolls. A demo account with fake data is the best protection; the
   blur is the safety net. See `reference/project-schema.md`.
5. **Edit list.** Fill in `project.json`:
   - clip `in`/`out`,
   - `zoom` on key UI,
   - `highlight` boxes and `clicks` (each click also plays a click sound),
   - `steps` for a **guided walkthrough**: a cursor clicks each button in
     turn and a numbered Bangla label (১, ২, ৩ …) names each option, with
     `follow: true` for a camera that zooms and pans along. Use this to
     show a menu or every option of a feature one by one,
   - `headline` and `text`.

   Screen-space values are normalised `[x, y, w, h]` read from the frame
   grid. Times are **source-clip seconds**.
6. **Music and timing.**
   - **Music:** set `music.file` to a royalty-free, upbeat track; use
     `"placeholder"` for drafts only. With no track from the user, make an
     original one (synthesised in code, so it is publishable and needs no
     licence): `python3 scripts/music_gen.py promo audio/music.wav
     --seconds 48` (upbeat, 112 BPM) or `bed … --seconds 240` (calmer,
     100 BPM, for tutorials). Ask the user to listen before the final.
   - **Beat:** with `music.bpm: "auto"` (the default), `hyperframes beats`
     detects the tempo and every scene cut lands on a beat.
   - **Text scenes:** a scene lasts as long as its text takes to read
     (`captions.reading_cps`, and at least `min_line_seconds` per line).
   - **Screen scenes:** they run at the recording's natural speed, capped at
     `motion.max_screen_seconds` (8 s); longer clips are sped up, to at most
     2.5×.
7. **Plan check.** `python3 $V render project.json --plan-only` prints the
   timeline. Aim for 45 s ± 3 s. Adjust it with clip `in`/`out`, the text
   lines, or a scene `duration`; never cut the CTA.
8. **Draft render.** `python3 $V render project.json --draft` runs these
   steps:
   - prepares the clips,
   - detects the beat,
   - writes the HyperFrames project to `build/hf/`,
   - mixes the music and SFX,
   - runs `hyperframes check`, which must pass,
   - renders the video,
   - muxes in the audio,
   - writes the `.srt`, the cover image and `timeline.json` to `out/`.

   `python3 $V preview project.json` opens HyperFrames Studio for scrubbing.
9. **Review.** Run `python3 $V qa out/<file>.mp4`, then view
   `contact_sheet.jpg`. Watch it twice:
   - **Content:** features are real, the Bangla copy is correct, there are no
     mobile-app claims, and there is no private data in any frame.
   - **Quality:** every line is readable in its time on a phone, cuts hit the
     beat, the SFX aren't too loud, and text stays in the safe zones.

   Fix issues in `project.json` and re-render.
   **⏸ Get the draft approved.**
10. **Final.** Run `python3 $V render project.json` (delivery quality), then
    `qa` again. Check every item in `reference/qa-checklist.md` before
    handing it over. File names follow `Project_vN_9x16_YYYY-MM-DD.mp4`;
    bump `version` for each revision.

## Rules that always apply

- **Privacy first.** No frame may show a phone number, email, password or
  customer data. Bake the blur into the clip (step 4) and verify it in QA
  frames. Never rely on an overlay alone.
- **Truthful content.** Show only features that exist and work today, and
  use correct prices and offers. The app is web-only.
- **No voice-over** unless the user asks for one for a specific video. With
  no narration, every message must be readable on screen in time. Keep each
  text line to about 5 words or fewer; split longer thoughts across lines.
- **Brand.** Use teal or dark green with gold accents, Hind Siliguri (bundled
  in `assets/fonts`, OFL), and the logo at the start (`logo` scene) and end
  (`cta` scene). Use one transition style.
- **Bangla text** is rendered by Chrome, so conjuncts shape correctly. Still
  proofread every headline and line against the approved script.
- **Safe zones (9:16):** keep text between y = 270 and y = 1250 and at least
  70 px from the sides. The text band ends at y = 1225. The QA contact sheet
  draws this box in red.
- **Music** must be royalty-free and supplied by the user. `"file":
  "placeholder"` makes a synthetic bed for drafts only; never publish with it.
- If the render environment blocks Chrome, deliver the checked composition in
  `build/hf/` and say so. Do not build a substitute rasteriser.

## Files

- `scripts/vedit.py` is the CLI: `setup`, `init`, `probe`, `frames`,
  `music`, `render`, `preview`, `qa`, and `tts` (only for voice-over
  projects).
- `scripts/compose.py` generates the HyperFrames HTML (scene types `title`,
  `logo`, `list`, `screen`, `cta`; frames `browser`, `phone`, `laptop`, `none`).
- `brands/<brand>/brand.json` holds colours, fonts, layout, motion, voice
  (off by default), audio, captions and reading speed, privacy, product facts
  and the CTA. Add a folder to support another brand.
- `templates/project.example.json` is the 45 s Digital Studio skeleton (no
  voice-over).
- `reference/workflow.md` explains the adapted workflow and why it differs
  from the generic PDF.
- `reference/project-schema.md` documents every `project.json` field.
- `reference/script-45s.md` has the beat sheet, Bangla on-screen copy rules
  and an example.
- `reference/qa-checklist.md` is the pre-delivery checklist.
- `engine/` is the pinned HyperFrames and GSAP install; `node_modules` is
  git-ignored.
