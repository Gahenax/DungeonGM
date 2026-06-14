## 2024-06-14 - [Accessibility] Dynamic Game Narrative Feeds
**Learning:** For accessibility in text-based RPG interfaces, dynamic game narrative feeds (such as chat containers) require `role="log"` and `aria-live="polite"` to ensure screen readers automatically announce new messages.
**Action:** Always apply these ARIA attributes to chat containers or live-updating feed regions.
