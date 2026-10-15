# Digital Studio: feature inventory from code (static read of app.js)

Source: `raw/app.js` (2334 lines), plus `index.html`, `config.js`, `pixel.js`, `style.css`. Read-only; no network calls made.
Line numbers (Lnnn) refer to app.js. All Bangla UI labels are quoted exactly as they appear in the code.

Stack: plain JS SPA, no framework. `supabase-js@2` comes from jsDelivr **without a version pin** (index.html). `config.js` holds the Supabase URL, a *publishable* key (value omitted here), `AUTH_DOMAIN: 'ds.digitalstudio.app'` and a Facebook Pixel ID. `pixel.js` loads the Meta Pixel and sends `PageView` on every screen/tab change, `Lead` when the register screen opens, and `CompleteRegistration` when a shop or customer signs up (L263, L538, L701, L2270-2271).

---

## 1. Screens, routing and roles

`S.screen` values (render map L2261):

| S.screen | Function | How you get there |
|---|---|---|
| `login` | `loginScreen()` L491 | The default screen. Also shown after logout and when a role is missing. |
| `csignup` | `csignupScreen()` L544 | Customer tab → "মোবাইল নম্বর দিয়ে অ্যাকাউন্ট খুলুন". This button appears only when the server flag `cust_signup_open` is true (L513, L2329). |
| `register` | `registerScreen()` L720 | Shop tab → "দোকান রেজিস্ট্রেশন করুন" (L516). |
| `gregister` | `gRegisterScreen()` L705 | Automatic: a Google login that has no profile role yet (route L202). |
| `setpw` | `setPwScreen()` L584 | A password-recovery link (`#type=recovery`) or the `PASSWORD_RECOVERY` event (L2322-2331). |
| `gate` | `gateScreen()` L744 plus the owner's `loginCard`/`licenseCard` | A shop user whose shop status is not `approved` (L208, L2261). |
| `shop` | `shopScreen()` L1470 | Role `shop` with shop status `approved` (L207). |
| `cust` | `custScreen()` L2091 | Role `customer` (L210). |
| `admin` | `adminScreen()` L2122 | Role `admin` (L205). |

**Roles** (`profiles.role`, L133). The login-tab role is checked against the profile role after sign-in (L228-231):
- **shop**: covers the owner and also staff. `S.isOwner = shops.owner_id === user.id`. `S.staffRole` is `'manager'` or `'staff'`. `S.mgr` = owner OR manager (L139).
- **customer** (UI key `cust`): linked to one home shop (`customers.shop_id`). A self-registered customer may have no shop (`shop_id` null).
- **admin**.
- **gate**: a shop that is pending, rejected or suspended (L744-757):
  - Pending: "অনুমোদনের অপেক্ষায়", with steps "আবেদন জমা" → "অ্যাডমিন যাচাই" → "দোকান চালু".
  - Rejected: "আবেদন গৃহীত হয়নি" plus "কারণ:" and the reason, and a button "আবার জমা দিন" (rpc `resubmit_shop`).
  - Suspended: "দোকান সাময়িক স্থগিত".
  - Buttons "অবস্থা দেখুন" and "বের হন".
  - The owner also sees the login-method card and the trade-license card (not when suspended).
- A user with no role who is not a Google user is signed out with "এই অ্যাকাউন্টের কোনো ভূমিকা নেই" (L203).

**Login email mapping** (L71-72, L121, L214-222). Auth is email-based under the hood:
- Shop: `s<mobile>@ds.digitalstudio.app`.
- Staff: `t<mobile>@…` is tried as a fallback.
- Customer: `u.<username>@…`.
- Admin: `a.<username>@…` or a real email.
- A final fallback for shops is the Edge Function `shop-auth` `{action:'login'}`, which lets a Gmail-registered shop log in by verified mobile number and password (L223-227).

**Session behaviour**
- Shop and admin users are logged out automatically after 30 minutes idle (L2280-2282). Customers are not.
- Heartbeats: `ping` every 60 s, and `guest_ping` visitor tracking for logged-out visitors (anonymous ID in localStorage, plus source/UTM and device) (L2285-2304).
- Polling: shop dashboard every 30 s (profile-view stats), admin overview every 15 s, and notifications every 30 s with a toast "নতুন নোটিফিকেশন এসেছে" (L2306-2321).

**Navigation**: `navTabs()` L447.
- Desktop: a sidebar, plus "বের হন".
- Mobile: a top bar ("Digital Studio" brand + page title + bell) and a bottom nav with 4 primary buttons plus "আরও". "আরও" opens the sheet "সব অপশন".
- Short labels in the bottom nav (L446): ড্যাশবোর্ড→হোম, আমার ফাইল→ফাইল, আমার দোকান→দোকান, আমার প্রোফাইল→প্রোফাইল, দোকান অনুমোদন→অনুমোদন, ওভারভিউ→হোম, সব দোকান→দোকান.

---

## 2. Public screens (no login)

### 2.1 Login, `loginScreen()` L491-517
- **Left brand panel** (`BR`, L425-429) has an illustration, a headline, a subline and 3 bullets that change with the selected role:
  - cust: "আপনার ফাইল, আপনার হাতের মুঠোয়". Bullets: "দোকানদারের দেওয়া ফাইল দেখুন ও ডাউনলোড করুন", "দোকানের পণ্য দেখুন ও অর্ডার করুন", "কেনা পণ্যের রিভিউ দিন".
  - shop: "কাস্টমারের ফাইল রাখুন গুছিয়ে". Sub: "আপনার দোকানের জন্য নিরাপদ অনলাইন স্টোরেজ, সব কাস্টমারের ফাইল এক জায়গায়।" Bullets: "প্রতি কাস্টমারের আলাদা লগইন", "পণ্য বিক্রি ও অর্ডার", "বিকাশ, নগদ, রকেট ও ক্যাশ পেমেন্ট".
  - admin: "পুরো প্ল্যাটফর্ম এক জায়গা থেকে".
  - The brand panel and illustration are hidden on screens under 800 px (style.css L232).
- **Role tabs** (L506): "কাস্টমার" (default), "দোকানদার", "অ্যাডমিন".
- **Customer tab**
  - Heading "আপনার ফাইলে ঢুকুন". Sub "আপনার ইউজারনেম ও পাসওয়ার্ড লিখুন। প্রথমবার দোকানদার যা দিয়েছেন সেটাই।"
  - Field "ইউজারনেম (মোবাইল নম্বর)", placeholder "যেমন: 01712345678". Then "পাসওয়ার্ড" with a show/hide toggle "দেখুন"/"লুকান".
  - Button "লগইন করুন".
  - If the server flag `cust_signup_open` is true: divider "নতুন কাস্টমার?" and button "মোবাইল নম্বর দিয়ে অ্যাকাউন্ট খুলুন".
  - Otherwise: the note "আপনার দোকানদার ইউজারনেম ও পাসওয়ার্ড তৈরি করে দেবেন।"
  - **No forgot-password for customers.**
- **Shop tab**
  - Heading "দোকানদার লগইন". Sub "Gmail দিয়ে এক চাপে ঢুকুন, অথবা মোবাইল নম্বর ও পাসওয়ার্ড দিন।"
  - Google button "Gmail দিয়ে লগইন / রেজিস্ট্রেশন" (Supabase OAuth, `prompt=select_account`).
  - Divider "অথবা মোবাইল নম্বর দিয়ে". Field "মোবাইল নম্বর" with a country-code dropdown: 20 countries, BD +880 is the default (L74-76). Then "পাসওয়ার্ড" and "লগইন করুন".
  - Divider "নতুন দোকান?" and button "দোকান রেজিস্ট্রেশন করুন".
  - Staff log in here with their own mobile number and password.
  - **No forgot-password for shops.**
