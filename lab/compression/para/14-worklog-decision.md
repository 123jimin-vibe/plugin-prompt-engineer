### Decision

Immutable record of *why* a choice was made.

```toml
+++
id = "d0001"
title = "No recursion in macros"
relates_to = ["s0007"]
supersedes = []
+++
```

Body: context → choice → rationale → consequences. Do not edit substance — supersede with a new decision. Trivial fixes (typos, formatting) are the only acceptable edits. Decisions stay in active directory; archive only when superseded.

Create when: non-trivial choice, design flaw, requirement change, feature abandonment. For small projects, recording in the task body is acceptable.
