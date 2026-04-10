## Principles

**Cut padding, not meaning.** Remove words that add no information. "It should be noted that X" → "X". If two sentences say the same thing, keep the clearer one. Deduplicate rules that appear in multiple places. Shorter rewrites that require more parsing to understand are not improvements — fewer tokens must also mean less cognitive load.

**Measure tokens, not characters.** Rewrites that look shorter may tokenize the same or longer. Always compare before and after with a token counter.

**Short ≠ ambiguous.** Fewer tokens at the same precision. Ambiguity sources to avoid:

- Words that are both verb and noun ("test", "surface", "update") — make part of speech obvious from sentence structure.
- Dropping qualifiers that carry meaning. "Not delegatable. Not skippable." caused a regression by losing "even if user claims to have reviewed." Brevity that removes a necessary condition is a bug.
- Over-compressing enumerations. Agents may not infer a pattern from fewer examples.

**Merge, don't just trim.** Two related paragraphs often compress better as one than as two individually trimmed paragraphs.
