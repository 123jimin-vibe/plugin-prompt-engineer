"""Invoke LLM — raw API calls (text in, text out)."""

import argparse
import json
import sys
import tomllib
from itertools import product
from pathlib import Path

from lib.io import ensure_utf8_stdio
from lib.llm import invoke as llm_invoke


# ===================================================================
# Argument parsing
# ===================================================================

class _OrderedPrompt:
    """Track a prompt entry with its insertion order."""

    __slots__ = ("role", "text", "order")

    def __init__(self, role: str, text: str, order: int):
        self.role = role
        self.text = text
        self.order = order


_counter = 0


def _next_order() -> int:
    global _counter
    _counter += 1
    return _counter


class _AppendOrdered(argparse.Action):
    """Custom action that records insertion order across all prompt flags."""

    def __call__(self, _parser, namespace, values, option_string=None):
        assert isinstance(values, str)
        entries = getattr(namespace, "_ordered_prompts", [])
        role = "system" if option_string in ("-s", "-S") else "user"
        is_file = option_string in ("-S", "-U")
        if is_file:
            text = Path(values).read_text(encoding="utf-8")
        else:
            text = values
        entries.append(_OrderedPrompt(role, text, _next_order()))
        namespace._ordered_prompts = entries


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments with mutual exclusion enforcement."""
    global _counter
    _counter = 0

    parser = argparse.ArgumentParser(
        description="Invoke LLM — raw API calls.",
        add_help=True,
    )

    # Config mode
    config_group = parser.add_argument_group("config mode")
    config_group.add_argument("-c", default=None, metavar="FILE", help="TOML config file.")
    config_group.add_argument("--dry-run", action="store_true", help="Print sweep summary, no API calls.")

    # Single-shot mode
    shot_group = parser.add_argument_group("single-shot mode")
    shot_group.add_argument("positional", nargs="?", default=None, help="User prompt (shorthand for -u).")
    shot_group.add_argument("-u", action=_AppendOrdered, metavar="TEXT", help="User prompt string (repeatable).")
    shot_group.add_argument("-U", action=_AppendOrdered, metavar="FILE", help="User prompt from file (repeatable).")
    shot_group.add_argument("-s", action=_AppendOrdered, metavar="TEXT", help="System prompt string (repeatable).")
    shot_group.add_argument("-S", action=_AppendOrdered, metavar="FILE", help="System prompt from file (repeatable).")

    # Generation
    gen_group = parser.add_argument_group("generation")
    gen_group.add_argument("-m", default="claude-sonnet-4-6", metavar="MODEL", help="Model ID.")
    gen_group.add_argument("-t", type=float, default=None, metavar="TEMP", help="Temperature.")
    gen_group.add_argument("--max-tokens", type=int, default=4096, metavar="N", help="Max output tokens.")

    # Output
    out_group = parser.add_argument_group("output")
    fmt = out_group.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", help="JSONL output with metadata.")
    fmt.add_argument("--toml", action="store_true", help="TOML output with metadata.")
    out_group.add_argument("-o", default=None, metavar="FILE", help="Write output to file.")
    out_group.add_argument("-q", action="store_true", help="Suppress response text in stdout.")

    ns = parser.parse_args(argv)

    # Validation: -c is mutually exclusive with single-shot flags
    has_singleshot = (
        ns.positional is not None
        or hasattr(ns, "_ordered_prompts") and ns._ordered_prompts
    )
    if ns.c and has_singleshot:
        parser.error("-c is mutually exclusive with single-shot prompt flags (-u, -U, -s, -S, positional)")

    if ns.dry_run and not ns.c:
        parser.error("--dry-run requires -c")

    # Inject positional as first user prompt entry
    if ns.positional is not None:
        entries = getattr(ns, "_ordered_prompts", [])
        entries.insert(0, _OrderedPrompt("user", ns.positional, 0))
        ns._ordered_prompts = entries

    return ns


# ===================================================================
# Prompt assembly
# ===================================================================

_DEFAULT_SEPARATOR = "\n\n"


def build_prompt(args: argparse.Namespace) -> dict[str, str]:
    """Assemble system/user messages from flags in insertion order."""
    entries = getattr(args, "_ordered_prompts", [])
    entries.sort(key=lambda e: e.order)

    system_parts: list[str] = []
    user_parts: list[str] = []

    for entry in entries:
        if entry.role == "system":
            system_parts.append(entry.text)
        else:
            user_parts.append(entry.text)

    result: dict[str, str] = {}
    if system_parts:
        result["system"] = _DEFAULT_SEPARATOR.join(system_parts)
    result["user"] = _DEFAULT_SEPARATOR.join(user_parts) if user_parts else ""
    return result


# ===================================================================
# Config mode
# ===================================================================


def load_config(path: str) -> dict:
    """Parse TOML config, resolve file paths relative to TOML parent."""
    toml_path = Path(path).resolve()
    base_dir = toml_path.parent

    with open(toml_path, "rb") as f:
        config = tomllib.load(f)

    # Resolve file paths in [[prompts]]
    for prompt in config.get("prompts", []):
        if "file" in prompt:
            val = prompt["file"]
            if isinstance(val, list):
                prompt["file"] = [str(base_dir / f) for f in val]
            else:
                prompt["file"] = str(base_dir / val)

    # Resolve file paths in [vars]
    for key, val in config.get("vars", {}).items():
        if isinstance(val, str):
            config["vars"][key] = str(base_dir / val)

    # Resolve [output].file
    output = config.get("output", {})
    if "file" in output:
        output["file"] = str(base_dir / output["file"])

    return config


def expand_matrix(config: dict) -> list[dict]:
    """Cartesian product of all sweep dimensions → list of run specs."""
    gen = config.get("generation", {})

    # Collect sweep dimensions
    dimensions: list[tuple[str, list]] = []

    # Model
    model = gen.get("model", "claude-sonnet-4-6")
    models = model if isinstance(model, list) else [model]
    if len(models) > 1:
        dimensions.append(("model", models))

    # Temperature
    temp = gen.get("temperature")
    if temp is not None:
        temps = temp if isinstance(temp, list) else [temp]
        if len(temps) > 1:
            dimensions.append(("temperature", temps))

    # Prompt sweeps (file arrays and prompt arrays)
    prompts = config.get("prompts", [])
    for i, prompt in enumerate(prompts):
        if "file" in prompt and isinstance(prompt["file"], list):
            dimensions.append((f"prompt_{i}_file", prompt["file"]))
        if "prompt" in prompt and isinstance(prompt["prompt"], list):
            dimensions.append((f"prompt_{i}_prompt", prompt["prompt"]))

    # Build cartesian product
    if not dimensions:
        # Single run — no sweep dimensions
        return [_build_run_spec(config, {})]

    dim_names = [d[0] for d in dimensions]
    dim_values = [d[1] for d in dimensions]

    runs = []
    for combo in product(*dim_values):
        overrides = dict(zip(dim_names, combo))
        run = _build_run_spec(config, overrides)
        run["_overrides"] = overrides
        runs.append(run)

    return runs


def _build_run_spec(config: dict, overrides: dict) -> dict:
    """Build a single run spec from config + sweep overrides."""
    gen = config.get("generation", {})
    separator = gen.get("separator", _DEFAULT_SEPARATOR)

    model = overrides.get("model", gen.get("model", "claude-sonnet-4-6"))
    if isinstance(model, list):
        model = model[0]

    temp = overrides.get("temperature", gen.get("temperature"))
    if isinstance(temp, list):
        temp = temp[0]

    max_tokens = gen.get("max_tokens", 4096)

    # Assemble prompts
    system_parts: list[str] = []
    user_parts: list[str] = []
    vars_content = _load_vars(config)

    for i, prompt in enumerate(config.get("prompts", [])):
        role = prompt["role"]
        do_substitute = prompt.get("substitute", False)

        # Resolve text
        if "prompt" in prompt:
            text = overrides.get(f"prompt_{i}_prompt", prompt["prompt"])
            if isinstance(text, list):
                text = text[0]
        elif "file" in prompt:
            file_val = overrides.get(f"prompt_{i}_file", prompt["file"])
            if isinstance(file_val, list):
                file_val = file_val[0]
            text = Path(file_val).read_text(encoding="utf-8")
        else:
            continue

        if do_substitute:
            text = substitute_vars(text, vars_content)

        if role == "system":
            system_parts.append(text)
        else:
            user_parts.append(text)

    messages: dict[str, str] = {}
    if system_parts:
        messages["system"] = separator.join(system_parts)
    if user_parts:
        messages["user"] = separator.join(user_parts)

    spec = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if temp is not None:
        spec["temperature"] = temp

    return spec


def _load_vars(config: dict) -> dict[str, str]:
    """Load [vars] file contents."""
    vars_section = config.get("vars", {})
    result: dict[str, str] = {}
    for key, filepath in vars_section.items():
        result[key] = Path(filepath).read_text(encoding="utf-8")
    return result


def substitute_vars(text: str, vars_content: dict[str, str]) -> str:
    """Replace ``{{key}}`` placeholders. Error on missing key."""
    import re

    def _replace(match):
        key = match.group(1).strip()
        if key not in vars_content:
            raise SystemExit(f"Unresolved variable: {{{{{key}}}}}")
        return vars_content[key]

    return re.sub(r"\{\{(\s*\w+\s*)\}\}", _replace, text)


# ===================================================================
# Output formatting
# ===================================================================


def format_result(result: dict, fmt: str | None, quiet: bool) -> str:
    """Format one result as plain/JSON/TOML, honoring -q."""
    if fmt == "json":
        data = dict(result)
        if quiet:
            data.pop("response", None)
        return json.dumps(data)

    if fmt == "toml":
        lines: list[str] = []
        for key, val in result.items():
            if quiet and key == "response":
                continue
            if isinstance(val, str):
                # Escape for TOML string
                escaped = val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
                lines.append(f'{key} = "{escaped}"')
            elif isinstance(val, int):
                lines.append(f"{key} = {val}")
            elif isinstance(val, float):
                lines.append(f"{key} = {val}")
        return "\n".join(lines)

    # Plain text
    if quiet:
        return ""
    return result["response"]


# ===================================================================
# Dry run
# ===================================================================


def dry_run(matrix: list[dict]) -> None:
    """Print dimension summary and total count to stdout."""
    print(f"Total runs: {len(matrix)}")

    dims: dict[str, set] = {}
    for run in matrix:
        for key, val in run.get("_overrides", {}).items():
            dims.setdefault(key, set()).add(str(val))

    for dim_name, values in dims.items():
        if len(values) > 1:
            print(f"  {dim_name}: {', '.join(sorted(values))}")


# ===================================================================
# Main
# ===================================================================


def main() -> None:
    """Entry point: parse → single-shot or config → invoke → format → output."""
    ensure_utf8_stdio()
    args = parse_args(sys.argv[1:])

    fmt = "json" if args.json else ("toml" if args.toml else None)

    if args.c:
        # Config mode
        config = load_config(args.c)
        matrix = expand_matrix(config)

        if args.dry_run:
            dry_run(matrix)
            return

        output_path = config.get("output", {}).get("file")
        output_file = open(output_path, "w", encoding="utf-8") if output_path else None

        errors: list[tuple[int, str]] = []
        results: list[dict] = []

        try:
            for i, run_spec in enumerate(matrix):
                try:
                    temp = run_spec.get("temperature", 1.0)
                    result = llm_invoke(
                        messages=run_spec["messages"],
                        model=run_spec["model"],
                        temperature=temp,
                        max_tokens=run_spec["max_tokens"],
                    )
                    results.append(result)
                    formatted = format_result(result, fmt, args.q)
                    if formatted:
                        print(formatted)
                    if output_file:
                        output_file.write(format_result(result, "json", False) + "\n")
                except Exception as exc:
                    errors.append((i, str(exc)))
        finally:
            if output_file:
                output_file.close()

        # TOML batch output
        if fmt == "toml" and results:
            # Already printed per-result above
            pass

        # Error summary
        if errors:
            from lib.format import render_table

            rows = [(str(idx), msg) for idx, msg in errors]
            table = render_table(rows, ["Run", "Error"])
            print(table, file=sys.stderr)
            raise SystemExit(f"{len(errors)} run(s) failed.")

    else:
        # Single-shot mode
        messages = build_prompt(args)
        if not messages.get("user") and not messages.get("system"):
            raise SystemExit("No prompts provided.")

        temp = args.t if args.t is not None else 1.0
        result = llm_invoke(
            messages=messages,
            model=args.m,
            temperature=temp,
            max_tokens=args.max_tokens,
        )

        formatted = format_result(result, fmt, args.q)
        if formatted:
            print(formatted)

        # Write to -o file
        if args.o:
            with open(args.o, "w", encoding="utf-8") as f:
                f.write(result["response"])


if __name__ == "__main__":
    main()