- **Admin tab**: heading "অ্যাডমিন লগইন" ("শুধু অ্যাডমিনের জন্য।"), field "অ্যাডমিন ইমেইল" (placeholder you@example.com) and the link "পাসওয়ার্ড ভুলে গেছেন?". The link sends a Supabase reset email; the reply never reveals whether the account exists (L568-574).
- **Login errors** are deliberately generic: "ইউজারনেম বা পাসওয়ার্ড মেলেনি". If the server lockout fires: "আজ এই নম্বরে অনেকবার ভুল পাসওয়ার্ড দেওয়া হয়েছে। কাল আবার চেষ্টা করুন।" (`login_locked`).
- If the Google provider is not configured: "Gmail লগইন এখনো চালু হয়নি। অ্যাডমিনকে জানান।" (L651).

### 2.2 Customer self-signup, `csignupScreen()` L544-567 (gated by server flag)
- **Gate**: the entry button shows only when rpc `cust_signup_open` returns true. The admin toggles it under Admin → স্টোরেজ → "কাস্টমারের নিজে নিবন্ধন" (L819-821). The server can also return `signup_closed` or `sms_not_configured`.
- Title "কাস্টমার অ্যাকাউন্ট খুলুন". Back link "← লগইনে ফিরে যান".
- **Step 1** ("ধাপ ১/২: নাম ও মোবাইল নম্বর")
  - Fields "আপনার নাম" (placeholder "যেমন: করিম উদ্দিন") and "মোবাইল নম্বর" (01XXXXXXXXX).
  - Hint "এই নম্বরই হবে আপনার ইউজারনেম (পরে বদলানো যায় না)। নম্বরে একটা ৬ অঙ্কের কোড যাবে।"
  - Button "কোড পাঠান" calls Edge Function `customer-signup {action:'send'}`.
  - **Bangladeshi numbers only** (`/^01[3-9]\d{8}$/`). Resend is throttled to once per 60 s on the client.
- **Step 2** ("ধাপ ২/২: কোড ও পাসওয়ার্ড")
  - Shows name · mobile with a "বদলান" link.
  - Fields "SMS-এ আসা কোড", "নতুন পাসওয়ার্ড" (min 8), "পাসওয়ার্ড আবার".
  - Button "অ্যাকাউন্ট খুলুন" calls `customer-signup {action:'register'}`, then auto-login and the toast "স্বাগতম! আপনার অ্যাকাউন্ট খোলা হয়েছে।"
  - Link "কোড আসেনি? আবার পাঠান".
  - The code expires after 10 minutes (ERR `otp_expired`).
- Footer note: "অ্যাকাউন্ট খোলার পর পছন্দের দোকান খুঁজে "অনুমতি দিন" চাপুন। দোকান রাজি হলে সেটাই আপনার দোকান হবে…"

### 2.3 Shop registration, `registerScreen()` L720-743 (mobile + SMS OTP)
- Back "← ফিরে যান". Title "দোকান রেজিস্ট্রেশন". Sub "রেজিস্ট্রেশনের পর অ্যাডমিন অনুমোদন দিলে দোকান চালু হবে।"
- Google button "Gmail দিয়ে রেজিস্ট্রেশন করুন", then the divider "অথবা মোবাইল নম্বর ও পাসওয়ার্ড দিয়ে".
- Section "দোকানের পরিচয়": "দোকানের নাম" (placeholder "যেমন: রহিম কম্পিউটার"), "ঠিকানা" ("গ্রাম/মহল্লা, থানা, জেলা").
- Section "লগইন": "মোবাইল নম্বর" with hint "এই নম্বর দিয়েই লগইন করবেন। বাংলাদেশি নম্বরে একটা ৬ অঙ্কের কোড যাবে, সেটা দিয়ে যাচাই হবে।" Then "পাসওয়ার্ড" ("কমপক্ষে ৮ অক্ষর").
- Section "যাচাই": "ট্রেড লাইসেন্স (ছবি বা PDF)" is **required**. Hint "আসল দোকান যাচাইয়ের জন্য। শুধু অ্যাডমিন দেখবেন।"
- Button "কোড পাঠান ও রেজিস্ট্রেশন করুন":
  - BD number: Edge Function `shop-auth {action:'send_register'}` sends an SMS OTP. Step 2 is "মোবাইল নম্বর যাচাই" with field "SMS-এ আসা কোড", button "রেজিস্ট্রেশন শেষ করুন", resend "কোড আসেনি? আবার পাঠান" (60 s throttle) and "← তথ্য বদলান". `shop-auth {action:'register'}` then signs in and runs rpc `register_shop`.
  - Foreign number: no OTP. A plain `sb.auth.signUp`, then `register_shop` (L245-248).
  - After registration the license is uploaded to bucket `shop-docs`, and the user lands on the **gate** screen. The shop is pending unless the admin's auto-approve is on.
- OTP errors (L55-59): `otp_wait`, `otp_too_many` (daily per number), `otp_busy` (global daily cap), `otp_wrong`, `otp_expired`, `sms_failed`, `mobile_taken`, `not_bd`.

### 2.4 Google shop registration, `gRegisterScreen()` L705-719
- Brand title "আর একটু বাকি". Heading "দোকানের তথ্য দিন". Sub "আপনার Gmail যাচাই হয়ে গেছে। দোকানের নাম ও মোবাইল দিলেই নিবন্ধন শেষ।"
- Shows the Google account (name and **email**) with "✓ যাচাই করা".
- Fields:
  - "দোকানের নাম".
  - "মালিকের নাম" (prefilled from the Google name).
  - "ঠিকানা".
  - "মোবাইল নম্বর". Hint: "কাস্টমার ও অ্যাডমিন যোগাযোগের জন্য। পরে লগইন করবেন Gmail দিয়েই।"
  - "ট্রেড লাইসেন্স (ছবি বা PDF)" (required).
- Button "নিবন্ধন শেষ করুন" runs rpc `register_shop_google`. Link "অন্য Gmail দিয়ে ঢুকুন" logs out.

### 2.5 Set new password, `setPwScreen()` L584 (from the recovery email)
- "নতুন পাসওয়ার্ড সেট করুন" / "নতুন পাসওয়ার্ড". Text: "কমপক্ষে ৮ অক্ষর। অক্ষর ও সংখ্যা মিলিয়ে দিন, কাউকে বলবেন না।" Button "পাসওয়ার্ড সেট করুন".
- In practice this is reachable only by the admin, because only the admin has a forgot-password link.

---

## 3. Shop-owner panel (`shopScreen` L1470, tabs `shopTabsList` L1446)

Tab list (key, exact label, icon). Sidebar group headers: `dash`→"মূল", `store`→"ব্যবসা", `help`→"সহায়তা ও সেটিং". Mobile bottom-nav primaries: dash, cust, svc, store.

| key | Label | Who sees it |
|---|---|---|
| `dash` | "ড্যাশবোর্ড" (mobile: "হোম") | all |
| `cust` | "কাস্টমার" | all |
| `svc` | "সেবা" | all |
| `store` | "শপ" + "(n)" new product and service orders | all |
| `promo` | "প্রচার" | all |
| `tpl` | "টেমপ্লেট" | all |
| `rep` | "রিপোর্ট" | owner, manager |
| `plan` | "স্টোরেজ" | owner, manager |
| `help` | "সহায়তা" | all |
| `staff` | "স্টাফ" | **owner only** |
| `prof` | "প্রোফাইল" | owner, manager |
| `note` | "নোটিফিকেশন" + "(n)" unread (bell icon, top bar on mobile) | all |

