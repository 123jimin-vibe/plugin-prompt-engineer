# TOML Config Schema

```toml
# Used with prompt-engineer:invoke-llm skill.

[generation]
model = ["claude-sonnet-4-6", "gpt-5-mini"]   # scalar or array (sweep)
temperature = [0.0, 0.5, 1.0]                  # scalar or array (sweep)
max_tokens = 4096                               # scalar only
separator = "\n\n"                              # default join between same-role entries

[vars]
input = "inputs/case1.md"            # named file refs, content read at runtime

[[prompts]]
role = "system"                       # "system" or "user"
file = ["strict.md", "relaxed.md"]    # array = sweep dimension

[[prompts]]
role = "user"
prompt = "inline text"                # use file or prompt, not both

[[prompts]]
role = "user"
file = "question.md"
substitute = true                     # replace {{key}} with [vars] content
separator = "\n---\n"                 # overrides [generation].separator for this join point

[output]
file = "results.jsonl"
```

## Sections

### `[generation]`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `model` | string or array | `"claude-sonnet-4-6"` | Model ID(s). Array = sweep dimension. |
| `temperature` | float or array | — | Temperature(s). Array = sweep dimension. |
| `max_tokens` | int | `4096` | Max output tokens. Scalar only. |
| `separator` | string | `"\n\n"` | Default join between same-role prompt entries. |

### `[vars]`

Named file references. Keys become variable names; values are file paths. Content is read at runtime and injected into prompts via `{{key}}` placeholders when `substitute = true`.

### `[[prompts]]`

Ordered list of prompt entries. Each entry contributes to either the system or user message.

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `role` | string | yes | `"system"` or `"user"`. |
| `prompt` | string | one of `prompt`/`file` | Inline text. |
| `file` | string or array | one of `prompt`/`file` | File path(s). Array = sweep dimension. |
| `substitute` | bool | no | Replace `{{key}}` placeholders with `[vars]` content. |
| `separator` | string | no | Overrides `[generation].separator` for this entry's join point. |

### `[output]`

| Key | Type | Description |
|-----|------|-------------|
| `file` | string | Output file path. Each run appends one JSONL record. |

## Matrix sweep

The cartesian product of all array values across `[generation]` and `[[prompts]]`. Example above: 2 models x 3 temperatures x 2 system files = 12 runs.

## Path resolution

All file paths (`file`, `[vars]`, `[output].file`) resolve relative to the TOML file's parent directory.

## Variable substitution

When `substitute = true`, `{{key}}` placeholders are replaced with content from `[vars]`. A reference to a missing key is an error — the run aborts with a message naming the unresolved key.

## Comment convention

Start config files with `# Used with prompt-engineer:invoke-llm skill.` for identification.
