## 2024-06-16 - Prevent unnecessary string allocation for token estimation
**Learning:** Concatenating large strings (like `prompt` and `generated_text` which can be 20,000 and 8,000 characters) just to calculate the estimated token count incurs an expensive memory allocation and copy.
**Action:** Always prefer mathematical calculation of lengths when only the length is needed, rather than allocating a large concatenated string first. Additionally, `(len + 3) // 4` is ~25% faster than `math.ceil(len / 4)` and avoids floating point operations.