Filter rule (L1451): owner sees everything; manager sees everything except `staff`; plain staff do not see `rep`, `plan`, `staff` or `prof`. The `pay` sub-tab under শপ is also owner/manager only (L1558).

### 3.1 ড্যাশবোর্ড (`dash`), `shopDash()` L1484 (the active definition; the older one at L869 is dead)
- `askCard`: "🔔 উত্তর দিন (n)". Owner and manager see pending cross-shop requests from customers and can answer "✓ রাজি" / "না".
- Hero:
  - "স্বাগতম", plus "(ম্যানেজার)" or "(স্টাফ)" for staff.
  - Shop name.
  - "দোকানের কোড: <code>".
  - Button "+ নতুন কাস্টমার" (goes to the cust tab).
- KPIs, each clickable: "নতুন অর্ডার", "কাস্টমার", "পণ্য", "আয় (টাকা)". Income counts only paid, non-cancelled product and service orders.
- `viewsCard` "আপনার প্রোফাইল কতজন দেখেছে" ("একজন দিনে একবার গোনা হয়"):
  - KPIs আজ / গত ৭ দিন / গত ৩০ দিন / মোট.
  - "গত ৩০ দিনে n জন কাস্টমার দেখেছে".
  - A bar chart. Its aria label says 14 days. Data: rpc `my_shop_stats`.
- "সাম্প্রতিক নোটিফিকেশন" (latest 5).
- `storageCard` "স্টোরেজ":
  - Used / limit and a progress bar.
  - "খালি আছে: X · nটি ফাইল".
  - At 80 % or more: a warning "স্টোরেজ প্রায় ভরে গেছে।" At 100 %: "স্টোরেজ ভরে গেছে, নতুন ফাইল রাখা যাবে না।"
  - Button "আরও স্টোরেজ কিনুন".
- `svcTiles` "ফটো ও আইডি সেবা". Tiles: "ফটো এডিট / পাসপোর্ট সাইজ", "এনআইডি / A4 প্রিন্ট", "প্রফেশনাল ফটো / পোশাক বদল".

### 3.2 কাস্টমার (`cust`), `custSection()` L1009
- **Welcome card** (after creating a customer or resetting a password; L991-1008).
  - Title "স্বাগত বার্তা পাঠান", or "নতুন পাসওয়ার্ড পাঠান" after a reset.
  - Shows name · **mobile**.
  - Shows the ready-made SMS text with the **plain-text username and password** (`pre.wtxt`).
  - Buttons:
    - "SMS পাঠান" opens an `sms:` link in the phone's own SMS app.
    - "WhatsApp-এ পাঠান" opens a wa.me link.
    - "কপি করুন".
    - "বন্ধ করুন".
  - Auto-SMS status line (`SMSR`, L267). One example: "✓ কাস্টমারের মোবাইলে SMS স্বয়ংক্রিয়ভাবে চলে গেছে।"
- **"নতুন কাস্টমার"** form:
  - Fields: "কাস্টমারের নাম"; "মোবাইল নম্বর" (country code + number).
  - Read-only "ইউজারনেম (মোবাইল নম্বরই, বদলানো যায় না)". The username is the mobile digits, checked live with rpc `username_available`. Statuses:
    - "✓ এই নম্বর দিয়ে নতুন কাস্টমার খোলা যাবে".
    - "✗ এই নম্বরে আগেই একজন কাস্টমার আছে। অন্য দোকানের হলে নিচে "অন্য দোকানের কাস্টমার" থেকে খুঁজে অনুমতি চান।"
  - "পাসওয়ার্ড (কমপক্ষে ৮)". This is a **plain text input, visible on screen**.
  - Optional checkbox "কাস্টমারের মোবাইলে অটো SMS পাঠান (আজ বাকি nটি)". It appears only when admin auto-SMS is on (rpc `sms_status`).
  - Button "কাস্টমার যোগ করুন" calls Edge Function `manage-customers {action:'create'}`.
- **`crossCard` "অন্য দোকানের কাস্টমার"** (L959). Cross-shop access with customer consent.
  - Search by username/mobile with button "খুঁজুন" (rpc `find_customer`).
  - The result shows name, @username and "<home shop>-এর কাস্টমার", plus one of:
    - status "আপনার নিজের কাস্টমার";
    - status "✓ যুক্ত আছে";
    - status "অনুরোধ অপেক্ষায়";
    - button "অনুমতি চান" (rpc `request_customer_access`).
  - Section "কাস্টমারের অনুরোধ (n)": "রাজি" / "না" (rpc `respond_access`). Plain staff see "মালিক/ম্যানেজার উত্তর দেবেন".
  - Section "আপনার পাঠানো অনুরোধ": "তুলে নিন" (rpc `revoke_access`).
- **"কাস্টমার তালিকা (n)"**: avatar, name, @username, the tag "অন্য দোকানের" for linked customers, and button "খুলুন". This opens the customer folder.

### 3.3 Customer folder (shop side), `customerFolder()` L1523
- Back "← সব কাস্টমার". Header shows avatar, name, "ইউজারনেম: @…" and **mobile**.
- For another shop's customer: a note explaining that only file actions are allowed.
- Home customers only:
  - Toggle "কাজ সম্পন্ন হয়েছে বলে চিহ্নিত করুন" / "✓ কাজ সম্পন্ন (বাতিল করতে চাপুন)" (rpc `set_customer_done`). Marking it done lets the customer leave a shop review.
  - "কাস্টমারের প্রোফাইল" with "সম্পাদনা" (`custEditForm` L1511):
    - "প্রোফাইল ছবি" upload, resized to 512 px into bucket `avatars`.
    - Fields নাম, পদবি, পেশা বা কাজ, মোবাইল নম্বর, ঠিকানা.
- "এই কাস্টমার রিপোর্ট করুন" (report box).
- **"ফাইল যোগ করুন"**:
  - "ফাইল আপলোড (JPG, PNG, WebP বা PDF — প্রতিটি সর্বোচ্চ ২৫ এমবি)", multiple files allowed.
  - "ডকুমেন্ট স্ক্যান (মোবাইলের ক্যামেরা)". This is `<input capture=environment>`. It **only uploads the camera photo, renamed `scan-YYYYMMDDHHMM.jpg`. No deskew, crop or PDF conversion here.** Deskew exists only in the NID tool.
  - Button "আপলোড করুন".
  - Upload flow: rpc `request_upload` → storage `customer-files` → rpc `finalize_upload`. On failure, `cancel_upload` (L289-304).
- **"ফাইল (n)"** list:
  - File-type badge, name, size, and the tag "অসমাপ্ত" if pending.
  - "ডাউনলোড" (60-second signed URL).
  - "মুছুন" (two-tap confirm, "নিশ্চিত করুন") for files this shop uploaded; otherwise "অন্য দোকানের দেওয়া".
- **"পাসওয়ার্ড রিসেট"** (home customers only):
  - "নতুন পাসওয়ার্ড (কমপক্ষে ৮)" is a plain text input.
  - Optional auto-SMS checkbox (only if the customer has a mobile).
  - Button "রিসেট করুন" calls `manage-customers {action:'reset'}` and then shows the welcome card with the new password.

### 3.4 সেবা (`svc`), `svcView()` L1982
Segmented control: "ফটো এডিট" | "এনআইডি A4" | "প্রফেশনাল ফটো".

