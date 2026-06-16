## 2024-05-15 - [Screen Reader Support for Chat Feeds]
**Learning:** In text-based RPG interfaces, dynamic game narrative feeds (like `.chat-container`) require `role="log"` and `aria-live="polite"` so screen readers automatically announce new messages as they appear without interrupting the user. Also, form inputs like `select` and `input` need `aria-label` when visible `<label>` elements are omitted to save space.
**Action:** Always add `role="log"` and `aria-live="polite"` to append-only chat or narrative logs, and ensure inputs without visible text labels have `aria-label` attributes.
