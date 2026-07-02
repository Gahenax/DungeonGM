## 2024-07-02 - Accessible Accordion Headers
**Learning:** In text-based RPG interfaces like Cripta, accordion-style content blocks (like the Character Sheet) often rely on custom interactive `div` elements, violating a11y standards.
**Action:** When creating accordion headers, always use a semantic `<button>` combined with `aria-expanded` and an `id`-matched `aria-controls` for screen reader synchronization, then apply reset CSS (`background: none; border: none; font-family: inherit;`) with a `:focus-visible` state to maintain the visual layout while ensuring keyboard accessibility.
