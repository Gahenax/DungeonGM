## 2024-06-25 - Accessible Dynamic RPG Feeds
**Learning:** In text-based RPG interfaces, dynamic game narrative feeds (such as chat containers) require `role="log"` and `aria-live="polite"` to ensure screen readers automatically announce new messages without interrupting the user.
**Action:** Always add `role="log"` and `aria-live="polite"` to containers that act as a dynamic message feed in RPG components. Ensure form inputs like `<select>` and `<input>` have explicit `aria-label` attributes if visible `<label>` elements are omitted to save space.
