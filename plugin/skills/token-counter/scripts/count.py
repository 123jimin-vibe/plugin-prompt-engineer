"""Token counter — count tokens in strings or files across models."""

import argparse
import sys
from pathlib import Path

MAX_NAME_LEN = 20

_anthropic_client = None


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Count tokens.")
    parser.add_argument("strings", nargs="*", help="Strings to count.")
    parser.add_argument("-f", action="append", default=[], help="File to count.")
    parser.add_argument(
        "-m", action="append", default=None, help="Model or tiktoken encoding."
    )
    parser.add_argument("-s", action="store_true", help="Per-section breakdown (TODO).")
    ns = parser.parse_args(argv)
    if ns.m is None:
        ns.m = ["claude-opus-4-6"]
    return ns


def collect_inputs(args: argparse.Namespace) -> list[tuple[str, str]]:
    """Return [(name, text), ...] from parsed args."""
    inputs: list[tuple[str, str]] = []
    for s in args.strings:
        name = s if len(s) <= MAX_NAME_LEN else s[:MAX_NAME_LEN] + "..."
        inputs.append((name, s))
    for fpath in args.f:
        text = Path(fpath).read_text(encoding="utf-8")
        inputs.append((Path(fpath).name, text))
    return inputs


def is_claude_model(model: str) -> bool:
    """Return True if *model* is a Claude model."""
    return model.startswith("claude-")


def count_tokens(text: str, model: str) -> int:
    """Count tokens for *text* using the appropriate backend."""
    if is_claude_model(model):
        global _anthropic_client
        if _anthropic_client is None:
            from anthropic import Anthropic

            _anthropic_client = Anthropic()
        resp = _anthropic_client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": text}],
        )
        return resp.input_tokens

    import tiktoken

    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding(model)
    return len(enc.encode(text))


def format_output(
    inputs: list[tuple[str, str]],
    models: list[str],
    counts: dict[tuple[str, str], int],
) -> str:
    """Format counts as a scalar or table."""
    if len(inputs) == 1 and len(models) == 1:
        key = (inputs[0][0], models[0])
        return str(counts[key])

    from lib.format import render_table

    multi_input = len(inputs) > 1
    multi_model = len(models) > 1

    columns: list[str] = []
    if multi_input:
        columns.append("Input")
    if multi_model:
        columns.append("Model")
    columns.append("Tokens")

    rows: list[tuple[str, ...]] = []
    for name, _ in inputs:
        for model in models:
            row: list[str] = []
            if multi_input:
                row.append(name)
            if multi_model:
                row.append(model)
            row.append(str(counts[(name, model)]))
            rows.append(tuple(row))

    return render_table(rows, columns)


def main() -> None:
    """Entry point."""
    args = parse_args(sys.argv[1:])
    inputs = collect_inputs(args)
    if not inputs:
        raise SystemExit("No inputs provided.")

    counts: dict[tuple[str, str], int] = {}
    for name, text in inputs:
        for model in args.m:
            counts[(name, model)] = count_tokens(text, model)

    print(format_output(inputs, args.m, counts))


if __name__ == "__main__":
    main()
