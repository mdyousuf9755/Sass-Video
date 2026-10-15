# Digital Studio: feature inventory

**Status: Phase 1 in progress (2026-10-15). Demo shop registered and all 12 shop tabs open without errors (see `test-report.md`).** Every tab and function below
was found by reading the live site's code. The public screens were also
opened in a real browser. **Nothing behind login has been tested yet.** The
live login and data server (Supabase) is blocked by this cloud session's
network policy, and no demo account exists.

Sources:
- **The site's own code.** `app.js`, downloaded from
  `digital-studio-bd.pages.dev` on 2026-10-15 and read line by line. The
  full notes, with line numbers, are in
  [`inspection/code-inventory.md`](inspection/code-inventory.md).
- **Browser screenshots of the public screens** (headless Chromium, desktop
  1920×1080 and mobile 390×844), in [`inspection/`](inspection/).
  - No form was submitted, and no code was sent or requested.
  - The Facebook Pixel and visitor counter were blocked during the visit,
    so the owner's statistics were not affected.
- **The owner's screenshots** from 2026-10-12.

Test-status legend:

| Mark | Meaning |
|---|---|
| ✅ | Tested live: the action ran and succeeded |
| 🖥 | Public screen opened live and rendered correctly; the action itself was not submitted |
| 👁 | Seen working in the owner's screenshots, not tested by Claude |
| 📄 | Found in the code only. Exists, but untested, and never shown |
| ⚠️ | Gated or possibly not live. Do not show it until it has been tested |
| ⛔ | Blocked. Needs a demo account or network access |

**Nothing is ✅ yet.** Every row needs a live test with a demo account before
it goes into a final script.

## A. Public screens (no login)

| # | Screen | Elements / functions (exact labels) | Status | Suggested scene |
|---|---|---|---|---|
| A1 | Login: role tabs | কাস্টমার · দোকানদার · অ্যাডমিন; left panel text changes per role | 🖥 | Opening |
| A2 | Shop-owner login | "Gmail দিয়ে লগইন / রেজিস্ট্রেশন"; mobile number with a country picker (20 codes, +880 default) and password with "দেখুন" (show); "লগইন করুন"; "দোকান রেজিস্ট্রেশন করুন". Staff log in here with their own mobile number | 🖥 (login not submitted) | Login demo |
| A3 | Shop registration, mobile route | "দোকান রেজিস্ট্রেশন": shop name, address, mobile, password (8+ characters), trade licence (image or PDF, "শুধু অ্যাডমিন দেখবেন"); "কোড পাঠান ও রেজিস্ট্রেশন করুন" sends a 6-digit SMS code to Bangladeshi numbers. The page itself says "অ্যাডমিন অনুমোদন দিলে দোকান চালু হবে" | 🖥 (not submitted) | Registration demo |
| A4 | Shop registration, Gmail route | "Gmail দিয়ে রেজিস্ট্রেশন করুন" → Google sign-in → "দোকানের তথ্য দিন" form | 🖥 button / 👁 form / ⛔ | Registration demo |
| A5 | After registering: approval gate | Waiting screen until the admin approves (unless the admin switched auto-approve on) | 📄 ⛔ | Mention: "অনুমোদনের পর চালু" |
| A6 | Customer login | "আপনার ফাইলে ঢুকুন": username (mobile number) + password; note "আপনার দোকানদার ইউজারনেম ও পাসওয়ার্ড তৈরি করে দেবেন।" | 🖥 | Customer login |
| A7 | Customer self sign-up | "মোবাইল নম্বর দিয়ে অ্যাকাউন্ট খুলুন" → name + mobile → SMS code → password. The button shows only when the admin turns it on. It did not show in this test, but that may be because the server was blocked | ⚠️ ⛔ | Leave out until confirmed |
| A8 | Admin login | Email + password, "পাসওয়ার্ড ভুলে গেছেন?" | 🖥 | Not in videos |

## B. Shop-owner panel

Tabs, in order: ড্যাশবোর্ড, কাস্টমার, সেবা, শপ, প্রচার, টেমপ্লেট, রিপোর্ট,
স্টোরেজ, সহায়তা, স্টাফ, প্রোফাইল, নোটিফিকেশন. Plain staff do not see
রিপোর্ট, স্টোরেজ, স্টাফ or প্রোফাইল. Managers see everything except
স্টাফ. Idle logout happens after 30 minutes.

