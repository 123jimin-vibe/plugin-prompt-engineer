VSCode extension for BFC, a BrainFuck compiler. BF = BrainFuck; BSM = BrainFuck assembly mnemonic language with three abstraction levels (core → frames → macros).

## AGENTS.md for `editors/vscode/`

VSCode extension providing syntax highlighting for BF and BSM.

- No build step — pure declarative TextMate grammars + language configs.
- Grammar design mirrors the three BSM levels (core → frames → macros) but in a single grammar file since TextMate has no layered-grammar support.
- BF grammar treats `#` as line comment by default; the hash-vs-breakpoint ambiguity is unresolvable statically (configurable at runtime in the compiler, not in the grammar).
- Icon files under `icons/` are placeholders — replace with real PNGs before publishing.
- Package with `vsce package` from this directory.