**A. ফটো এডিট, `photoTool()` L1924**: a passport/stamp photo maker. Everything runs in the browser except the AI edit.
- Empty state: "ছবি দিন ও মাপ বেছে নিন। ক্রপ ও ছাপার শিট অটো হবে।"
- "মাপ" presets (L1738): "পাসপোর্ট ৩৫×৪৫ মিমি", "পাসপোর্ট ৪৫×৫৫ মিমি", "স্ট্যাম্প ২৫×৩০ মিমি", and "কাস্টম মাপ (mm / cm / inch / px)".
  - Custom units: মিমি/সেমি/ইঞ্চি/পিক্সেল.
  - DPI: ৩০০ (প্রিন্ট), ৬০০, ২০০, ১৫০, ৭২ (অনলাইন).
  - Allowed range 5–297 mm.
  - A live info line shows px × px · mm × mm · DPI.
- "ঘোরান": "⟲ বামে ৯০°" / "⟳ ডানে ৯০°". Slider "সামান্য বাঁকা হলে সোজা করুন (ডিগ্রি)", −15 to +15.
- **Background replacement** ("ব্যাকগ্রাউন্ড"): "আসল ব্যাকগ্রাউন্ড", "সাদা", "হালকা নীল", "হালকা ধূসর", "স্বচ্ছ (PNG)". Two methods:
  - "স্মার্ট — মানুষ চিনে আলাদা করে (প্রস্তাবিত)": Google **MediaPipe selfie segmenter**, loaded from jsDelivr and storage.googleapis.com and run in the browser (L1811-1845).
    - Option "আরও নিখুঁত চুলের কিনারা (বড় মডেল, প্রথমবার ~১৬ এমবি নামবে)".
    - Slider "কিনারা…" 20–80.
    - Status "মডেল প্রস্তুত হচ্ছে…" or "✓ মানুষ আলাদা করা হয়েছে…".
    - Hint "বিনামূল্যে, আপনার ব্রাউজারেই চলে, ছবি কোথাও পাঠানো হয় না।"
    - Falls back to the colour method if the model fails, with the toast "স্মার্ট মডেল লোড হয়নি…".
  - "সাধারণ — একরঙা দেয়ালের ছবির জন্য": a flood-fill from the edges, with tolerance slider 10–80 (`cutBg` L1793).
- **AI edit box** (`aiEditBox` L1887), titled "AI দিয়ে লিখে এডিট" with a "ক্রেডিট: n" tag.
  - Quick chips (L1885): "ব্যাকগ্রাউন্ড সাদা করো", "কালো কোট, সাদা শার্ট ও টাই পরাও", "ছবি পরিষ্কার, উজ্জ্বল ও শার্প করো", "চুল পরিপাটি করো", "ব্যাকগ্রাউন্ড হালকা নীল করো".
  - Textarea of up to 500 characters.
  - Button "AI দিয়ে এডিট করুন (১ ক্রেডিট)". While busy it reads "AI এডিট করছে… (১০–৩০ সেকেন্ড)".
  - Edge Function `ai-assist {action:'image_edit'}`. The image is downscaled to 1280 px JPEG. Backend is Google Gemini (see GEMINI_API_KEY, L2196).
  - Undo "↶ আগের ছবিতে ফিরুন". With zero credits, the button "ক্রেডিট কিনুন" also appears.
  - Warning: "পাসপোর্ট বা সরকারি কাজে AI দিয়ে বদলানো ছবি দেবেন না।"
- Sliders: "জুম (%)" 100–250, "ডানে-বামে", "উপরে-নিচে", "উজ্জ্বলতা (%)" 70–140, "কনট্রাস্ট (%)" 70–140.
- "A4 শিটে কপি": 4/6/8/12/16/20.
- Outputs:
  - "ছবি (JPG)" or "ছবি (PNG)".
  - "A4 শিট (PDF)". The PDF is built by a hand-written encoder (L1739).
  - "A4 শিট (JPG)".
- Save to customer: picker "কাস্টমারের ফোল্ডারে রাখতে চাইলে বেছে নিন" and button "A4 শিট (PDF) কাস্টমারের ফোল্ডারে রাখুন". This uploads into that customer's files and uses storage.

**B. এনআইডি A4, `nidTool()` L1963**: prints a national ID card front and back on A4.
- Title "এনআইডি কার্ড (A4 প্রিন্ট)". Text: "সামনে ও পেছনের ছবি দিন। কার্ড বাঁকা থাকলে অটো সোজা হবে, তারপর A4 কাগজের মাঝখানে আসল মাপে (৮৫.৬×৫৪ মিমি) বসবে।"
- Uploads "সামনের পাশ" and "পেছনের পাশ".
  - **Automatic deskew**: a projection-profile skew detector over ±20°.
  - Slider "কোণ ঠিক করুন (ডিগ্রি)" and button "অটো সোজা".
- Checkbox "কিনারা অটো ছাঁটুন (ছবিতে টেবিল দেখা গেলে)" (auto-trims the background).
- Outputs "A4 (PDF)" and "A4 (JPG)", and "A4 (PDF) কাস্টমারের ফোল্ডারে রাখুন".
- Privacy hint: "এনআইডির তথ্য সংবেদনশীল…"

**C. প্রফেশনাল ফটো, `proTool()` L1977**: not a separate tool.
- Text "ছবিতে AI দিয়ে কোট-টাই বা ফর্মাল পোশাক পরানো যায়। প্রতি ছবিতে ১ AI ক্রেডিট লাগে।"
- The single button "ফটো এডিটে গিয়ে AI দিয়ে করুন" switches to ফটো এডিট and prefills the AI prompt with "কালো কোট, সাদা শার্ট ও টাই পরাও, মুখ একই রাখো".

### 3.5 শপ (`store`), `storeView()` L1556
Sub-tabs: "পণ্য", "পণ্যের অর্ডার (n)", "সেবার অর্ডার (n)", and "পেমেন্ট" (owner/manager only).
- **পণ্য** (`prodSection` L1040):
  - Form "নতুন পণ্য": "পণ্যের নাম" (80), "দাম (টাকা)", "স্টক (সংখ্যা)", "বিবরণ" (400), "অতিরিক্ত তথ্য (ব্র্যান্ড, মাপ, ওয়ারেন্টি)" (160), "ছবি (ঐচ্ছিক, ২ এমবির মধ্যে)" (JPG/PNG/WebP). Button "পণ্য যোগ করুন".
  - Max 200 products (ERR `too_many_products`).
  - List "আমার পণ্য (n)": inline দাম/স্টক with "আপডেট" and "মুছুন". The tag "অ্যাডমিন লুকিয়েছে" appears if admin hid the product.
- **পণ্যের অর্ডার** (`ordSection` L1056):
  - Each row shows title × qty, status (নতুন/প্রক্রিয়াধীন/সম্পন্ন/বাতিল), "পরিশোধিত", customer name, total, payment method and txn ID.
  - Buttons "প্রক্রিয়ায়", "সম্পন্ন", "নগদ পেয়েছি"/"টাকা পেয়েছি" (rpc `confirm_payment`) and "বাতিল". rpc `update_order`.
- **সেবার অর্ডার** (`sordSection` L1563):
  - The shop sets "মূল্য (টাকা)" and "অবস্থা" (নতুন/চলছে/সম্পন্ন/বাতিল), then "আপডেট" (rpc `shop_update_service_order`).
  - "টাকা পেয়েছি" / "নগদ পেয়েছি" calls rpc `confirm_service_payment`.
