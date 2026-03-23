"""API key validation — reusable across providers."""

import os

_PROVIDER_ENV_VARS: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def require_api_key(provider: str) -> str:
    """Return the API key for *provider*, or exit with a clear error."""
    env_var = _PROVIDER_ENV_VARS.get(provider)
    if env_var is None:
        raise SystemExit(f"Unknown API provider: {provider}")
    key = os.environ.get(env_var, "")
    if not key:
        raise SystemExit(f"{env_var} is not set.")
    return key
