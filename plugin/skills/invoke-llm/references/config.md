# TOML Config Schema

```toml
# Used with prompt-engineer:invoke-llm skill.

[generation]
model = ["claude-sonnet-4-6", "gpt-5.4-mini"]   # scalar or array (sweep)
temperature = [0.0, 0.5, 1.0]                  # scalar or array (sweep)
max_tokens = [512, 1024, 4096]                  # scalar or array (sweep)
separator = "\n\n"                              # default join between same-role entries

[vars]
input = ["inputs/case1.md", "inputs/case2.md"]  # scalar or array (sweep); content read at runtime

[[prompts]]
role = "system"                       # "system", "user", or "assistant"
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
| `max_tokens` | int or array | `4096` | Max output tokens. Array = sweep dimension. |
| `separator` | string | `"\n\n"` | Default join between same-role prompt entries. |

### `[vars]`

Named file references. Keys become variable names; values are file paths (scalar or array). Array values are sweep dimensions — each file path produces a separate run. Content is read at runtime and injected into prompts via `{{key}}` placeholders when `substitute = true`.

### `[[prompts]]`

Ordered list of prompt entries. Entries are assembled into a message sequence matching the pattern `system? (user assistant)* user`. Consecutive same-role entries are joined with the separator.

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `role` | string | yes | `"system"`, `"user"`, or `"assistant"`. |
| `prompt` | string | one of `prompt`/`file` | Inline text. |
| `file` | string or array | one of `prompt`/`file` | File path(s). Array = sweep dimension. |
| `substitute` | bool | no | Replace `{{key}}` placeholders with `[vars]` content. |
| `separator` | string | no | Overrides `[generation].separator` for this entry's join point. |

### `[output]`

| Key | Type | Description |
|-----|------|-------------|
| `file` | string | Output file path. Written as JSONL (one record per run). |

## Matrix sweep

The cartesian product of all array values across `[generation]`, `[vars]`, and `[[prompts]]`. Example above: 2 models x 3 max_tokens x 2 inputs x 2 system files = 24 runs.

## Path resolution

All file paths (`file`, `[vars]`, `[output].file`) resolve relative to the TOML file's parent directory.

## Variable substitution

When `substitute = true`, `{{key}}` placeholders are replaced with content from `[vars]`. A reference to a missing key is an error — the run aborts with a message naming the unresolved key.

## Comment convention

Start config files with `# Used with prompt-engineer:invoke-llm skill.` for identification.
