## 2024-06-23 - [Accessible Dynamic Game Feeds]
**Learning:** In text-based RPG interfaces, dynamic game narrative feeds (such as chat containers) require `role="log"` and `aria-live="polite"` to ensure screen readers automatically announce new messages as they are appended to the DOM.
**Action:** Always verify that components continuously appending narrative text include these ARIA attributes to maintain a seamless accessible experience for non-visual users.
