# ডেভেলপারের জন্য: নতুন দোকান পেমেন্ট সেটিং সেভ করতে পারছে না

## সমস্যা

- নতুন রেজিস্টার করা দোকান **শপ → পেমেন্ট → সংরক্ষণ করুন** চাপলে
  "কিছু একটা সমস্যা হয়েছে" দেখায়।
- সার্ভার থেকে উত্তর আসে `POST /rest/v1/payment_settings` → **HTTP 403**।
- শুধু "ক্যাশ" টিক দিয়ে, কোনো নম্বর ছাড়া সেভ করলেও একই ফল। তাই সমস্যা
  নম্বরে নয়।
- ফলে নতুন দোকানের কাস্টমার শুধু ক্যাশে পেমেন্ট করতে পারছে।
- টেস্ট করা হয়েছে 2026-10-15-এ, একটা ডেমো দোকানে (দোকানের কোড 6414)।

## কারণ (কোড দেখে যা বোঝা যাচ্ছে)

`app.js`-এর `savePay()` ফাংশন এই কল করে:

```js
sb.from('payment_settings').upsert(row, { onConflict: 'shop_id' })
```

PostgREST-এ upsert চালাতে টেবিলে **INSERT** আর **UPDATE** দুটো RLS
policy-ই লাগে। নতুন দোকানের জন্য টেবিলে এখনো কোনো লাইন নেই, তাই কাজটা
INSERT হিসেবে চলে, আর সেই INSERT-টাই RLS আটকে দিচ্ছে। সম্ভবত টেবিলে
INSERT-এর policy নেই, বা থাকলেও শর্ত মিলছে না। পুরনো দোকানের লাইন আগে
থেকে আছে বলে তাদের ক্ষেত্রে সমস্যা ধরা পড়েনি।

## যা করতে হবে

**১. আগে এখনকার policy-গুলো দেখুন** (Supabase → SQL Editor):

```sql
select policyname, cmd, roles, qual, with_check
from pg_policies
where schemaname = 'public' and tablename = 'payment_settings';
```

**২. INSERT (আর দরকার হলে UPDATE) policy যোগ করুন।** দোকানের মালিক যেন
শুধু নিজের দোকানের লাইন লিখতে পারে:

```sql
create policy "shop owner can insert own payment settings"
on public.payment_settings
for insert to authenticated
with check (
  exists (select 1 from public.shops s
          where s.id = payment_settings.shop_id and s.owner_id = auth.uid())
);

-- UPDATE policy আগে থেকে না থাকলে এটাও দিন:
create policy "shop owner can update own payment settings"
on public.payment_settings
for update to authenticated
using (
  exists (select 1 from public.shops s
          where s.id = payment_settings.shop_id and s.owner_id = auth.uid())
)
with check (
  exists (select 1 from public.shops s
          where s.id = payment_settings.shop_id and s.owner_id = auth.uid())
);
```

**৩. ম্যানেজারকেও অনুমতি দিতে চাইলে:** এখনকার UPDATE বা SELECT policy-তে
ম্যানেজারের জন্য যে শর্ত বা helper function আছে, সেটাই এখানে মিলিয়ে দিন।
আলাদা নিয়ম বানাবেন না।

**৪. টেস্ট করুন:** ডেমো দোকানে (কোড 6414) লগইন করে শপ → পেমেন্ট-এ
সংরক্ষণ চাপুন। "সংরক্ষণ হয়েছে" দেখাবে, আর পেজ রিলোড করলেও সেভ করা নম্বর
থেকে যাবে।

> **সাবধান:** অন্য দোকানের লাইনে কেউ যেন লিখতে না পারে, সেটা নিশ্চিত
> করুন। শর্তে `owner_id = auth.uid()` অবশ্যই থাকতে হবে।
