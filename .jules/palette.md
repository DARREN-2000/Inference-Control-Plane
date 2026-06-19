## 2024-06-18 - Form Accessibility Enhancements
**Learning:** Using `<label>` wrappers around inputs can be less robust for screen readers compared to explicit `htmlFor` matching with `id`. Adding visual red asterisks to required fields without `aria-hidden="true"` causes screen readers to read "star" or "asterisk", distracting from the form element's meaning.
**Action:** Always prefer `htmlFor` -> `id` linking for form elements and use `aria-hidden="true"` on decorative visual indicators like required field asterisks to improve the screen reader experience.
