## File layout

- One `.md` = one rule. Frontmatter for activation; body is markdown inside an XML `<rule>` wrapper.
- No `---` in body outside frontmatter.

Frontmatter:

- `alwaysApply: true` — always included.
- `globs` + `alwaysApply: false` — auto-attached when matching files are in context.
- `description` + `alwaysApply: false` — agent-requested (AI decides when to include).

Body:

- Wrap body in `<rule for="id">` ... `</rule>`.
- `for` encodes section and hierarchy: `"dir-name"` for main rules (`00-main.md`), `"dir-name/slug"` for sub-rules (slug = filename without ordering prefix or extension).