| # | Tab | Functions | Status | Suggested scene |
|---|---|---|---|---|
| B1 | ড্যাশবোর্ড | Welcome, shop code, "+ নতুন কাস্টমার"; counters (new orders, customers, products, income); profile views with a chart; recent activity; storage card ("আরও স্টোরেজ কিনুন"); AI credit box | 👁 ⛔ | Dashboard tour |
| B2 | কাস্টমার: new | Name, mobile, password (8+ characters); username = mobile number. A welcome card shows the login details to pass on (SMS, WhatsApp or copy; automatic SMS only if the admin enabled it) | 👁 ⛔ | Add customer (**blur the password**) |
| B3 | কাস্টমার: other shop's customer | Search by username; ask for access; the customer approves or revokes | 👁 📄 ⛔ | Optional |
| B4 | Customer folder | Profile + edit; "কাজ সম্পন্ন হয়েছে বলে চিহ্নিত করুন" (mark job done); upload JPG/PNG/WebP/PDF up to 25 MB each; "ডকুমেন্ট স্ক্যান" (phone camera photo, **no auto-straightening**); download / delete; password reset; report customer | 👁 ⛔ | File upload |
| B5 ✅ | সেবা → ফটো এডিট | Passport photo maker in the browser: 35×45 / 45×55 / 25×30 mm or custom size; rotate and straighten; **background change** (white / light blue / grey / transparent); zoom, brightness, contrast; export JPG/PNG or an **A4 sheet of 4–20 copies** as PDF/JPG; save directly into a customer's folder | 📄 ⛔ | **Strong new scene** |
| B6 | সেবা → AI এডিট (inside ফটো এডিট) | "AI দিয়ে লিখে এডিট": typed prompt or quick chips (e.g. a black coat, white shirt and tie). 1 credit per image | ⚠️ the code has an error text "এখনো চালু হয়নি (Google বিলিং বাকি)" | **Leave out until tested** |
| B7 ✅ | সেবা → এনআইডি A4 | Front + back NID photos → auto-straighten (±20°) → real card size on A4 as PDF/JPG | 📄 ⛔ | Strong new scene (**use a fake/sample card only**) |
| B8 | শপ → পণ্য | Add product: name, price, stock, description, extra info, image (2 MB); up to 200 products | 👁 ⛔ | Shop |
| B9 | শপ → পণ্যের অর্ডার / সেবার অর্ডার | Order list, status updates, confirming payment | 📄 ⛔ | Orders |
| B10 | শপ → পেমেন্ট | Cash; bKash / Nagad / Rocket numbers; bank (optional). Money goes straight to the shop | 👁 ⛔ | Payment (**blur the numbers**) |
| B11 | প্রচার | New ad with "AI দিয়ে লিখুন"; title 60 / body 140 characters; image; admin approval → "স্পনসর্ড" on customers' home; up to 5 ads | 👁 ⚠️ (AI text needs the server's AI key) | Promotion |
| B12 | টেমপ্লেট | Ready-made files (CV/biodata, DOCX); design templates (visiting card, poster, banner) | 👁 ⛔ | Templates |
| B13 | রিপোর্ট | Total and completed orders, income, monthly accounts, top-selling services and products | 👁 ⛔ | Reports |
| B14 | স্টোরেজ | Storage used; buy a plan or AI credits **manually** (pay the admin's bKash/Nagad, enter the transaction ID, admin approves). Prices come from the database | 📄 ⛔ | Brief mention only |
| B15 | সহায়তা | FAQ, feedback form ("মতামত"). The "AI সহকারী" card is **placeholder only** | 📄 ⚠️ | Feedback CTA (**never show AI সহকারী**) |
| B16 | স্টাফ | Owner only: up to 10 staff, role স্টাফ or ম্যানেজার, each with their own mobile login | 📄 ⛔ | Tutorial only |
| B17 | প্রোফাইল | Public shop page: cover, photo, bio, services, links, gallery (30), map location; login card (mobile/Gmail); trade licence | 📄 ⛔ | Tutorial only (**blur contacts and GPS**) |
| B18 | নোটিফিকেশন | List, mark as read | 👁 ⛔ | Brief |

## C. Customer panel

Tabs: হোম, আমার ফাইল, আমার দোকান, অর্ডার, নোটিফিকেশন, সাহায্য,
আমার প্রোফাইল, বের হন.

| # | Tab | Functions | Status | Suggested scene |
|---|---|---|---|---|
| C1 | হোম | Job-done banner + "রিভিউ দিন"; sponsored ads; service tiles; nearby shops (location with permission); all shops + search | 👁 ⛔ | Customer side |
| C2 | Shop page | "এই দোকানকে অনুমতি দিন"; cover, services, address, gallery, reviews | 👁 ⛔ | Nearby shops |
| C3 | আমার ফাইল | View and download the files the shop uploaded | 👁 ⛔ | Customer downloads |
| C4 | আমার দোকান | Products, shop info, review + stars, report this shop | 👁 ⛔ | Reviews |
| C5 | অর্ডার | Product and service orders, payment (txn ID), status | 📄 ⛔ | Tutorial only |
| C6 | নোটিফিকেশন | List with "নতুন" (New) badge | 👁 ⛔ | Brief |
| C7 | সাহায্য | FAQ (it wrongly says customers cannot self-register; see D) | 📄 ⛔ | Skip |
| C8 | আমার প্রোফাইল | Photo, name, profession, address; change password; shop permissions | 👁 ⛔ | Tutorial only |

## D. Problems and things to check

These are reported separately, as the brief asks. **They come from reading
the code and the public pages. None was confirmed in a live test.** Nothing
was changed on the site.

| # | Problem | Seen where | Severity |
|---|---|---|---|
| D1 | ~~"1 GB free" is not in the code~~ **Resolved 2026-10-15:** a newly registered demo shop shows "০ বাইট / ১.০০ জিবি" (test-report R7). The CTA claim is true | Live ✅ | Resolved |
| D2 | Shop owners and staff have no "forgot password" and no in-app password change; only the admin has one | Code | Medium |
| D3 | The customer FAQ says "নিজে অ্যাকাউন্ট খোলা যায় না", which contradicts the self sign-up feature | Code | Low |
| D4 | Plain staff: "আরও স্টোরেজ কিনুন" and "ক্রেডিট কিনুন" do nothing visible (the page is hidden from them) | Code | Low |
| D5 | Developer setup messages could reach users ("Supabase-এ Confirm email বন্ধ করুন", "GEMINI_API_KEY বসাতে হবে") | Code | Low |
| D6 | Social-link icons load from an `icons/` folder; if it is missing, profiles show broken images | Code | Check live |
| D7 | Mobile registration page: in the full-page screenshot the dark background stops partway and the rest is light grey | Browser 🖥 | Cosmetic, check on a phone |
| D8 | The file pickers show the browser's English "Choose File / No file chosen" | Browser 🖥 | Cosmetic |
| D9 | The views chart is labelled "গত ১৪ দিনের" (last 14 days) while its caption says 30 days | Code | Cosmetic |
| D10 | `supabase-js@2` is loaded without an exact version; the site's own HTML comment says to pin it | Code | Maintenance |
| D12 | After a registration error the page clears the password and licence file (test-report R3) | Live | Low |
| D13 | First SMS code did not arrive; the resend did (test-report R5) | Live | Watch |
| D14 | The সহায়তা tab shows a "ভার্চুয়াল অ্যাসিস্ট্যান্ট (আমাদের টিম)" request form, though the owner says it is not launched | Live | Keep out of videos |
| D15 | New-customer form: if "কাস্টমার যোগ করুন" is pressed while the number is still being checked, the page re-renders, clears the password and **re-ticks "অটো SMS পাঠান"** even if the owner unticked it, so an SMS could go out unintentionally (test-report R9) | Live | Medium |
| D16 | Photo tool: saving the A4 sheet to a customer's folder shows no confirmation message (test-report R15) | Live | Low |
| D17 | NID tool: auto-trim leaves a thin strip of background at the card's side edges (test-report R16) | Live | Low |
| D18 | **Payment settings cannot be saved by a new shop**: `payment_settings` upsert → HTTP 403 (row-level security), even with cash only. Customers of new shops can only pay cash (test-report R17) | Live | **High** |
| D19 | New orders reach the shop panel only after a page reload (test-report R20) | Live | Low |
| D20 | **Privacy:** the only ready-made template ("English 2 page cv") is a real person's CV with name, address, mobile and email, downloadable by every shop. Replace it with a dummy CV and never show it in a video (test-report R24) | Live | **High** |
| D11 | AI photo edit may not be live (error text "Google বিলিং বাকি"); the "AI সহকারী" card is placeholder text | Code | **Keep both out of the videos** |

## E. Rules for the scripts that follow from this

- **Do not claim:**
  - automatic scan straightening (it exists only in the NID tool);
  - AI photo editing or the AI assistant;
  - customer self sign-up;
  - a mobile app;
  - 15 GB;
- **Strong new scenes to verify first:**
  - the passport photo maker (B5), with background change and an A4 sheet;
  - the NID A4 tool (B7), with a sample card only;
  - staff accounts (B16).
- **Blur list:** the code shows passwords in plain text on the new-customer
  welcome card and the reset screen. Payment numbers, transaction IDs, NID
  images, GPS coordinates, the shop code and the Gmail on the login card
  also need covering. The full list per screen is in
  `inspection/code-inventory.md` §8.

## F. What is needed to finish Phase 1

1. **Network:** allow `tukeabjoxguklbjieuzd.supabase.co` and
   `cdn.jsdelivr.net` for this environment (the login and data server).
2. **A dedicated test Gmail or test mobile number** that the owner controls,
   plus permission to create **one demo shop and one demo customer**. The
   brief forbids using the owner's own account or getting around
   verification.
3. **The admin approves the demo shop.** Shop registration needs admin
   approval (A5).
