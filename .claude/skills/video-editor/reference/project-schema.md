# project.json reference

A project folder holds `project.json`, `recordings/`, `audio/`, an optional
`logo.png`, and the generated `build/` and `out/`. Relative paths resolve
from the project folder.

## Top level

| Field | Default | Meaning |
|---|---|---|
| `name` | `Project` | Used in output file names: `<name>_v<version>_9x16_<date>.mp4`. |
| `version` | `1` | Bump this for every revision sent to the client. |
| `brand` | `digital-studio` | A folder under `brands/`, or a path to a `brand.json`. |
| `brand_overrides` | — | Deep-merged over the brand, e.g. `{"cta": {"secondary": "..."}}`. |
| `logo` | brand logo | PNG logo. The project folder is searched first, then the brand folder. If it's missing, a placeholder "DS" badge is drawn. |
| `voiceover.mode` | brand `voice.default_mode` (`none` for Digital Studio) | `none`: no narration; on-screen `text` lines carry the message and set the timing. `scenes`: one voice file per scene (`vo_file`, or `vedit.py tts`). `single`: one continuous take (`voiceover.file`, `voiceover.offset`), with every scene needing a `duration`. |
| `music.file` | — | Royalty-free track (looped and trimmed), or `"placeholder"` for drafts. `music.start` skips into the track; `music.gain_db` overrides the level. |
| `music.bpm` | `"auto"` | `"auto"`: `hyperframes beats` detects tempo and phase (cached in `build/beats.json`), and scene cuts snap to the beat. A number: use that BPM, with `music.first_beat` (seconds into the track) giving the phase. `"off"`: no snapping. Applies only when `voiceover.mode` is `none`. |
| `sound_design` | `true` | Whoosh, pop and click SFX. |
| `sfx` | `[]` | Extra SFX events: `[{"type": "pop", "t": 12.3}]`, timed on the global timeline. |
| `captions.burn` | `true` | Burn captions in. The `.srt` file is written either way. |
| `cover_at` | `1.5` | Second to grab the cover image from. |

## Scenes (`scenes[]`)

Common fields:
- `id`: unique, used for file names.
- `type`: one of the scene types below.
- `text`: on-screen Bangla lines, as one string or a list of 1–2 strings
  (about 5 words each). They appear one after another as pills under the
  headline, each held for reading time. This is the main message carrier
  when there is no voice-over.
- `duration`: forces a length; beat snapping skips this scene.
- `captions`: true/false, to show or hide this scene's lines.
- `vo`, `vo_file`: only used when `voiceover.mode` is `scenes` or `single`.
  `vo` is the narration text and becomes the captions.

Text fields accept `*word*` to colour that word gold.

### `title`
`headline` (big, centred), optional `sub`, optional `logo: true`.

### `logo`
Logo reveal with the brand name, byline and tagline. `sub` overrides the
tagline.

### `screen`
For landscape frames (`browser`, `laptop`) with `text` lines, the text sits
directly under the headline and the window moves down, so the line never
covers the app UI. Portrait (`phone`) scenes keep it in the lower text band.

| Field | Meaning |
|---|---|
| `clip` | Recording path. |
| `in`, `out` | Source seconds to use. |
| `speed` | Playback speed. With no voice-over the clip plays at this speed for up to `motion.max_screen_seconds` (8 s); a longer clip is sped up to fit (at most 2.5×) unless `auto_speed: false` or `duration` is set. If the clip is shorter than the text needs, the last frame is frozen. |
| `frame` | `browser` (default for landscape: window with the brand URL in the address bar), `phone` (portrait or mobile-browser recordings), `laptop`, `none`, `auto`. |
| `url` | Address-bar text for the `browser` frame (default: brand URL). |
| `headline` | Up to 6–8 words, shown above the device. |
| `zoom` | `[{"t": 3.0, "dur": 2.5, "x": 0.3, "y": 0.2, "scale": 1.7}]`: centre the point `(x, y)` and punch in, easing in and out. |
| `highlight` | `[{"box": [x, y, w, h], "t": 1.0, "dur": 2.0}]`: gold box over the UI. |
| `clicks` | `[{"t": 1.2, "x": 0.27, "y": 0.35}]`: tap ripple plus a click sound (no cursor). |
| `steps` | **Guided walkthrough:** `[{"t": 0.8, "x": 0.06, "y": 0.17, "label": "ড্যাশবোর্ড"}, ...]`. An animated cursor glides to each point, clicks it at `t` (press, ripple, click sound), and a numbered pill (১, ২, ৩ …) shows `label` next to it until the next step: the "show every option one by one" look. Put `t` where the recording actually opens that option. The scene stretches to fit every step plus 1.6 s after the last one. |
| `follow` | `true`: the camera zooms in (`follow_zoom_scale`, default 1.6) and pans from step to step with the cursor, then zooms back out before the cut. Don't combine with manual `zoom` in the same scene. |
| `blur` | Privacy boxes, see below. |

