# Registration and login test report

Live tests on `digital-studio-bd.pages.dev` from a headless Chromium session.
Facebook Pixel and visitor-count requests were blocked so tests do not
pollute the owner's statistics. Passwords and SMS codes are never written
here.

| # | Date | Test | Input | Result | Status |
|---|---|---|---|---|---|
| R1 | 2026-10-15 | Shop registration, mobile route: fill the form | Shop "Yousuf Printing Shop", demo address (Jatrabari, Dhaka), mobile 01581470954, 8+ char password, demo trade licence (WebP, marked "DEMO – NOT A VALID LICENSE") | Form accepted all fields, file picker shows the licence | ✅ |
| R2 | 2026-10-15 | Press "কোড পাঠান ও রেজিস্ট্রেশন করুন" | as R1 | Server `shop-auth` answered **HTTP 409**; page shows "এই মোবাইল নম্বর আগেই ব্যবহার হয়েছে". **No SMS was sent and no account was created.** The duplicate-number check works | ✅ (check works) / ⛔ demo shop not created |

| R3 | 2026-10-15 | Fix the number after the R2 error | New test number (owner-supplied, kept private; videos show 01700-000000) | The page **cleared the password and the licence file** after the error; both had to be entered again (other fields kept) | ⚠️ usability |
| R4 | 2026-10-15 | Request SMS code | as R1 with the new number | "০১… নম্বরে ৬ অঙ্কের কোড পাঠানো হয়েছে"; page moves to "মোবাইল নম্বর যাচাই" | ✅ |
| R5 | 2026-10-15 | "কোড আসেনি? আবার পাঠান" | after 60 s | "নতুন কোড পাঠানো হয়েছে". The owner reported the first SMS did not arrive; a code did arrive after the resend | ✅ (first SMS possibly lost) |
| R6 | 2026-10-15 | Enter the code, "রেজিস্ট্রেশন শেষ করুন" | 6-digit code from the owner | Account created, logged in and **taken straight to the dashboard** (no approval wait: admin auto-approve is on). Took about 9 s. No licence-upload error shown | ✅ |
| R7 | 2026-10-15 | New shop's storage | — | Dashboard and স্টোরেজ show **"০ বাইট / ১.০০ জিবি"**. **"১ জিবি ফ্রি" confirmed for a new shop** | ✅ |
| R8 | 2026-10-15 | Open every shop tab once (read only) | ড্যাশবোর্ড, কাস্টমার, সেবা, শপ, প্রচার, টেমপ্লেট, রিপোর্ট, স্টোরেজ, সহায়তা, স্টাফ, প্রোফাইল, নোটিফিকেশন | All 12 tabs open with no console or HTTP errors | ✅ |
| R9 | 2026-10-15 | Add a demo customer (কাস্টমার → নতুন কাস্টমার) | Name "ডেমো কাস্টমার", owner-supplied test mobile (videos show 01700-000000), 8+ char password, **auto-SMS unticked** | First click too early: "নম্বর যাচাই হচ্ছে, এক সেকেন্ড পরে চাপুন". That re-render **cleared the password and re-ticked the auto-SMS box**. After re-entering and unticking: "কাস্টমার তৈরি হয়েছে", welcome card with login text, SMS / WhatsApp / copy buttons. No SMS sent | ✅ / ⚠️ bug |

The first number (01581470954) was already registered, so R2 stopped as the
brief requires; no login was attempted on that existing account.

## Demo shop

- Name "Yousuf Printing Shop", address "Shop No. 12, Ground Floor, Main
  Road, Jatrabari, South Dhaka, Dhaka-1204" (from the owner's DEMO licence).
- Shop code 6414. Login details are in `demo-account/` (git-ignored), never
  in git or on screen.

## Facts seen live in the new shop (R8)

- **Storage plans** (স্টোরেজ): +500 MB ৳50, +1 GB ৳90, +5 GB ৳400.
  **AI credits**: 10 edits ৳80, 30 ৳210, 100 ৳650. Rotation, size and
  background change are free; only AI edits use credits.
- **সহায়তা**: "AI সহকারী" says an API key is still needed (not live). A
  "ভার্চুয়াল অ্যাসিস্ট্যান্ট (আমাদের টিম)" request form is visible
  (design, online forms, typing, social setup). The owner said the virtual
  assistant is not launched, so it stays out of the videos.
- **টেমপ্লেট**: one ready-made file ("English 2 page cv", DOCX) and the
  visiting card / poster / banner designer with SVG download.
- **কাস্টমার**: auto-SMS checkbox shows "আজ বাকি ২০টি".
- **স্টাফ**: staff or manager role, login on the দোকানদার tab.

## Other observations

- On desktop 1920×1080 the registration page is taller than the window and
  the teal page background stops at the bottom of the first screen (white
  strip below). Same as D7 in `feature-inventory.md`, now seen on desktop too.
