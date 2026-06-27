## 2024-10-18 - Improve screen reader experience for game board
**Learning:** Dynamic game narrative feeds (such as chat containers) require `role="log"` and `aria-live="polite"` to ensure screen readers automatically announce new messages. Also, form inputs like `<select>` and `<input>` must have explicit `aria-label` attributes if visible `<label>` elements are omitted to save space.
**Action:** Always add `role="log"` and `aria-live="polite"` to chat/narrative containers and ensure all form inputs have accessible labels, either visible or via `aria-label`.