- **পেমেন্ট** (`paySection` L1071), "পেমেন্ট নেওয়ার ব্যবস্থা":
  - Checkbox "ক্যাশ অন ডেলিভারি / দোকানে নগদ".
  - বিকাশ, নগদ and রকেট numbers, each with an account type (পার্সোনাল/এজেন্ট/মার্চেন্ট).
  - "ব্যাংক অ্যাকাউন্ট (ঐচ্ছিক: ব্যাংক, শাখা, নাম, নম্বর)".
  - Saved to table `payment_settings`. Note: "কাস্টমার সরাসরি আপনার নম্বরে টাকা পাঠাবে, অ্যাপ টাকা ধরে না।"

### 3.6 প্রচার (`promo`), `promoView()` L1579: ads with AI copywriting
- "নতুন প্রচার": "অ্যাডমিনের অনুমোদনের পর আপনার প্রচার কাস্টমারদের হোম পেজে "স্পনসর্ড" হিসেবে দেখা যাবে।"
- AI box "AI সহকারী (ঐচ্ছিক): কী নিয়ে বিজ্ঞাপন?" with button "AI দিয়ে লিখুন" (`ai-assist {action:'ad_text'}`, Gemini). It fills in the title and body.
- Fields "শিরোনাম" (60), "বিস্তারিত" (140), "ছবি (ঐচ্ছিক)". Button "প্রচার শুরু করুন" (rpc `create_ad`). Max 5 ads (`too_many_ads`).
- "আমার প্রচার (n)" with statuses "অনুমোদনের অপেক্ষায়" / "চালু" / "বাতিল" / "অ্যাডমিন বন্ধ রেখেছেন", plus the reason. "বন্ধ করুন" deletes the ad (rpc `delete_ad`).

### 3.7 টেমপ্লেট (`tpl`), `tplView()` L1664
- **"রেডিমেড ফাইল টেমপ্লেট"**: a library of files the admin uploaded.
  - Categories (L1607): CV / বায়োডাটা, বিজনেস কার্ড, জমি বিক্রয় দলিল, বন্ধকনামা, আবেদনপত্র, অঙ্গীকারনামা, চুক্তিপত্র, ব্যানার / পোস্টার, অন্যান্য.
  - Search "খুঁজুন: CV, দলিল, কার্ড…" and category chips.
  - Each row has "দেখুন" (PDF/images only) and "ডাউনলোড", with a usage counter (rpc `template_used`).
  - Empty state: "অ্যাডমিন এখনো কোনো টেমপ্লেট দেননি।"
- **"ডিজাইন টেমপ্লেট"**: a very simple SVG generator.
  - Types: ভিজিটিং কার্ড 540×300, পোস্টার 420×594, ব্যানার 800×300.
  - Fields শিরোনাম, উপশিরোনাম, মোবাইল নম্বর, রং.
  - Button "SVG ডাউনলোড করুন". Defaults: "আপনার দোকানের নাম", "ফটোকপি · প্রিন্ট · অনলাইন ফর্ম", "01XXXXXXXXX".

### 3.8 রিপোর্ট (`rep`), `reportView()` L1675 (owner/manager)
- KPIs "মোট অর্ডার", "সম্পন্ন অর্ডার", "আয় (টাকা)".
- "মাসিক হিসাব" (per month: count and taka).
- "কোন সেবা বা পণ্য বেশি চলছে" (top 10 with bars).
- Hint: income counts only paid orders. Computed on the client.

### 3.9 স্টোরেজ (`plan`), `planSection()` L787 (owner/manager)
- `storageCard`, as on the dashboard.
- **"আরও স্টোরেজ কিনুন"**:
  - Plan tiles "+X GB · N টাকা", **read from DB table `storage_plans` (id, mb, price). No prices are hard-coded.**
  - After choosing a plan: "N টাকা এই নম্বরের যেকোনোটিতে পাঠান:" plus the **admin's bKash/Nagad numbers** (from `platform_settings`).
  - Fields "কোন মাধ্যমে পাঠিয়েছেন" and "ট্রানজেকশন আইডি". Button "কেনার অনুরোধ পাঠান" (rpc `request_storage`).
  - Manual approval by admin.
  - With no plans: "এখনো কোনো প্ল্যান নেই।" With no admin numbers: "অ্যাডমিন এখনো পেমেন্টের নম্বর দেননি। একটু পরে চেষ্টা করুন।"
- **"AI ক্রেডিট"** card (`aiBuyCard` L771):
  - Tag "বাকি: n".
  - Text: "ফটো এডিটে লিখে নির্দেশ দিয়ে AI এডিট করতে প্রতি ছবিতে ১ ক্রেডিট লাগে। এডিট ব্যর্থ হলে ক্রেডিট ফেরত আসে। ঘোরানো, মাপ, ব্যাকগ্রাউন্ড বদল বিনামূল্যে।"
  - Plans "nটি এডিট · N টাকা" from **DB table `ai_plans`**.
  - Same bKash/Nagad + txn flow. Button "AI ক্রেডিট কেনার অনুরোধ পাঠান" (rpc `request_ai_credits`).
  - History "আমার AI ক্রেডিট কেনা".
- **"আমার কেনাকাটা (n)"**: storage request history with status যাচাইয়ের অপেক্ষায়/অনুমোদিত/বাতিল, method, txn ID and date.

### 3.10 সহায়তা (`help`), `shopHelp()` L1705
- **"AI সহকারী"**: a placeholder card only. "AI সহকারী চালু করতে একটি AI সার্ভিসের API চাবি লাগবে… চাবি পেলে আমরা এটি নিরাপদভাবে (সার্ভারের মাধ্যমে) যুক্ত করব।" **Not live.**
- **"ভার্চুয়াল অ্যাসিস্ট্যান্ট (আমাদের টিম)"**: "যে কাজ নিজে করা কঠিন, আমাদের টিমকে দিয়ে করিয়ে নিন।"
  - "কাজের ধরন" options: ডিজাইন করানো / অনলাইন ফর্ম পূরণ / ডকুমেন্ট টাইপ বা এডিট / ফেসবুক পেজ বা সোশ্যাল সেটআপ / অন্যান্য.
  - "বিস্তারিত", then "অনুরোধ পাঠান" (rpc `create_assist`).
  - List "আমার অনুরোধ (n)" with status গ্রহণের অপেক্ষায়/চলছে/সম্পন্ন and the admin's note.
- **"সাহায্য"** FAQ (L1689-1693), 6 questions.
- **"মতামত পাঠান"**: textarea "আপনার মতামত বা সমস্যা", button "পাঠান" (rpc `send_feedback`).

### 3.11 স্টাফ (`staff`), `staffView()` L1719 (owner only)
- "নতুন স্টাফ": নাম, মোবাইল, "পাসওয়ার্ড (কমপক্ষে ৮)" (plain text input), "ভূমিকা" (স্টাফ / ম্যানেজার).
  - Hint: "স্টাফ "দোকানদার" লগইনে নিজের মোবাইল নম্বর ও পাসওয়ার্ড দিয়ে ঢুকবে…"
  - Button "স্টাফ যোগ করুন" (`manage-customers {action:'create_staff'}`). Max 10 staff (`too_many_staff`).
- "স্টাফ তালিকা (n)": name, role tag, **mobile**, and "সরান" (`remove_staff`).

