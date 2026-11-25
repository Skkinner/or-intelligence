"""Claude (Anthropic) client. Server side only: the API key comes from the environment and never reaches the browser.

Environment:
  ANTHROPIC_API_KEY      key from the Claude Console (required)
  ORI_LLM_MODEL          model id (default claude-sonnet-5-5)
  ORI_ALLOW_EXTERNAL_AI  must be "1" to let de-identified case text go to the external service (default off)
"""
from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_MODEL = "claude-sonnet-5-5"


class LLMError(Exception):
    """Any failure talking to the model; the message is safe to show to the user (never contains the key)."""


@dataclass
class Result:
    text: str
    tokens_in: int
    tokens_out: int
    model: str


def model_name() -> str:
    return os.environ.get("ORI_LLM_MODEL", DEFAULT_MODEL)


def status() -> tuple[bool, str]:
    """(usable, reason_code). reason_code: '' | 'no_key' | 'not_approved' | 'no_package'."""
    if os.environ.get("ORI_ALLOW_EXTERNAL_AI", "0") != "1":
        return False, "not_approved"
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False, "no_key"
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False, "no_package"
    return True, ""


def _client():
    import anthropic
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=90.0, max_retries=2)


def complete(system: str, messages: list[dict], max_tokens: int = 1800) -> Result:
    """One non-streaming call. `messages` = [{"role": "user"|"assistant", "content": str}]."""
    ok, why = status()
    if not ok:
        raise LLMError({"not_approved": "External AI is not enabled (set ORI_ALLOW_EXTERNAL_AI=1).",
                        "no_key": "ANTHROPIC_API_KEY is not set on the server.",
                        "no_package": "The 'anthropic' package is not installed."}[why])
    import anthropic
    try:
        r = _client().messages.create(model=model_name(), max_tokens=max_tokens, system=system, messages=messages)
    except anthropic.AuthenticationError:
        raise LLMError("The Claude API key was rejected. Check ANTHROPIC_API_KEY.") from None
    except anthropic.RateLimitError:
        raise LLMError("Claude is rate-limited right now. Wait a minute and try again.") from None
    except anthropic.APIConnectionError:
        raise LLMError("Cannot reach the Claude API. Check the network connection.") from None
    except anthropic.APIStatusError as e:
        raise LLMError(f"Claude API error (HTTP {e.status_code}).") from None
    text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
    if not text:
        raise LLMError("Claude returned an empty answer.")
    return Result(text=text, tokens_in=r.usage.input_tokens, tokens_out=r.usage.output_tokens, model=r.model)
