"""Token counter — stub that verifies tiktoken is importable."""

try:
    import tiktoken
    print(f"tiktoken {tiktoken.__version__} OK")
except ImportError as e:
    raise SystemExit(f"tiktoken not available: {e}")
