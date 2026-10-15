# Audit report: Digital Studio 16:9 production (Phase 1–2)

Date: 2026-10-15. Nothing was changed on the live site for this audit, and
no data was created.

## 1. Tools actually available

| Tool | Status | Notes |
|---|---|---|
| Playwright + Chromium (headless) | ✅ works | Login, clicks, uploads and downloads already ran live in the tests |
| Browser video: Playwright `recordVideo` | ⚠️ low quality | 1920×1080 but VP8 at about 0.9 Mbps and 25 fps; UI text gets soft. **Not used** |
| Browser video: Chrome screencast (CDP) | ✅ chosen | Lossless 1920×1080 PNG frames at about 14–15 fps with timestamps → ffmpeg makes 30 fps constant-frame-rate clips. Sharp text |
| FFmpeg 6.1.1 | ✅ | Blur and replace, timeline, audio mix, loudness, QA |
| HyperFrames 0.8.150 + GSAP (video-editor skill) | ✅ | Restored in `.claude/skills/video-editor/engine/`. Titles, cursor and click highlights, zooms, end card. The skill's layouts are 9:16; **a 16:9 brand layout must be added** |
| Fonts | ✅ | Hind Siliguri (OFL) |
| Python numpy + Pillow | ✅ | Masks, overlays, contact sheets, music generator |
| Music | ✅ | `music_bed_4min` and `music_promo_48s`, original and owner-approved (`../digital-studio-reel/audio/`) |
| ElevenLabs (connector) | ❌ **blocked** | Samples worked, then: "Free Tier access has been disabled … upgrade to a paid subscription". The free tier also does not allow commercial use |
| Other Bangla TTS | ❌ | HyperFrames TTS (Kokoro) has no Bangla voice; Microsoft edge-tts is blocked by the network |
| Persistent browser with the demo shop logged in | ✅ | Running in the background (it ends with the session) |

## 2. What can be automated here

- Recording every scene clip from the demo accounts.
- Privacy edits: number → `01700-000000`, password blur, crops.
- Titles, cursor highlights and zooms, the end card, the music mix, both
  exports, QA, thumbnails and contact sheets.
- **Not possible right now:** the voice-over (see 3).

## 3. Missing keys, permissions or decisions

1. **Voice.** A paid ElevenLabs plan, or the owner's own recording. No
   paid service is used without the owner's approval.
2. **Approval for new demo records** (list in 6).
3. **The portrait** used for the photo tool: the brief says "synthetic";
   the image on file is the one the owner sent. Need confirmation that it
   is AI-made, or that the person agreed to appear.
4. **VO text** (see 7).

## 4. Features verified live (`../digital-studio-reel/test-report.md`)

| Feature | Test | Safe to show |
|---|---|---|
| Login page, role tabs | public pages | ✅ |
| Shop registration with mobile + SMS code → dashboard | R1–R6 | ✅ from footage already captured (no new SMS) |
| 1 GB free storage for a new shop | R7 | ✅ |
| Add customer, welcome card | R9 | ✅ (password hidden) |
| Upload JPG/PDF; "প্রতিটি সর্বোচ্চ ২৫ এমবি" | R10, label on screen | ✅ The 25 MB limit is the app's own label; a 25 MB file was **not** uploaded |
| Customer login, আমার ফাইল, download | R11–R12 | ✅ |
| Job done → notification → 5-star review | R13 | ✅ |
| Passport photo: 35×45 mm, light-blue background, A4 sheet × 8, save to folder | R14–R15 | ✅ |
| NID A4 with a synthetic DEMO card, auto-straighten, PDF | R16 | ✅ |
| Product, cash order, status flow, report ৳450 | R18–R21 | ✅ cash only |
| Service order, price ৳50, status | R22–R23 | ✅ |
| Staff add + staff login | R26–R27 | ✅ (see 5) |

## 5. Not safe to show or claim

- **bKash / Nagad / Rocket.** Saving fails with HTTP 403 (R17). Excluded
  until the developer fix is re-tested.
- **Staff privacy claim.** Plain staff still see the income number on the
  dashboard (R27). The VO must **not** say income or reports are owner-only.
- **Other features left out:** AI (photo edit, ad text, assistant),
  virtual assistant, Gmail login, ads (প্রচার), nearby-shop distance,
  customer self sign-up, mobile app, 15 GB.
- **Never record:**
  - the customer **home** page (it shows other shops and another shop's ad);
  - the ready-made CV template (a real person's CV);
  - the real NID that was offered.

## 6. New demo records that recording will create (needs approval)

All of these are on the demo shop (code 6414) and its demo customer only.
No real account is touched.

| Clip | New rows | Alternative with no new rows |
|---|---|---|
| `add_customer` | 1 more customer (needs one more **unused** number) | Fill the form without submitting, then cut to the existing "ডেমো কাস্টমার" in the list. The welcome card is not shown again |
| `upload` | 2 file rows (demo-cv.pdf/.jpg again) | Delete the two existing demo files first, then re-upload (net zero) |
| `done_review` | 1–2 notifications (toggle done off → on) | The review cannot be repeated (one per customer). Show the existing ★★★★★ review |
| `photo_tool` | 0 (download only); 1 file row if "ফোল্ডারে রাখুন" is shown | Skip the save step |
| `nid_tool` | 0 | — |
| `orders` | 1 product order (status changes; report becomes ৳900) | Show the existing completed order and report ৳450 only |
| `service_order` | 1 service order | Show the existing order (price ৳50, "চলছে") and finish it to "সম্পন্ন" (1 status change) |
| `staff` | 0 | Show the existing "ডেমো স্টাফ" |
| `register` | 0 | Form filled, **not** submitted. The code step and the dashboard come from the real test footage (screenshots R4–R6) with the number replaced |

## 7. Voice-over text: one problem

The VO lines in the master prompt add up to **316 words ≈ 2 min 24 s of
speech** at 2.2 words/s, but the tutorial timeline is **4 min 50 s**. That
would leave about half the video without speech.

Several lines are also production notes, not things to say to a shop
owner:
- "test report অনুযায়ী দেখান";
- "সংবেদনশীল তথ্য কখনো ভিডিওতে প্রকাশ করবেন না";
- "permission অনুযায়ী যাচাই করুন".

Proposal: use `script-tutorial.md` (about 590 words, already matched to
the verified features). Change its staff line to the safe wording in 5, and
take the master prompt's hook and CTA wording where it is better.

## 8. Execution plan

1. Owner approves: 6 (records), 7 (VO text), the portrait, and the voice
   route.
2. Add a 16:9 layout to the video-editor skill (brand variant).
3. Record the 12 clips with the CDP screencast; privacy pass with frame
   sheets.
4. Assemble both timelines (titles, highlights, end card with logo, URL,
   "Developed by Yousuf Digital Center", the address "College Road,
   Kankirhat, Senbagh, Noakhali" and 01865453564).
5. Mix music; add the VO when it exists. Without a VO, a music-only draft
   with on-screen text can be delivered for review, **clearly labelled as
   having no VO**.
6. Export, QA (`qa-report.md`), thumbnails, contact sheets.
