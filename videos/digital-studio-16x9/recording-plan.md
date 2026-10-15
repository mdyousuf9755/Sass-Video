# Recording plan (both 16:9 videos)

All footage is recorded by Claude in a headless browser (Playwright), not by
hand.

- **Accounts:** the demo accounts only (shop "Yousuf Printing Shop",
  "ডেমো কাস্টমার", "ডেমো স্টাফ").
- **Format:** 1920×1080 at 30 fps, browser zoom 100 %.
- **Cursor:** the mouse is moved slowly, so the editor can overlay a
  cursor, click ripples and zooms (video-editor `steps`).
- **No analytics noise:** the Facebook Pixel and visitor-count calls are
  blocked while recording.

## Clips

One clip per scene, named after the scene. "Blur / replace" lists what the
editor must hide. Real login numbers become **01700-000000**; passwords are
always blurred.

| Clip | Scene(s) | Account | Actions | Blur / replace |
|---|---|---|---|---|
| `login_roles` | 1 | none | Open the site; click কাস্টমার, দোকানদার, অ্যাডমিন | — |
| `register` | 2 | new throwaway? **No**: replay on the filled form only, without sending a code | Fill the form with the demo values (do **not** press "কোড পাঠান"); then cut to the code screen, re-staged with the screenshot from R4 | number → demo, password |
| `dashboard` | 3, promo 2 | shop | Dashboard, slow scroll to the storage card | shop code (optional) |
| `add_customer` | 4, promo 3 | shop | Fill the new-customer form with a **second** demo customer, or replay the welcome card | number → demo, password, welcome-card password |
| `upload` | 5, promo 3 | shop | Folder → choose files → আপলোড করুন | username/number line |
| `customer_files` | 6, promo 4 | customer | Login → আমার ফাইল → ডাউনলোড | number → demo, password |
| `done_review` | 7, promo 6 | shop + customer | Mark done (toggle off/on) → customer notification → review form | number line |
| `photo_tool` | 8, promo 5 | shop | Load portrait → size → background blue → copies 8 → A4 sheet download | — (portrait used with permission) |
| `nid_tool` | 9, promo 5 | shop | Load DEMO ID front/back → auto-straight → A4 | — (DEMO card only) |
| `orders` | 10, promo 6 | shop + customer | Product page → কিনুন (cash) → shop status buttons → রিপোর্ট | customer number line |
| `service_order` | 11 | customer + shop | New service order → price and status | — |
| `staff` | 12 | shop | Staff list (existing "ডেমো স্টাফ") and the form | staff number → demo, password |

## Notes

- **Repeatable states.** Re-recording some actions changes production data
  on the demo shop only (for example, another order or another review).
  Before re-recording, Claude lists any new demo rows it will create; it
  creates nothing on real accounts.
- **Registration is not repeated live.** It would need another unused
  number and SMS code. The registration clip is the filled form plus the
  code screen from the real test.
- **Home page.** The customer home shows other real shops and another
  shop's ad. Record the customer side starting at "আমার ফাইল", or crop the
  home page to the demo shop's card.