### 3.12 প্রোফাইল (`prof`) (owner/manager), L1476
- **Public profile editor** (`shopProfileTab` L1379):
  - Cover banner "ব্যানার যোগ করুন"/"ব্যানার বদলান" (1800 px). Shop photo "ছবি যোগ করুন" (900 px). Both go to bucket `shop-public`.
  - Shop name, bio, "যোগদান: date".
  - Buttons "বিস্তারিত সম্পাদনা", "অন্যরা যেভাবে দেখবে" (preview), "ম্যাপ লোকেশন বসান".
  - **Per-field visibility toggle** "সবার জন্য" / "শুধু আমি". Defaults (L1266): mobile, email and WhatsApp are private; everything else is public.
  - Sections (L1263):
    - দোকানের তথ্য: সেবার ধরন, সেবাসমূহ, খোলার সময়, ঠিকানা, প্রতিষ্ঠার সাল.
    - মালিক: মালিকের নাম, পদবি.
    - শিক্ষা ও প্রশিক্ষণ.
    - লিংক: ওয়েবসাইট.
    - যোগাযোগ: মোবাইল, ইমেইল, ফেসবুক, হোয়াটসঅ্যাপ, ইনস্টাগ্রাম, টিকটক, ইউটিউব, লিংকডইন.
  - The edit form (L1358) also includes "পরিচিতি (সংক্ষেপে, ১৬০ অক্ষর)", "দোকানের নাম" and "ঠিকানা". Those three are owner only.
  - "কাজের নমুনা" gallery: "ফটো যোগ করুন" (multiple, max 30 photos per `too_many_photos`), delete ✕ with "নিশ্চিত?".
  - Read-only reviews block (average stars).
- **Map location** (`locCard` L1408), "📍 দোকানের ম্যাপ লোকেশন":
  - GPS button "দোকানে বসে লোকেশন নিন (GPS)".
  - Or paste a Google Maps link or "23.4607, 91.1809" with button "বসান".
  - Short links (goo.gl/maps.app) are rejected with instructions. A location outside Bangladesh asks for confirmation.
  - "ম্যাপে দেখুন" shows the **lat/lng coordinates and address** on screen.
- **Owner only**:
  - `loginCard` "লগইনের উপায় ও যাচাই" (L666):
    - Mobile number with status "✓ যাচাই হয়েছে" / "যাচাই হয়নি". "যাচাইয়ের কোড পাঠান" sends an SMS OTP; then "যাচাই করুন". A Gmail-only shop also sets a mobile password here.
    - Gmail row "Gmail যুক্ত করুন" (Supabase `linkIdentity`) or "✓ যুক্ত", showing the **Gmail address**.
  - `licenseCard` "ট্রেড লাইসেন্স": "✓ জমা দেওয়া হয়েছে" / "জমা দেওয়া হয়নি", "জমা দেওয়া লাইসেন্স দেখুন", and a replace upload.

### 3.13 নোটিফিকেশন (`note`), `noteSection()` L1106
- askCard, then the list (newest 50) with the tag "নতুন".
- Tapping a notification routes by regex on its text (L1086-1088). Shop routes:
  - অনুমতি/অনুরোধে → cust#xc
  - স্টোরেজ/AI ক্রেডিট → plan
  - বিজ্ঞাপন → promo
  - অর্ডার/পেমেন্ট/পণ্য → store
  - রিভিউ → prof
  - "অনুরোধ (" → help
- Opening the tab marks everything read (rpc `mark_notifications_read`).

---

## 4. Customer panel (`custScreen` L2091)

Tabs (L2093), in order:
1. "হোম" (`main`)
2. "আমার ফাইল" (`files`)
3. "আমার দোকান" (`shop`)
4. "অর্ডার" (`ord`)
5. "নোটিফিকেশন" (`note`)
6. "সাহায্য" (`help`)
7. "আমার প্রোফাইল" (`prof`)

- **Customer with no linked shop** (self-signup): "আমার দোকান" and "অর্ডার" are hidden. The bottom nav becomes হোম/ফাইল/সাহায্য/প্রোফাইল.

### 4.1 হোম (`main`), `custHome()` L2012
- askCard (shops asking for file access).
- If there is no shop, a card "আপনার দোকান বেছে নিন" with instructions or the list of shops awaiting a reply.
- Hero with avatar, "স্বাগতম" and name.
- If work is marked done and not yet reviewed: "আপনার কাজ সম্পন্ন হয়েছে।" with button "রিভিউ দিন".
- **"বিজ্ঞাপন"**: sponsored ads, each labelled "স্পনসর্ড" (rpc `list_ads`). Tapping one opens the shop or an https link.
- **"আমাদের সেবা"** tiles filter the shop list: অনলাইন ফর্ম পূরণ, প্রিন্ট ও ফটোকপি, ডিজাইন, ডকুমেন্ট স্ক্যান, ছবি তোলা. The "ফাইল সংরক্ষণ" tile opens আমার ফাইল.
- **"কাছের দোকান"**:
  - Button "আমার কাছের দোকান দেখুন" (browser geolocation). Shows the nearest 6 shops with distance (মিটার/কিমি) and a Google Maps directions button.
  - Hint: location is never stored.
- **"সব দোকান"**: search "দোকান বা সেবা খুঁজুন" (placeholder "যেমন: ফটোকপি"). Rows show name, the tag "আমার দোকান", address, ★rating and "দেখুন" (rpc `list_shops`).
- **Public shop view** (`publicShopView` L1430), opened from a list:
  - Card "এই দোকানে কাজ করাতে চান?" with button "এই দোকানকে অনুমতি দিন" (rpc `customer_request_shop`).
  - Cover, photo, bio, joined date, "যাওয়ার পথ (Google Maps)" and distance.
  - Public info rows, gallery and reviews.
  - Opening a public shop view counts a profile view (rpc `view_shop`).

### 4.2 আমার ফাইল (`files`)
- List of files with "ডাউনলোড" (60-second signed URL). Empty: "এখনো কোনো ফাইল নেই। দোকানদার আপলোড করলে এখানে দেখা যাবে।"
- Hint: "ফাইল আপলোড ও মোছার কাজ দোকানদার করেন। আপনি দেখতে ও ডাউনলোড করতে পারবেন।" **Customers cannot upload.**

### 4.3 আমার দোকান (`shop`), `custShop()` L2082
- Home shop public profile.
- "পণ্য (n)" grid with price and stock.
- **Product detail** (`productDetail` L1125):
  - Back "← সব পণ্য". Price, "স্টক আছে: n" / "স্টক শেষ".
  - **"কিনুন"** form:
    - Fields "পরিমাণ" and "পেমেন্টের মাধ্যম". Options: ক্যাশ অন ডেলিভারি / বিকাশ / নগদ / রকেট / ব্যাংক ট্রান্সফার, each showing the **shop's account number**.
    - "ট্রানজেকশন আইডি" (6–40 alphanumeric) and "ঠিকানা বা নির্দেশ (ঐচ্ছিক)".
    - Button "কিনুন" (rpc `place_order`). Quantity 1–1000.
  - "রিভিউ (n)" list.
  - "আপনার রিভিউ": "তারা" (1–5 ★), "মতামত (ঐচ্ছিক)", button "রিভিউ দিন" (rpc `submit_review`; requires a completed order).
  - "এই পণ্য রিপোর্ট করুন".
- **Shop review** (`reviewsBlock`): when the shop has marked the customer done, the prompt "আপনার কাজ কেমন হলো?" appears with a 5-star picker and "রিভিউ জমা দিন" (rpc `submit_shop_review`).
- "এই দোকান রিপোর্ট করুন". Report reasons: ভুয়া বা প্রতারণা / খারাপ আচরণ / ভুল তথ্য / অন্য কারণ.

