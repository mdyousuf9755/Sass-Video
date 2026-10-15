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
