# Pre-delivery checklist

Run `python3 scripts/vedit.py qa out/<file>.mp4` and view the contact sheet.
Then tick every line. Anything unticked is a blocker.

## Content
- [ ] The script was followed. Every headline and text line matches the
      approved Bangla text, and the spelling and conjuncts were proofread.
- [ ] With the sound **off**, the whole message is understandable from the
      text alone, and every line can be read before it disappears.
- [ ] Every feature shown exists and works today; any prices or offers are
      confirmed.
- [ ] No mobile-app claims (no app download, store or install wording). The
      URL is correct: digital-studio-bd.pages.dev.
- [ ] The CTA reads "টেস্ট ভার্সনে ১ জিবি ফ্রি – আজই রেজিস্টার করুন:
      digital-studio-bd.pages.dev | আপনার মতামত জানান".

## Privacy
- [ ] Every screen scene was checked frame by frame on the
      `frames --every 0.5` sheets **after** the blur. No phone numbers,
      emails, passwords, OTPs, customer names or numbers, or payment details
      are visible, including mid-scroll and during zooms.
- [ ] Only the shop name and address are readable.

## Brand and layout
- [ ] Only teal, dark green and gold, the Hind Siliguri font, and the real
      logo (not the "DS" placeholder) appear.
- [ ] The logo appears at the start and the end.
- [ ] All text is inside the red safe-zone box on the contact sheet, and
      nothing important sits under the Reels UI at the bottom or right.

## Audio
- [ ] There is no voice-over (unless this project asked for one). The music
      is upbeat and fits the brand.
- [ ] The cuts land on the beat, and the music starts and ends cleanly
      (fades).
- [ ] The SFX are subtle and in time: whoosh on cuts, pop on text, click on
      taps.
- [ ] QA reports loudness of -14 ± 1 LUFS and true peak ≤ -1.5 dBTP.
- [ ] The music is royalty-free and licensed. The placeholder bed was **not**
      used.

## Technical (QA script)
- [ ] 1080×1920, 30 fps, H.264 yuv420p, AAC 48 kHz.
- [ ] Duration is under 60 s, target 45 ± 3 s.
- [ ] No black frames and no long silences.
- [ ] Watched once on a phone screen.

## Delivery
- [ ] `Project_vN_9x16_YYYY-MM-DD.mp4`, plus the `.srt` and `_cover.jpg`.
- [ ] `version` was bumped for this revision.
- [ ] Final approval received.
