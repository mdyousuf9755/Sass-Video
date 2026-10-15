# Digital Studio: tutorial video (16:9, about 4.5 minutes)

**Status: draft 1, for the owner's approval.** Every feature named below was
tested live on 2026-10-15 with the demo accounts (see
`../digital-studio-reel/test-report.md`, R-numbers in brackets). Nothing
untested or unlaunched is mentioned.

- **Format:** 1920×1080, 30 fps, Facebook + YouTube.
- **Voice:** professional Bangladeshi Bengali male, calm and clear, about
  2.2 words per second.
- **Music:** `music_bed_4min` (original, owner-approved) under the voice,
  ducked about 18 dB.
- **Screen:** real recordings of the demo shop "Yousuf Printing Shop" and
  "ডেমো কাস্টমার", inside a browser frame showing
  `digital-studio-bd.pages.dev`.
- **Privacy:**
  - Every real login number is covered and replaced by **01700-000000**.
  - Passwords are never shown.
  - Other shops, the sponsored ad of another shop and the ready-made CV
    template are never shown.

## Kept out on purpose

| Feature | Why |
|---|---|
| Mobile app | Does not exist; web only |
| 15 GB, AI সহকারী, ভার্চুয়াল অ্যাসিস্ট্যান্ট | Not launched (owner) |
| AI photo edit, AI ad text | Not tested; may not be live |
| bKash / Nagad / Rocket payment | **Saving fails for new shops (R17, D18).** Add back once the developer fix is confirmed |
| Gmail login, প্রচার (ads), nearby-shop distance | Not tested |
| Customer self sign-up | Off by default (admin switch) |
| The "English 2 page cv" template | A real person's CV |

## Script

Times are cumulative. "VO" is the voice-over; "Screen" is what is recorded;
"Text" is the on-screen title (Hind Siliguri, teal and gold).

### 0. Hook (0:00 to 0:12)
- **Screen:** quick montage: upload → customer download → photo sheet → the
  logo.
- **Text:** কাস্টমারের সব ফাইল, এক জায়গায়
- **VO:** কম্পিউটার বা প্রিন্টের দোকানে প্রতিদিন কাস্টমারের অনেক ফাইল
  জমে। পেনড্রাইভ হারায়, ফাইল খুঁজে পাওয়া যায় না। আজ দেখাবো এর সহজ
  সমাধান: ডিজিটাল স্টুডিও।

### 1. What it is (0:12 to 0:27)
- **Screen:** login page, the three role tabs.
- **Text:** শুধু ব্রাউজারে চলে · কোনো ইনস্টল লাগবে না
- **VO:** ডিজিটাল স্টুডিও একটি ওয়েব অ্যাপ। মোবাইল বা কম্পিউটারের
  ব্রাউজারে খুললেই চলে, কিছু ইনস্টল করতে হয় না। দোকানদার, কাস্টমার,
  দুজনেরই আলাদা লগইন আছে।

### 2. Register your shop (0:27 to 0:57) [R1–R6]
- **Screen:** দোকানদার → দোকান রেজিস্ট্রেশন করুন → shop name, address,
  mobile (shown as 01700-000000), password (dots only), trade licence
  (DEMO) → কোড পাঠান → code step → dashboard.
- **Text:** মোবাইল নম্বর দিয়ে রেজিস্ট্রেশন · SMS কোডে যাচাই
- **VO:** শুরু করতে "দোকানদার" অপশনে গিয়ে "দোকান রেজিস্ট্রেশন করুন"
  চাপুন। দোকানের নাম, ঠিকানা, মোবাইল নম্বর আর একটি পাসওয়ার্ড দিন।
  ট্রেড লাইসেন্সের ছবি দিন, এটা শুধু অ্যাডমিন দেখবেন। এরপর মোবাইলে
  একটি ছয় অঙ্কের কোড আসবে। কোডটি লিখলেই আপনার দোকান তৈরি।

### 3. Dashboard (0:57 to 1:17) [R6–R8]
- **Screen:** dashboard; zoom on counters, then the storage card
  "১.০০ জিবি".
