# QA report: Digital Studio 16:9 videos

Date: 2026-10-15. Measured with ffprobe/ffmpeg on the exported files; frames
were checked on contact sheets.

## Promo v3 (correction of v2)

File: `exports/Digital_Studio_Promo_v3_16x9_2026-10-15.mp4`. v2 is kept
unchanged next to it.

### What changed from v2 (scene `p_dash`, 4.6–10.6 s)

- **Storage card misreading.** The card reads **"৬৭৩.০ কেবি / ১.০০ জিবি"**:
  673 **KB** used of 1.00 GB. That is not 673 GB, and it does not contradict
  the 1 GB free offer. In v2 the zoom made "কেবি" small and easy to misread.
  - v3 shows the card un-zoomed, with a gold highlight and the label
    "ব্যবহৃত ৬৭৩ কেবি · মোট ১ জিবি ফ্রি" (from 7.85 s).
  - The numbers are the app's real values for the demo shop (test-report
    R7, R10).
- **Left side cut off.** The zoom is gone, so the whole app (sidebar
  included) is inside the browser frame.
- **Footage.** The same existing dashboard recording (1.2–6.3 s of
  `dashboard.mp4`). There was **no new recording, no new demo record and no
  production data change**.
- **Everything else is unchanged:** the other scenes, the voice-over files,
  scene lengths and the music.

### Measurements

| Check | Result |
|---|---|
| Video | H.264, **1920×1080, 30 fps** |
| Duration | **40.40 s** |
| Audio | AAC 48 kHz stereo; voice-over (Tanvir) in all 7 scenes; loudness **−14.1 LUFS**, peak −1.9 dBFS |
| Black frames (>0.3 s) | none |
| Silence (>1.5 s, −45 dB) | none |
| Subtitles | Burned in; `.srt` exported. **Identical to v2** (same VO text and timing, since scene lengths did not change) |

### Privacy and claims

| Check | Result |
|---|---|
| Phone numbers | Only the demo number **01700-000000** inside the app; the business number **01865453564** on the CTA (owner-approved) |
| Passwords, OTP | Not visible (dots / not shown) |
| Other shops, other shops' ads, real CV, real NID | Not shown |
| Storage claim | "১ জিবি ফ্রি" matches the live test (new shop: ১.০০ জিবি, R7). The highlight label states the real used amount |
| Unsupported claims | None. No mobile app, bKash/Nagad/Rocket, AI, Gmail login, 15 GB or customer self sign-up. "ব্রাউজারেই চলে, কোনো ইনস্টল লাগবে না" is true (web app) |

### Known limits

- The voice-over was made on an ElevenLabs **free** account. ElevenLabs'
  free plan does not include commercial use; the owner should confirm the
  licence before publishing.

## Tutorial v3

File: `exports/Digital_Studio_Tutorial_v3_16x9_2026-10-15.mp4`. v2 is kept
unchanged next to it.

### What changed from v2

- **Dashboard (46.3–59.1 s):** the same fix as promo v3. There is no zoom,
  so the whole app is in the frame. The storage card is highlighted with
  "ব্যবহৃত ৬৭৩ কেবি · মোট ১ জিবি ফ্রি".
- **Registration (25.6–46.3 s):**
  - The recording is framed on the form. The app's own left panel, which
    lists "বিকাশ, নগদ, রকেট ও ক্যাশ পেমেন্ট", is no longer visible:
    bKash/Nagad/Rocket stay out until the payment-settings bug (D18) is
    fixed.
  - The code-entry screenshots are cropped to the form card only.
  - The number shows as 01700-000000 and the code as dots.
- **Everything else is unchanged:** the other scenes, the voice-over,
  subtitles and music. No new recording, demo record or production data
  change.

### Measurements

| Check | Result |
|---|---|
| Video | H.264, **1920×1080, 30 fps** |
| Duration | **208.80 s (3:28.8)** |
| Audio | AAC 48 kHz stereo; voice-over (Rafiq) in all 14 scenes; **−14.1 LUFS**, peak −1.9 dBFS |
| Black frames (>0.3 s) | none |
| Silence (>2.5 s, −45 dB) | none |
| Subtitles | Burned in; `.srt` with 74 cues, timed to each scene's voice file |

### Privacy and claims

- **Privacy:** the same results as the promo.
  - Inside the app only the demo number 01700-000000 appears.
  - Passwords are dots; the SMS code is dots.
  - No other shops, the customer home page, the real CV or a real NID.
- **Staff line:** it says only that plain staff cannot see রিপোর্ট, স্টোরেজ
  and প্রোফাইল (true, R27). It does not claim income is hidden (D21).
- **Not mentioned:** no mobile app, bKash/Nagad/Rocket, AI, Gmail login,
  15 GB or customer self sign-up.

## Tutorial v4 (quality correction of v3)

File: `exports/Digital_Studio_Tutorial_v4_16x9_2026-10-15.mp4`. v3 is kept
unchanged.

### A. Inspection findings (on v3)

**Metadata (v3), verified with ffprobe:**
- H.264 High yuv420p, 1920×1080, 30 fps.
- Video 946 kbps; AAC-LC 48 kHz stereo 271 kbps.
- Duration 208.8 s, 6,264 frames.

**Confirmed:**

