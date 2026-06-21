## 2024-10-24 - Accessibility for Text-Based RPG Interfaces
**Learning:** Dynamic game narrative feeds (like the `chat-container`) require `role="log"` and `aria-live="polite"` so screen readers automatically announce new game events. Additionally, to save space, visible form labels may be omitted in the action form, but explicit `aria-label`s must be provided on `select` and `input` elements.
**Action:** Ensure all dynamically updating feed containers use ARIA live regions and provide explicit labels to form controls that lack visible labels.