**Coordinates** are normalised to the recording: `x` and `y` are 0–1 from the
top-left, and `w`/`h` are fractions of width and height. Read them off the
red 0.1 grid in `vedit.py frames` output. **Times** in `zoom`, `highlight`,
`clicks` and `blur` are **source-clip seconds**, the `t=` stamp on each
frame. Trimming and speed changes are converted for you.

### Blur boxes
```json
{"box": [0.06, 0.21, 0.75, 0.03]}
{"box": [0.06, 0.21, 0.75, 0.03], "t": 2.0, "until": 6.5}
{"box": [0.06, 0.21, 0.75, 0.03], "to": [0.06, -0.33], "move_from": 2.0, "move_until": 6.85}
{"box": [0.5, 0.4, 0.3, 0.05], "style": "solid"}
```
- With no `t` or `until`, the box applies to the whole clip.
- `to` moves the box linearly between `move_from` and `move_until`, which is
  how you follow scrolling content. Off-frame positions are fine.
- `style: "solid"` paints a brand-coloured box instead of blurring. Use it for
  text that stays legible through blur, such as very large digits.
- Boxes are padded by 6 px. Make them generous: cover the whole line, not
  just the digits.

For a long scrolling list with constant scroll speed, generate the boxes
instead of typing them out:

```python
H, scroll_px, t0, t1 = 2340, 1260, 2.0, 6.85      # frame height, total scroll, scroll window (source s)
rows_px = [1065 + i * 230 for i in range(12)]     # top of each sensitive line before scrolling
blur = [{"box": [0.06, y / H, 0.5, 60 / H], "to": [0.06, (y - scroll_px) / H],
         "move_from": t0, "move_until": t1} for y in rows_px]
```

### `list`
Headline plus `items` (feature names, about 2–6 words each) that slide in one
after another, each with a gold tick and a pop sound, mirroring the feature
list in the app's own login panel. `item_gap` (default 0.55 s) sets the
rhythm; the scene lasts until every item has been readable.

### `cta`
Logo, brand name, an optional offer badge (`cta.offer`, e.g. "টেস্ট ভার্সনে
*১ জিবি ফ্রি*", "1 GB free on the test version"), the gold button
(`cta.headline`), URL pill (`cta.url`), the secondary line
(`cta.secondary`) and a small address line (`brand.address`; hide it with
`"address": false`), followed by a tap and a gentle pulse. The
defaults come from `brand.cta`; override them per scene with `"cta": {...}`.
It has no text lines; the CTA text is the message.

## Outputs

- `out/<name>.mp4` is the deliverable. `out/<name>.srt` holds the on-screen text lines,
  `out/<name>_cover.jpg` the cover, and `out/<name>_timeline.json` the scene
  starts, durations and SFX.
- `build/hf/` is the HyperFrames project (`index.html` plus
  `compositions/<scene>.html`). Open it with `vedit.py preview`. It is
  regenerated on every render, so make changes in `project.json`, or in
  `compose.py` for a design change that should apply to every video.
- `build/mix.wav` is the final audio mix (music + SFX). `build/beats.json` is the detected tempo.
