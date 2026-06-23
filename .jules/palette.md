## 2024-06-18 - Form Accessibility Enhancements
**Learning:** Using `<label>` wrappers around inputs can be less robust for screen readers compared to explicit `htmlFor` matching with `id`. Adding visual red asterisks to required fields without `aria-hidden="true"` causes screen readers to read "star" or "asterisk", distracting from the form element's meaning.
**Action:** Always prefer `htmlFor` -> `id` linking for form elements and use `aria-hidden="true"` on decorative visual indicators like required field asterisks to improve the screen reader experience.

## 2024-08-16 - Form and Async Action Accessibility Enhancements
**Learning:** Buttons with dynamically changing inner text (e.g. "Generating..." / "Run Inference") do not need an `aria-label`, as screen readers will simply read the inner text. Using both is redundant and can cause double-reading. Additionally, dynamic content updates like API error messages or async results should be explicitly labeled with `role="alert"` or `aria-live="polite"` respectively, to ensure screen readers announce these updates.
**Action:** When creating buttons with dynamic inner text, avoid redundant `aria-label`s. Always use `aria-live` or `role="alert"` for important dynamic UI state changes, and hide purely decorative loading SVGs using `aria-hidden="true"`.

## 2026-06-23 - Native Form Disabling via Fieldset
**Learning:** Manually disabling individual form inputs and buttons during an async submission is tedious and can lead to missed fields. Wrapping the entire form contents in a `<fieldset disabled={isLoading}>` natively disables all descendant form controls at once. This correctly removes them from the tab order and provides proper semantic context to assistive technologies that the entire section is unavailable.
**Action:** For form accessibility and UX, prefer wrapping form inputs inside a `<fieldset disabled={isLoading}>` to natively disable the entire form during async requests instead of manually disabling individual inputs and buttons.