| ID | Time | Defect | Severity | Evidence |
|---|---|---|---|---|
| F1 | 0:00–0:13 | No real UI until 13.0 s. The voice's "solution" line starts at about 7.5 s | Medium | Timeline; pauses in the hook voice file (sentence breaks at 4.0, 6.7 and 9.1 s) |
| F2 | 0:46–0:59 | The voice describes the counters (48.4–53.1 s) while the picture has already scrolled to the storage card (from 50.5 s) | Medium | Dashboard voice-file pauses (1.2 and 6.4 s) against the recording's scroll mark (4.19 s) |
| F3 | all | Low video bitrate (946 kbps) | Low | 100% crops show **no visible** blocking; text edges are slightly soft |

**Checked and fine:**
- CTA: about 15 s on screen, readable, no black frame, audio fades to −53 dB.
- Music: 16–18 dB below the voice (speech about −16 to −18 dB RMS, music-only gaps about −33 to −35 dB).
- No clipping (peak −1.9 dBFS), no long silences, no black frames.

**Unverified or not changed:**
- **Audio by ear:** NOT VERIFIED. Claude cannot listen, so pronunciation, naturalness and noise were not judged by ear. Only levels and pauses were measured.
- **Small secondary text** (file sizes, dates) is small on phones. Not changed: the main labels are readable, and extra zooms would crop content again.
- **Subtitle timing:** subtitles are spread over each voice file by text length, not aligned word by word. Spot checks show up to about 1 s offset, for example "ফাইল খুঁজে পাওয়া যায় না।" stays up at 7.9 s while the voice has moved on. Not changed in v4.

### B. Change log

| ID | Original time | Change | Reason | Tool | Verification |
|---|---|---|---|---|---|
| F1 | 0:00–0:13 | The hook title card now runs 0–7.3 s. A new 7.3–13.0 s UI preview, headed "সহজ সমাধান: ডিজিটাল স্টুডিও" (from the approved VO line), shows real recordings: আমার ফাইল (customer files), the passport photo result and রিপোর্ট (after its count-up ends, so it shows 2 orders, 1 completed, ৳450). The hook voice and subtitles run over both parts | Shows the product's value from 7.3 s instead of 13 s | compose16.py (HyperFrames) + ffmpeg | Frames at 4, 7.9, 10, 12.5 s checked; no invented UI; total length unchanged |
| F2 | 0:46.3–0:59.1 | Dashboard top section slowed (0.585×) so the counters stay on screen until about 53.4 s. Then the scroll to storage; the highlight appears at 53.65 s with the "১ জিবি" line | Visuals match the narration | compose16.py | Frames at 50, 53.7 s checked |
| F3 | all | Final encode CRF 14, preset slow, tune stillimage, from the source render (one lossy pass) | Sharper small text | ffmpeg/libx264 | v4 video bitrate 1,581 kbps; decode errors 0 |

Everything else is unchanged: the other scenes, the voice-over files, the
music, the scene order and the total length.

### C. Scorecard (v4)

| Category | Score | Note |
|---|---|---|
| Visual quality | 8 | Sharp 1080p, real UI; small secondary text on phones |
| Audio and voice-over | 7 | Levels, ducking and loudness measured fine; **not judged by ear** |
| Editing and continuity | 8 | Sync fixed for the hook and dashboard; subtitle timing ±1 s |
| Text and branding | 9 | Brand colours, font and logo; approved CTA text |
| Storytelling and engagement | 8 | UI from 7.3 s; clear step order |
| AI consistency or animation | n/a | No AI-generated visuals; the voice is ElevenLabs TTS |
| Technical delivery | 9 | 1080p30, −14.1 LUFS, no black frames, no errors |
| Overall professional readiness | 8 | |

### D. Export details

| Field | Value |
|---|---|
| File | `videos/digital-studio-16x9/exports/Digital_Studio_Tutorial_v4_16x9_2026-10-15.mp4` |
| Size | 48.6 MB |
| Duration | 208.80 s |
| Video | H.264 High, yuv420p, 1920×1080, 30 fps CFR, CRF 14, preset slow, tune stillimage, ~1,581 kbps |
| Audio | AAC-LC, 48 kHz stereo, 320 kbps target (271 kbps measured); −14.1 LUFS integrated, −1.9 dBFS peak |
| Subtitles | `.srt` with 74 cues next to the MP4; subtitles also burned in |

### E. Final approval: **CONDITIONAL APPROVAL**

Conditions:
1. Someone listens to the full audio once: pronunciation and naturalness
   were not verified by ear.
2. The ElevenLabs free-plan licence is confirmed for commercial use, or the
   voice is regenerated on a paid plan.
3. The ±1 s subtitle timing is acceptable, or a later pass aligns subtitles
   to sentence pauses.

### F. Checklist

| Check | Status |
|---|---|
| The opening communicates the tutorial's value quickly | VERIFIED (UI at 7.3 s) |
| Important UI text is readable | VERIFIED (main labels; small secondary text is small on phones) |
| Visuals match the narration | VERIFIED for the hook and dashboard; other scenes within 1–3 s |
| Audio has been listened to and verified | NOT VERIFIED (measured only) |
| Branding and content remain accurate | VERIFIED |
| No new editing defects were introduced | VERIFIED on frame checks (the count-up frame in the preview was caught and fixed before rendering) |
| The exported video was inspected | VERIFIED (ffprobe, loudness, black frames, decode, contact sheets) |
| The final CTA is readable | VERIFIED |
| The output file exists and plays correctly | VERIFIED (decodes without errors; playback by ear not verified) |
