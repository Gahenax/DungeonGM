## 2024-06-15 - Accessible Dynamic Chat Containers
**Learning:** Dynamic game narrative feeds (such as the D&D chat event log in `GameBoard.tsx`) are silently updated in the DOM, meaning screen reader users are completely unaware of new narrative events. Simply appending messages to a `div` is a major accessibility blocker for text-based RPGs.
**Action:** Always ensure dynamic narrative/chat containers utilize `role="log"` and `aria-live="polite"`. This tells screen readers to automatically announce new messages as they are added to the DOM without interrupting the user's current actions.
