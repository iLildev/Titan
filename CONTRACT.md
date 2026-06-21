# Titan Framework Contract (v1)

هذا الملف يحدد السلوك الرسمي لمكتبة Titan.

أي تغيير في السلوك الظاهر للمطور يعتبر breaking change إلا إذا تم تحديث هذا الملف.

---

# 1. Public API

الاستيراد المسموح فقط:

from titan import Titan
from titan import InlineKeyboard
from titan import TitanError
from titan import TelegramError

---

# 2. Core Principle

- No hidden side effects
- Deterministic execution
- ctx هو نقطة التنفيذ الوحيدة

---

# 3. Context (ctx)

Allowed actions:
- reply()
- send()
- edit() (callback only)
- delete_message()
- ban_user()
- answer_callback()

Rules:
- لا وصول مباشر لـ Telegram API
- Message / Update / Chat / Sender = data-only

---

# 4. Event System

- message
- callback
- new_member
- left_member

Semantic events must not overlap with message handler.

---

# 5. Callback Routing

- @bot.callback(data) has priority
- fallback → @bot.on("callback")
- duplicate registration = TitanError

---

# 6. Long Polling

- exponential backoff:
  1s → 2s → 4s → 8s → 16s → 30s
- reset on success

---

# 7. Offset Handling

- external responsibility
- bot.run(offset=...)
- bot.offset available for persistence
- on_offset optional hook

---

# 8. Stability Rule

Any change is breaking if it:
- changes output for same input
- adds undocumented behavior
- changes execution order