- **Text:** টেস্ট ভার্সনে ১ জিবি ফ্রি
- **VO:** এটা আপনার ড্যাশবোর্ড। এখানে নতুন অর্ডার, কাস্টমার, পণ্য আর
  আয়ের হিসাব এক নজরে দেখবেন। টেস্ট ভার্সনে প্রতিটি দোকান পাচ্ছে এক
  জিবি ফ্রি স্টোরেজ।

### 4. Add a customer (1:17 to 1:42) [R9]
- **Screen:** কাস্টমার → name "ডেমো কাস্টমার", mobile (01700-000000),
  password (blurred) → কাস্টমার যোগ করুন → welcome card (password
  blurred) → SMS / WhatsApp / কপি buttons.
- **Text:** প্রতি কাস্টমারের আলাদা লগইন
- **VO:** এবার কাস্টমার যোগ করি। কাস্টমারের নাম, মোবাইল নম্বর আর একটি
  পাসওয়ার্ড দিন। মোবাইল নম্বরটাই হবে তার ইউজারনেম। "কাস্টমার যোগ
  করুন" চাপলেই লগইনের তথ্যসহ একটি স্বাগত বার্তা তৈরি হয়, যা SMS বা
  হোয়াটসঅ্যাপে পাঠাতে পারবেন।

### 5. Upload files (1:42 to 2:02) [R10–R11]
- **Screen:** customer folder → ফাইল আপলোড → demo-cv.pdf + demo-cv.jpg →
  আপলোড হয়েছে → file list.
- **Text:** JPG, PNG, PDF · প্রতিটি ২৫ এমবি পর্যন্ত
- **VO:** কাস্টমারের নাম চাপলে তার ফোল্ডার খুলবে। এখানে ছবি বা পিডিএফ
  ফাইল আপলোড করুন, একসাথে একাধিক ফাইলও দেওয়া যায়। ফাইল এখন
  নিরাপদে অনলাইনে রাখা থাকল, যেকোনো সময় ডাউনলোড করতে পারবেন।

### 6. The customer's side (2:02 to 2:25) [R12]
- **Screen:** a second browser: কাস্টমার tab → login (number shown as
  01700-000000, password dots) → আমার ফাইল → ডাউনলোড.
- **Text:** কাস্টমার নিজেই ফাইল দেখে ও ডাউনলোড করে
- **VO:** এবার কাস্টমারের দিক দেখি। কাস্টমার তার মোবাইল নম্বর আর
  পাসওয়ার্ড দিয়ে লগইন করে "আমার ফাইল"-এ সব ফাইল দেখতে পায়, আর নিজেই
  ডাউনলোড করে নিতে পারে। বারবার দোকানে এসে ফাইল চাইতে হয় না।

### 7. Job done → notification → review (2:25 to 2:47) [R13]
- **Screen:** shop: "কাজ সম্পন্ন হয়েছে বলে চিহ্নিত করুন" → customer:
  নোটিফিকেশন (১), banner "রিভিউ দিন" → 5 stars → রিভিউ জমা দিন →
  rating ৫.০.
- **Text:** কাজ শেষ হলে কাস্টমার জানতে পারে
- **VO:** কাজ শেষ হলে "কাজ সম্পন্ন" চিহ্নিত করুন। কাস্টমার সাথে সাথে
  নোটিফিকেশন পাবে, আর দোকানকে স্টার দিয়ে রিভিউ দিতে পারবে। ভালো রিভিউ
  মানে নতুন কাস্টমারের আস্থা।

### 8. Passport photo tool (2:47 to 3:17) [R14–R15]
- **Screen:** সেবা → ফটো এডিট → owner-supplied portrait → size 35×45 →
  background "হালকা নীল" → A4 sheet with 8 copies → download, then
  "কাস্টমারের ফোল্ডারে রাখুন".
- **Text:** পাসপোর্ট ছবি · ব্যাকগ্রাউন্ড বদল · A4 শিট
- **VO:** দোকানের প্রতিদিনের কাজ আরও সহজ করতে আছে ফটো টুল। ছবি দিন,
  মাপ বেছে নিন, যেমন পাসপোর্ট পঁয়ত্রিশ বাই পঁয়তাল্লিশ মিলিমিটার।
  ব্যাকগ্রাউন্ড সাদা বা হালকা নীল করে নিন। এক ক্লিকে A4 কাগজে আটটি
  কপি তৈরি, প্রিন্ট করুন বা সরাসরি কাস্টমারের ফোল্ডারে রেখে দিন।

