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

| R10 | 2026-10-15 | Upload files to the demo customer (shop side) | Two sample files made for the test ("Demo CV", PDF 97 KB + JPG 130 KB, no real person) | "আপলোড হয়েছে"; "ফাইল (২)" listed with size, ডাউনলোড / মুছুন | ✅ |
| R11 | 2026-10-15 | Download from the shop side | demo-cv.pdf | Downloaded file is byte-identical (99,270 bytes) | ✅ |
| R12 | 2026-10-15 | Customer login + every customer tab (separate browser) | Demo customer's mobile + password | Login OK. হোম, আমার ফাইল, আমার দোকান, অর্ডার, নোটিফিকেশন, সাহায্য, আমার প্রোফাইল all open with no errors. Both files listed; JPG download OK. Home shows a real sponsored ad and other real shops in "সব দোকান" | ✅ |
| R13 | 2026-10-15 | Mark job done (shop) → notification → review (customer) | 5 stars + demo comment | Shop button turns into "✓ কাজ সম্পন্ন (বাতিল করতে চাপুন)". Customer gets notification "আপনার কাজ সম্পন্ন হয়েছে…" (badge "নোটিফিকেশন (১)") and a home banner with "রিভিউ দিন". Review submitted: "আপনি রিভিউ দিয়েছেন। ধন্যবাদ!", shop rating ৫.০ | ✅ |

| R14 | 2026-10-15 | সেবা → ফটো এডিট: passport photo | Owner-supplied portrait (used with permission) | Loaded; 35×45 mm at 300 DPI (413×531 px). Background "হালকা নীল" with the smart (person-detection) method: "✓ মানুষ আলাদা করা হয়েছে…". Downloads OK: photo JPG, A4 sheet PDF and JPG with 8 copies. Slight white halo at the hair and ear edges | ✅ |
| R15 | 2026-10-15 | Photo tool → "A4 শিট (PDF) কাস্টমারের ফোল্ডারে রাখুন" | Demo customer | File appears in the folder ("ফাইল (৩)", photo-sheet-a4.pdf 446 KB). **No on-screen confirmation** was visible after saving | ✅ / ⚠️ UX |
| R16 | 2026-10-15 | সেবা → এনআইডি A4 | Generic "DEMO ID CARD" made for the test (fake data, no real person), photographed tilted +6° / −5° on a desk | Auto-straighten detected −6° and +5° exactly. A4 PDF and JPG: both sides straight, real card size, centred. Auto-trim leaves a thin strip of the desk on the left and right edges | ✅ / ⚠️ minor |

| R17 | 2026-10-15 | শপ → পেমেন্ট: save bKash/Nagad/Rocket | Demo number 01700000000 (owner-approved) | **Failed**: "কিছু একটা সমস্যা হয়েছে, আবার চেষ্টা করুন"; server `POST /rest/v1/payment_settings` → **HTTP 403**. Also fails with **no number at all** (cash only), so it is not the number. The upsert is refused by the table's row-level security for a new shop with no row yet. Nothing saved | ❌ **bug** |
| R18 | 2026-10-15 | শপ → পণ্য: add product | "ডেমো পেনড্রাইভ 16GB", ৳450, stock 10, description, extra info, demo image | "যোগ হয়েছে"; "আমার পণ্য (১)" | ✅ |
| R19 | 2026-10-15 | Customer orders the product | Qty 1, payment "ক্যাশ অন ডেলিভারি" (the only method, because of R17), note | "অর্ডার হয়েছে। দোকানদার নিশ্চিত করবেন।"; customer অর্ডার tab: "× ১ নতুন · মোট ৪৫০ টাকা · ক্যাশ" | ✅ |
| R20 | 2026-10-15 | Shop sees the order | — | Shown only **after a page reload** (badges "শপ (১)", "নতুন অর্ডার ১"); no live update | ✅ / ⚠️ UX |
| R21 | 2026-10-15 | Shop: প্রক্রিয়ায় → নগদ পেয়েছি → সম্পন্ন | — | "আপডেট হয়েছে", "পেমেন্ট নিশ্চিত হয়েছে"; status "সম্পন্ন · পরিশোধিত". রিপোর্ট: 1 order, 1 completed, income ৳450, "অক্টোবর ২০২৬ · ১টি অর্ডার · ৪৫০ টাকা", top product listed | ✅ |

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

## Recording notes from the customer side

- The customer **হোম** shows other real shops (names and addresses) under
  "সব দোকান" and a real sponsored ad from another shop. Shop name and
  address are allowed on screen, but these are third parties: crop or blur
  them, or show only the demo shop.
- A real person's NID (shared online) was offered for the NID test. It was
  **not used**: it carries a real name, NID number, address and face. The
  generic DEMO ID card is used in its place.
