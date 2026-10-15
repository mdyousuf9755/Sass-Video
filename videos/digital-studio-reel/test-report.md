# Registration and login test report

Live tests on `digital-studio-bd.pages.dev` from a headless Chromium session.
Facebook Pixel and visitor-count requests were blocked so tests do not
pollute the owner's statistics. Passwords and SMS codes are never written
here.

| # | Date | Test | Input | Result | Status |
|---|---|---|---|---|---|
| R1 | 2026-10-15 | Shop registration, mobile route: fill the form | Shop "Yousuf Printing Shop", demo address (Jatrabari, Dhaka), mobile 01581470954, 8+ char password, demo trade licence (WebP, marked "DEMO – NOT A VALID LICENSE") | Form accepted all fields, file picker shows the licence | ✅ |
| R2 | 2026-10-15 | Press "কোড পাঠান ও রেজিস্ট্রেশন করুন" | as R1 | Server `shop-auth` answered **HTTP 409**; page shows "এই মোবাইল নম্বর আগেই ব্যবহার হয়েছে". **No SMS was sent and no account was created.** The duplicate-number check works | ✅ (check works) / ⛔ demo shop not created |

## Blocker

01581470954 is already registered on the platform (as a shop, staff member
or customer). Registration stopped here, as the brief requires. No login was
attempted on that existing account.

## Other observations

- On desktop 1920×1080 the registration page is taller than the window and
  the teal page background stops at the bottom of the first screen (white
  strip below). Same as D7 in `feature-inventory.md`, now seen on desktop too.
