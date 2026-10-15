# 45-second reel: beat sheet and on-screen Bangla copy

There is **no voice-over**. Music and sound effects set the mood; the
on-screen text tells the story. Each scene has:
- a **headline**: big and bold, at most 6–8 words, with one `*gold*` accent
  word;
- 0–2 **text lines**: smaller pills under the headline, about 2–5 words
  each, appearing one after the other.

Viewers scroll fast and read with the sound off, so every line must be
readable at a glance.

## Beat sheet

| # | Scene id | Type | Time | Job | Text lines |
|---|---|---|---|---|---|
| 1 | `hook` | title | 0–3 s | Stop the scroll: a question about the viewer's pain | 1 |
| 2 | `problem` | title | 3–7 s | Name the daily hassle in concrete terms | 2 |
| 3 | `intro` | logo | 7–10 s | Logo reveal, plus a one-line promise | 1 |
| 4–6 | `feature1..3` | screen | 10–36 s | One feature each: show it, zoom in, tap. Headline = what it is; lines = what it does and why it helps | 1–2 each |
| 7 | `benefit` | title | 36–39 s | Free, runs in the browser, no install needed | 1 |
| 8 | `cta` | cta | 39–45 s | Register free today, plus feedback (fixed CTA card from `brand.json`) | — |

**Feature tour pattern:** for a feature with several options (a menu, a
settings page, a form), use one screen scene with `steps`: the cursor
clicks each option in order and a numbered label (১, ২, ৩ …) names it.
Keep each label to 1–3 words (the option's name as it appears in the app),
with about 1.2–1.5 s between clicks. With `follow: true` the camera rides
along. A good tour has 3–6 steps; split longer tours into two scenes.

Screen scenes carry most of the time: the demo plays at natural speed for up
to 8 s per feature. Two features with longer demos also work. Never squeeze
the hook or the CTA.

## Timing (automatic)

- A text line stays on screen for `max(1.4 s, characters ÷ 11)`; tune this
  with `captions.reading_cps` and `min_line_seconds` in `brand.json`.
- A scene is long enough for its lines; screen scenes also follow the clip
  length (up to 8 s).
- With `music.bpm: "auto"`, scene lengths round up to whole beats, so every
  cut, whoosh and headline pop lands on the music.

## Copy rules

- **Language:** everyday spoken Bangla (চলিত ভাষা). Use "আপনি" with the
  viewer. Prefer short words.
- **Line length:** about 5 words or fewer per line. If a thought is longer,
  split it into two lines; never use three.
- **Hook:** a question or bold statement in the headline, for example
  "দোকানের সব কাজ এখনো *খাতায়*?" ("Still doing all your shop work in a
  *ledger*?")
- **Feature scenes:** the headline names the result ("সব *অর্ডার* এক
  জায়গায়", "All your *orders* in one place"); the line says the action or
  benefit ("এক স্ক্রিনেই দেখুন", "See it all on one screen"). Don't repeat
  the headline in the line.
- **Truth:** every feature named must appear in a recording and work today.
  No prices or offers unless the user confirms them.
- **Web-only:** say "ব্রাউজারেই চলে" (runs in the browser), "কোনো ইনস্টল
  লাগবে না" (no install needed), or "যেকোনো ডিভাইসের ব্রাউজারে" (in any
  device's browser). Never say মোবাইল অ্যাপ (mobile app), অ্যাপ ডাউনলোড (app
  download), Play Store, or ইনস্টল করুন (install it).
- **Brand name** is written in Latin script: "Digital Studio".
- **Numbers** match the app (Bangla digits if the app shows them).
- **Punctuation:** use "?" for the hook. Leave the "।" (dari, the Bangla full
  stop) off short lines because it adds clutter.

## Example (replace the features with what the recordings show)

| Scene | Headline | Text lines |
|---|---|---|
| hook | দোকানের সব কাজ এখনো \*খাতায়\*? | হিসাব মেলাতে রোজ ঝামেলা? |
| problem | সময় নষ্ট, ভুলের \*ঝুঁকি\* | অর্ডার হারিয়ে যায় · হিসাব মেলে না |
| intro | (logo + tagline) | আপনার ব্যবসার সহজ সমাধান |
| feature1 | সব \*অর্ডার\* এক জায়গায় | দোকানের প্রোফাইল আর সব অর্ডার · এক স্ক্রিনেই দেখুন |
| feature2 | এক নজরে \*আজকের বিক্রি\* | আজকের বিক্রি আর নতুন অর্ডার · এক নজরে |
| feature3 | গ্রাহকের তথ্য \*নিরাপদ\* | গ্রাহকের তথ্য থাকে নিরাপদ |
| benefit | একদম \*ফ্রি\*, ব্রাউজারেই চলে | কোনো ইনস্টল লাগবে না |
| cta | (CTA card) | — |

What the example lines say in English:
- **hook:** "Still doing all your shop work in a *ledger*?" / "Daily hassle
  balancing the accounts?"
- **problem:** "Wasted time, risk of *mistakes*" / "Orders get lost · The
  accounts don't add up"
- **intro:** "An easy solution for your business"
- **feature1:** "All your *orders* in one place" / "Your shop profile and
  all orders · See it all on one screen"
- **feature2:** "*Today's sales* at a glance" / "Today's sales and new
  orders · At a glance"
- **feature3:** "Customer info stays *safe*"
- **benefit:** "Totally *free*, runs in the browser" / "No install needed"
