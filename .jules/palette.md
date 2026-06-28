## 2026-06-28 - Dynamic Game Feed Accessibility
**Learning:** In text-based RPG interfaces, the dynamic narrative feed needs `role="log"` and `aria-live="polite"` so screen readers automatically announce new game events without requiring focus shifts.
**Action:** Apply these ARIA attributes to any chat or event feed container representing ongoing background or sequential text updates.