### 4.4 অর্ডার (`ord`), `custOrders()` L2041
- "নতুন সেবার অর্ডার": "সেবা" (5 services), "বিস্তারিত", button "অর্ডার করুন" (rpc `place_service_order`, home shop only). Message: "অর্ডার গেছে। দোকানদার মূল্য ঠিক করবেন।"
- "সেবার অর্ডার (n)":
  - Status and "মূল্য: … / দোকানদার ঠিক করবেন".
  - Once a price is set: পেমেন্টের মাধ্যম + ট্রানজেকশন আইডি, then "পেমেন্টের তথ্য দিন" (rpc `pay_service_order`).
- "পণ্যের অর্ডার (n)": status, total, method, "যাচাই চলছে".

### 4.5 নোটিফিকেশন: same component as the shop side
Customer routes: অনুমতি → prof#acc, অর্ডার/পেমেন্ট → ord, সম্পন্ন/রিভিউ → main, রিপোর্ট → help.

### 4.6 সাহায্য (`help`)
- The same placeholder "AI সহকারী" card (not live).
- FAQ (FAQC, L1694): 4 questions.
- "মতামত পাঠান".

### 4.7 আমার প্রোফাইল (`prof`), `custProfile()` L2067
- "এই তথ্য শুধু আপনি ও আপনার দোকানদার দেখতে পারেন।"
- "প্রোফাইল ছবি": only after linking to a shop. Otherwise: "দোকানের সাথে যুক্ত হলে ছবি দিতে পারবেন".
- Fields নাম, পদবি (placeholder "যেমন: শিক্ষক, ছাত্র, ব্যবসায়ী"), পেশা বা কাজ, মোবাইল নম্বর, ঠিকানা. Button "সংরক্ষণ করুন".
- **"লগইন"** card: "ইউজারনেম: @… (স্থায়ী, বদলানো যায় না)", "নতুন পাসওয়ার্ড (কমপক্ষে ৮ অক্ষর)", "আবার লিখুন", button "পাসওয়ার্ড বদলান".
- **Access permissions** (`accessCard` L977), "কোন দোকান আমার ফাইলে কাজ করতে পারে":
  - Incoming shop requests: "রাজি" / "না".
  - Own pending requests: "তুলে নিন".
  - Approved shops: "✓ অনুমতি আছে" with "বাতিল করুন" (two-tap).

---

## 5. Admin panel (brief), `adminScreen()` L2122

| Tab | Label | What it does |
|---|---|---|
| `ov` | ওভারভিউ | Live online count (shop/customer), recent activity, anonymous visitors (sources: Facebook ad, Google, WhatsApp…; device; 30-day chart), DAU/WAU/MAU table, per-shop regularity table, KPI tiles, recent reports. Refreshes every 15 s. |
| `ap` | দোকান অনুমোদন | **Auto-approve toggle** "নতুন দোকান স্বয়ংক্রিয় অনুমোদন" (rpc `admin_set_auto_approve`). Pending and rejected shops show mobile, verified tag, email, address, license link. Actions "অনুমোদন", "বাতিল" with reason. |
| `rp` | রিপোর্ট | Status নতুন/দেখছি/সমাধান/বাতিল, plus a note to the reporter. |
| `rq` | অনুরোধ | Virtual-assistant requests: status and a note to the shop. |
| `ad` | বিজ্ঞাপন | Admin creates ads (live immediately, with link and AI text). Approve, reject, pause, resume, edit, delete. Filter chips. |
| `fb` | মতামত | Feedback, toggle "দেখা হয়েছে". |
| `st` | স্টোরেজ | Admin bKash/Nagad receiving numbers. Storage plans (GB + price) add/delete. Purchase requests "টাকা পেয়েছি, অনুমোদন"/"বাতিল". **Auto SMS (BulkSMSBD)** on/off, daily per-shop limit (default 20, 0–1000), balance check, cost hint "নন-মাস্কিং SMS প্রায় ০.৩৫ টাকা". **Customer self-signup toggle**. AI credit plans (cost hint "$০.০৩৪ (≈ ৪ টাকা)" per image). Manual AI credit grants. AI credit requests. |
| `sh` | সব দোকান | All shops: suspend or re-enable; "স্টোরেজ যোগ করুন" (GB) per shop. |
| `prods` | পণ্য নিয়ন্ত্রণ | Hide or unhide any product. |
| `tm` | টেমপ্লেট লাইব্রেরি | Upload templates (20 MB max; pdf, doc(x), xls(x), ppt(x), jpg, png, webp, psd, cdr, ai, zip) to bucket `templates`. |
| `set` | অ্যাকাউন্ট সেটিং | Change password; change email. |

The overview states that the admin cannot see customer files.

---

## 6. Limits and numbers in code

- **Free storage**: **not in the client code.** No "1 GB" or default quota appears anywhere. Each shop's quota comes from `shops.storage_limit`, a DB value whose default is server-side. Admin can add GB per shop.
- **Storage plan prices**: **not hard-coded.** They come from DB table `storage_plans` (mb, price), which the admin creates with input in GB (placeholder examples "যেমন 1 বা 0.5" and price "যেমন 90"; placeholders only).
- **AI credit plan prices**: from DB table `ai_plans`. Placeholder examples "যেমন 10" edits and "যেমন 80" taka.
- **Customer files**: JPG, PNG, WebP or PDF only, **25 MB per file** (L12-13, L53). Upload is rejected when storage is full.
- **Product image**: JPG/PNG/WebP, **2 MB** (L323).
- **Trade license**: JPG/PNG/WebP/PDF. A PDF may be up to **5 MB**. Images are re-encoded to JPEG at 2200 px max and must then be 5 MB or less (L609-627).
- **Public shop images** are re-encoded to JPEG: profile 900 px, cover 1800 px, gallery 1400 px, ads 1200 px. Customer avatar 512 px. Any image is first loaded at 2400 px max.
- **Admin template**: **20 MB**, with the extension list above.
- **Count limits**: products 200; ads 5 at once; gallery photos 30; staff 10. Product order quantity 1–1000.
- **Username**: 3–30 characters; lowercase a-z, 0-9, `.` and `_`; must start and end alphanumeric; no `..`. Reserved: admin, support, help, digitalstudio, digital.studio, official, system, root (L102-103). In practice **a customer's username is their mobile number** (digits, no `+`), which is permanent.
- **Password**: minimum 8 characters, maximum 72 (input maxlength). No complexity rule is enforced.
- **Mobile**: BD numbers are normalised to `01XXXXXXXXX`. Other countries become `+<cc><digits>`, 7–15 digits. 20 country codes. SMS OTP works only for BD `01[3-9]XXXXXXXX`.
- **OTP**: 6 digits, valid 10 minutes, resend after 1 minute. There are per-number daily and global daily caps (server side).
- **Login**: server-side lockout after too many wrong passwords per day (`login_locked`). Generic error messages.
- **Transaction ID**: 6–40 characters, English letters and digits.
- **Auto-SMS**: daily cap per shop set by admin (default 20).
- **Session**: 30-minute idle logout for shop and admin.
- **Signed URLs**: file download 60 s; template 120 s; license 600 s (owner) or 3600 s (admin); images 3600 s.
- **Photo tool**: zoom 100–250 %, brightness and contrast 70–140 %, straighten ±15°, copies per A4 4/6/8/12/16/20, custom size 5–297 mm, DPI 72/150/200/300/600. NID tool: deskew ±20°, card size 85.6 × 54 mm.
- **AI edit**: 1 credit per image, refunded on failure. Admin cost note: about $0.034 (≈ ৳4) per image.
- **Ad text**: title 60, body 140 characters. Bio 160. Product description 400.

---

## 7. Gated, unfinished or approval-dependent features

