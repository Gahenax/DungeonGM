## 2024-11-20 - Accessible Dynamic RPG Feeds
**Learning:** Text-based RPGs need `role="log"` and `aria-live="polite"` on dynamic game narrative feeds so screen readers automatically announce new narrator/player messages without manual focus shifts. Also, forms using icon-only or omitted visual labels to save space must include `aria-label` attributes to ensure they remain accessible to screen reader users.
**Action:** When creating new feed-like components or compact inputs (especially in GameBoard components), enforce `aria-live` tags and `aria-label` on inputs missing `<label>` tags.
