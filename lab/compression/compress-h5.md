Compress the given text. Rules:
- Preserve all meaning, technical constraints, and specificity.
- Remove redundancy, filler, verbose phrasing, and unnecessary elaboration.
- Do not add new information or interpretation.
- Output only the compressed text. No commentary.

Examples:

Input:
## Naming

- `snake_case` — variables, attributes, arguments
- `camelCase` — functions (including function-typed variables)
- `PascalCase` — classes, interfaces, types

Output:
## Naming
`snake_case` vars/attrs/args · `camelCase` functions · `PascalCase` classes/interfaces/types

Input:
These optimizations are distinct from AST optimization passes, which transform the AST before interpretation. Interpreter optimizations leave the AST unchanged and instead short-circuit execution.

Output:
Unlike AST passes that transform before interpretation, interpreter optimizations leave the AST unchanged and short-circuit execution.

Input:
Subsystem initialization failures (WASAPI device unavailable, DX12 device creation failure, etc.) are reported to the user and the application exits cleanly with a diagnostic message (via logging if available, otherwise stderr/message box).

Runtime failures trigger a clean shutdown. The application does not attempt hot recovery; the user restarts. This is acceptable for a calibration utility that is not a long-running service.

Output:
All failures → clean exit. Init failures (WASAPI, DX12, etc.) reported via logging if available, otherwise stderr/message box. Runtime failures: no hot recovery; user restarts. Acceptable for a calibration utility, not a long-running service.