| Feature | Gate / status |
|---|---|
| Shop goes live | **Admin approval** (gate screen). Auto-approve can switch this off. |
| Customer self-signup | **Off unless** admin turns on "কাস্টমারের নিজে নিবন্ধন" (`cust_signup_open`). Also needs BulkSMSBD configured. BD numbers only. |
| Shop SMS OTP registration and mobile verification | Needs SMS configured. Error text "SMS এখনো চালু হয়নি…" exists. |
| Auto SMS to customers | Admin toggle plus daily cap. Otherwise the shop sends manually from its own phone, WhatsApp or copy. |
| Gmail login and Gmail linking | Depends on the Supabase Google provider and manual-linking settings. Error texts "Gmail লগইন এখনো চালু হয়নি" and "Gmail যুক্ত করা এখনো চালু হয়নি". |
| **AI photo edit** | Needs purchased credits (admin-approved manual payment). Error `ai_billing` reads "AI ছবি এডিট এখনো চালু হয়নি (Google বিলিং বাকি)", which suggests it **may not be live** (unverified). |
| AI ad copy | Needs `GEMINI_API_KEY`. Error "AI এখনো চালু হয়নি…". |
| **"AI সহকারী"** card (shop and customer help) | **Placeholder text only, not implemented.** |
| Storage purchase / AI credits | Manual: pay the admin's bKash/Nagad, enter the txn ID, admin verifies. Shows "এখনো কোনো প্ল্যান নেই।" if the admin has created no plans. |
| Shop ads (প্রচার) | Admin approval. Admin ads go live immediately. |
| Product and shop reviews | Product: only after a completed order. Shop: only after the shop marks the customer "done" or a service order is done. |
| Cross-shop file access | Needs customer consent (and shop owner/manager consent). |
| Templates library | Empty until the admin uploads files. |
| Customer profile photo | Only once linked to a shop. |

---

## 8. Privacy-sensitive on-screen data, by screen (for blurring)

- **Login**: typed mobile number, username (= mobile) and password. The password becomes visible if "দেখুন" is pressed.
- **Customer signup**: name, mobile, OTP code, passwords.
- **Shop register / Google register**: shop name, address, mobile, password, license file name; on Google register also the **Google name and email**.
- **Gate**: reject reason; owner's verified mobile and Gmail (loginCard).
- **Shop dashboard**: shop name, **shop code**.
- **কাস্টমার tab**:
  - New-customer form: name, mobile, username, **password as plain text**.
  - **Welcome card**: name, mobile and the full SMS text with **username and password in clear text**.
  - Customer list: names, @usernames (= mobile numbers), avatars.
  - Cross-shop search: names, @username, home shop name.
- **Customer folder**: name, @username, **mobile**, avatar, designation, occupation, **address**, **file names** (often personal, e.g. NID scans), plain-text reset password plus the welcome card.
- **Services**:
  - Photo tool: the customer's face photo; customer names in the picker.
  - **NID tool: front and back NID images (name, NID number, date of birth, address, photo).** Blur fully.
- **শপ**: product orders (customer names, txn IDs, notes/addresses); service orders (customer names, details, txn IDs); **পেমেন্ট sub-tab: bKash/Nagad/Rocket numbers and bank account details**.
- **স্টোরেজ**: the **admin's bKash/Nagad receiving numbers**, and the shop's own transaction IDs in history.
- **স্টাফ**: staff names and **mobile numbers**, plain-text password field.
- **প্রোফাইল**:
  - Mobile, email, WhatsApp, social links, owner name, address.
  - **GPS coordinates**.
  - Login card: **mobile and Gmail address**.
  - Trade license link/file.
- **Notifications**: may contain customer and shop names.
- **Customer home / shop view**: shop names, addresses, distances, public phone/email if a shop made them public, ad content.
- **Customer অর্ডার / product detail**: the **shop's payment numbers** (bKash etc. with account type), the customer's txn IDs.
- **Customer profile**: name, mobile, address, designation, occupation, avatar, @username.
- **Admin** (not for video): shop mobiles, emails, licenses, txn IDs, admin login email at the top of the overview ("লগইন: <email>"), visitor IDs.

---

## 9. Possible bugs and oddities (from code reading, unverified)

1. **Duplicate `shopDash()`** (L869 and L1484). The later one wins, so L869-877 is dead code. It also references a non-existent tab key `'ord'`.
2. **Duplicate ERR key `mobile_taken`**: defined at L58 and L65, then overridden at L1174 with a different text ("এই মোবাইল নম্বর আগেই ব্যবহার হয়েছে"). The earlier shop-specific messages are never shown.
3. **The customer FAQ contradicts self-signup.**
   - FAQC (L1694) says "নিজে অ্যাকাউন্ট খোলা যায় না।" even though self-signup exists when the flag is on.
   - FAQS (L1690) says customers are added with "নাম, ইউজারনেম ও পাসওয়ার্ড", but the username is now forced to be the mobile number.
4. **Plain staff hit dead buttons.**
   - Dashboard "আরও স্টোরেজ কিনুন" (L766) and AI box "ক্রেডিট কিনুন" (L1910) call `shopPick('plan')`.
   - `plan` is not in a plain staff member's tab list, so `shopScreen` silently falls back to the dashboard.
5. **Shop owners and staff have no in-app password change and no forgot-password.**
   - Only admin has "পাসওয়ার্ড ভুলে গেছেন?" (L512), and only admin gets `accountCard` (L2176).
   - Customers can change their password but have no self-service reset; the FAQ tells them to ask the shop.
6. **"ডকুমেন্ট স্ক্যান" in the customer folder is only a camera upload** (L1524-1528). No deskew, crop or enhancement. Deskew exists only in the NID tool. Marketing that says "scan with deskew" would be accurate only for NID.
7. **Developer-facing messages can reach users:**
   - "সেটআপ বাকি: Supabase-এ "Confirm email" বন্ধ করুন (README দেখুন)" (L247, foreign-number shop signup).
   - "AI এখনো চালু হয়নি: Supabase-এ GEMINI_API_KEY বসাতে হবে।" (L2196, shown to shops in the প্রচার AI box).
   - "AI চাবির প্রজেক্টে টাকা শেষ: বিনামূল্যের প্রজেক্টের নতুন চাবি দিন।"
8. **Social link icons** load from relative `icons/*.png` (L1286-1289: phone, gmail, facebook, whatsapp, instagram, tiktok, youtube). These files were not part of the download; if missing, broken-image icons appear on profiles.
9. `linkOf()` (L1281): the comment says only https, but `http://` links are also accepted.
10. **Unpinned dependency**: `@supabase/supabase-js@2` has no exact version (index.html; the HTML comment itself says to pin it). MediaPipe is pinned to 1.1.0, but its models use `latest` URLs.
11. `storageCard` divides by `storage_limit`. A null or 0 limit would show "null বাইট" or NaN and a full bar (L761-765). Edge case only.
12. Customer login with a foreign number typed with "+" fails, because usernames are stored without "+" and `doLogin` strips only "@" (L217).
13. Service-order payment row (L2047-2052): the txn ID field shows even when "ক্যাশ" is selected (it is ignored). The viewsCard chart label says "গত ১৪ দিনের" while the caption says 30 days (L930).
14. The admin storage card text says payment numbers are for storage, "দোকানদাররা স্টোরেজ কেনার টাকা এই নম্বরে পাঠাবে।" They are also used for AI credit purchases. Rocket is not offered for platform purchases (bKash/Nagad only).
15. The customer-profile "সংরক্ষণ করুন" button (L2076) has no busy/disabled state, so double-taps send duplicate updates. Harmless.
16. Product review form shows to every customer; eligibility is enforced only by the server error `not_eligible`.
