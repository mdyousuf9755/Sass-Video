# Workflow, adapted for Digital Studio

The reference PDF ("Video Editing Workflow Reference") is a generic 9-stage
process for product-promo videos. This file records how each stage is applied
to **this** project: a 45 s, 9:16 Facebook Reel. The reel is a faceless
explainer built from screen recordings of a web-only app, with **no
voice-over**: music, sound effects and on-screen Bangla text only (the user's
choice). Where the PDF and this file disagree, this file wins. Where this
file and the user's brief disagree, the brief wins.

| # | PDF stage | What we do here | Why it differs |
|---|---|---|---|
| 1 | Brief & plan | The brief is mostly fixed in `brand.json`: computer-shop owners in Bangladesh (goal: register on the test version and send feedback), Reels 9:16, 45 s, friendly and energetic tone, CTA "টেস্ট ভার্সনে ১ জিবি ফ্রি – আজই রেজিস্টার করুন: digital-studio-bd.pages.dev \| আপনার মতামত জানান". Per video, ask only which features to show and whether there is an offer. | Saves a round of questions; the brand does not change between videos. |
| 2a | Assembly | `init` creates `recordings/`, `audio/` and `out/`. One recording per feature, named after the scene id. | |
| 2b | Rough cut | Set `in`/`out` per scene. A demo plays at natural speed up to 8 s; longer actions are sped up automatically (max 2.5×). | Matches the PDF's "speed up long screen actions". |
| 2c | Fine cut | With no narration, **reading time and the music drive the pacing**: each text line is held for `max(1.4 s, chars ÷ 11)`, and scene lengths round up to whole beats (tempo from `hyperframes beats`), so cuts, whooshes and text pops land on the music. | There is no voice to cut on, so we cut on the beat instead. |
| 2d | Picture lock | Approve the draft before the final render. A delivery render takes minutes, so it happens once. | |
| 3 | Graphics | Brand gradient background; a browser-window frame showing the real URL (default, because the app is web-only), or a phone frame for mobile-browser recordings; gold highlight boxes; 6–8 word headlines with a gold accent word. | The PDF's "laptop/phone frame" becomes browser-first; there is no app-store look. |
| 3 | Privacy | Blur is **baked into the recording pixels with ffmpeg before composition**. Boxes are marked from gridded frame sheets; scrolling text uses moving boxes. Shop name and address stay; everything else personal is hidden. | Baked pixels cannot be undone by a later layout change. An overlay could slip. |
| 4 | Motion | HyperFrames + GSAP: every scene enters with one style (rise + fade, 0.4 s), headlines pop (`back.out`), the device eases in, zooms ease in and out (`power2.inOut`) on the key UI, click ripples show taps, and the logo appears at the start (logo scene) and end (CTA). | One transition style and no gimmicks, as the PDF asks; seekable and deterministic renders. |
| 5 | Audio | **No voice-over.** A royalty-free, upbeat music track is the bed at full level, fading in over 0.3 s and out over 1.8 s, and starting on a beat. Synthesised SFX: whoosh on every cut, pop on headlines and text, click on taps and the CTA button. Final mix -14 LUFS, true peak ≤ -1.5 dBTP. (If a project switches on a voice-over, the music drops about 11 dB under it and is side-chain ducked, which meets the PDF's -18 to -22 dB.) | The user chose music and SFX only. The SFX are generated, so there are no licence issues. |
| 6 | Captions → on-screen text | Without narration, the "captions" **are** the script: 1–2 short Bangla lines per scene (about 5 words each), bold white on a dark teal pill, popping in one after another under the headline. Burned in, and also exported as `.srt`. | The PDF treats captions as optional; here they carry the message. |
| 7 | Review | `qa` runs technical checks and makes a contact sheet with the safe zone drawn. Watch twice: (1) content and truth (features exist, no mobile-app claims, no private data), (2) quality (every line readable in its time, cuts on the beat, SFX not too loud, spelling, black frames). Check it on a phone screen, with sound off and then on. | Adds the project's own risks: privacy, the web-only claim, and readability without narration. |
| 8 | Export | H.264 High, yuv420p, 30 fps, AAC 320 kbps 48 kHz, faststart. The delivery render is near-lossless (CRF ~16); bitrate follows the content, and simple motion graphics often stay under 10 Mbps, which is fine. Names follow `Project_vN_9x16_YYYY-MM-DD.mp4`, plus `.srt` and `_cover.jpg`. | |
| 9 | Format | Only 9:16 1080×1920 for Reels, under 60 s, target 45 s. A different ratio needs a new brand variant (`video` and `layout` blocks) because the layout is designed for 9:16. | The PDF lists every platform; this project needs only one. |

## Checkpoints

1. On-screen script approved (scene list, headlines, text lines).
2. Privacy boxes reviewed on the frame sheets.
3. Draft approved (watched in full, QA passing).
4. Final delivered with the checklist completed (`qa-checklist.md`).