### 9. NID A4 print (3:17 to 3:37) [R16]
- **Screen:** সেবা → এনআইডি A4 → the tilted **DEMO ID card** front and
  back → auto-straightened → A4 (PDF).
- **Text:** এনআইডির দুই পাশ, আসল মাপে A4-এ
- **VO:** এনআইডি প্রিন্টের জন্য কার্ডের সামনে আর পেছনের ছবি দিন। ছবি
  বাঁকা থাকলেও অটো সোজা হয়ে যায়, আর দুই পাশ আসল মাপে A4 কাগজে বসে
  যায়।

### 10. Products, orders, reports (3:37 to 4:07) [R18–R21]
- **Screen:** শপ → পণ্য → "ডেমো পেনড্রাইভ 16GB" → customer orders (cash)
  → shop: প্রক্রিয়ায় → নগদ পেয়েছি → সম্পন্ন → রিপোর্ট (৳৪৫০).
- **Text:** পণ্য বিক্রি · অর্ডার · আয়ের হিসাব
- **VO:** দোকানের পণ্যও এখানে বিক্রি করতে পারবেন। পণ্যের নাম, দাম আর
  ছবি দিন। কাস্টমার অর্ডার করলে আপনি অর্ডারের অবস্থা আপডেট করবেন, আর
  টাকা পেলে চিহ্নিত করবেন। রিপোর্টে মাসিক আয় আর কোন পণ্য বেশি চলছে,
  সব হিসাব তৈরি থাকে।

### 11. Service orders (4:07 to 4:19) [R22–R23]
- **Screen:** customer: অর্ডার → "প্রিন্ট ও ফটোকপি" → shop sets price ৳50,
  status "চলছে".
- **Text:** সেবার অর্ডার অনলাইনে
- **VO:** প্রিন্ট, ফটোকপি বা অনলাইন ফর্মের মতো সেবার অর্ডারও কাস্টমার
  অনলাইনে দিতে পারে। আপনি মূল্য ঠিক করে কাজের অবস্থা জানিয়ে দেবেন।

### 12. Staff (4:19 to 4:31) [R26–R27]
- **Screen:** স্টাফ → add "ডেমো স্টাফ" (number 01700-000000) → staff list.
- **Text:** স্টাফ ও ম্যানেজার অ্যাকাউন্ট
- **VO:** দোকানে কর্মচারী থাকলে তাদের জন্য আলাদা স্টাফ অ্যাকাউন্ট খুলে
  দিন। সাধারণ স্টাফ রিপোর্ট, স্টোরেজ আর দোকানের প্রোফাইল দেখতে পারবে না।

### 13. Call to action (4:31 to 4:50)
- **Screen:** end card: logo, offer badge, URL, "Developed by Yousuf
  Digital Center", address, Contact 01865453564.
- **Text:** টেস্ট ভার্সনে ১ জিবি ফ্রি – আজই রেজিস্টার করুন:
  digital-studio-bd.pages.dev | আপনার মতামত জানান
- **VO:** ডিজিটাল স্টুডিওর টেস্ট ভার্সনে এখন এক জিবি স্টোরেজ একদম ফ্রি।
  আজই রেজিস্টার করুন: ডিজিটাল স্টুডিও বিডি ডট পেজেস ডট ডেভ। ব্যবহার
  করে আপনার মতামত আমাদের জানান। আপনার মতামতেই ডিজিটাল স্টুডিও আরও ভালো
  হবে।

**About 590 words of VO ≈ 4 min 30 s of speech at 2.2 words/s; total 4:50
with pauses.**

## Note on item 12

The staff VO names only what is hidden from plain staff (the রিপোর্ট,
স্টোরেজ and প্রোফাইল tabs, R27). It does **not** say income is owner-only,
because plain staff still see the income number on the dashboard (D21).
