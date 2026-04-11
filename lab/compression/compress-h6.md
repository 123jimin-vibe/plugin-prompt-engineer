Compress the given text by restructuring, not word-trimming.

Merge clauses, eliminate repeated subjects, use compact inline notation (`·`).
Do not swap synonyms, swap voice, or convert to markdown tables — zero savings.
Preserve all meaning. Do not add interpretation. Output only the compressed text.

Input:
## Naming

- `snake_case` — variables, attributes, arguments
- `camelCase` — functions (including function-typed variables)
- `PascalCase` — classes, interfaces, types

Output:
## Naming
`snake_case` vars/attrs/args · `camelCase` functions (incl. function-typed vars) · `PascalCase` classes/interfaces/types

Input:
These optimizations are distinct from AST optimization passes, which transform the AST before interpretation. Interpreter optimizations leave the AST unchanged and instead short-circuit execution.

Output:
Unlike AST optimization passes that transform before interpretation, interpreter optimizations leave the AST unchanged and instead short-circuit execution.

Input:
### Failure Policy

Subsystem initialization failures (WASAPI device unavailable, DX12 device creation failure, etc.) are reported to the user and the application exits cleanly with a diagnostic message (via logging if available, otherwise stderr/message box).

Runtime failures trigger a clean shutdown. The application does not attempt hot recovery; the user restarts. This is acceptable for a calibration utility that is not a long-running service.

Output:
### Failure Policy
Subsystem init failures (WASAPI, DX12, etc.) → clean exit with diagnostic to user (via logging if available, otherwise stderr/message box). Runtime failures: no hot recovery; user restarts. Acceptable for a calibration utility that is not a long-running service.