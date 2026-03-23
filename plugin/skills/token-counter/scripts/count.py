"""Token counter — stub that verifies dependencies are importable."""

try:
    import tiktoken
    print(f"tiktoken {tiktoken.__version__} OK")
except ImportError as e:
    raise SystemExit(f"tiktoken not available: {e}")

try:
    from lib.test import ping
    assert ping() == "pong"
    print(f"lib.test.ping() OK")
except ImportError as e:
    raise SystemExit(f"lib not available: {e}")
