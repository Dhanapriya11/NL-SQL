"""
Unified LLM client — Ollama (local) or OpenRouter (cloud API key).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

import requests

Provider = Literal["ollama", "openrouter"]

OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
DEFAULT_OPENROUTER_MODEL = os.environ.get(
    "OPENROUTER_MODEL", "google/gemini-2.5-flash"
)

OPENROUTER_MODELS = [
    "google/gemini-2.5-flash",
    "google/gemini-2.5-flash-lite",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-7b-instruct",
]


@dataclass
class LLMConfig:
    provider: Provider = "openrouter"
    model: str = DEFAULT_OPENROUTER_MODEL
    api_key: str = ""


def _ascii_header(value: str) -> str:
    return value.encode("ascii", errors="ignore").decode("ascii")


def chat(
    prompt: str,
    config: LLMConfig,
    temperature: float = 0.1,
    timeout: int = 90,
) -> str:
    """Send a single user prompt and return assistant text."""
    if config.provider == "openrouter":
        return _openrouter_chat(prompt, config, temperature, timeout)
    return _ollama_chat(prompt, config.model, temperature, timeout)


def _ollama_chat(
    prompt: str, model: str, temperature: float, timeout: int
) -> str:
    url = f"{OLLAMA_URL.rstrip('/')}/api/chat"
    payload = {
        "model": model or DEFAULT_OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")
    except requests.ConnectionError as exc:
        raise ConnectionError(
            f"Cannot reach Ollama at {OLLAMA_URL}. Run: ollama serve && ollama pull llama3"
        ) from exc
    except requests.Timeout as exc:
        raise TimeoutError(
            f"Ollama timed out after {timeout}s. "
            "Switch to OpenRouter in the sidebar (faster on slow PCs)."
        ) from exc


def _openrouter_chat(
    prompt: str, config: LLMConfig, temperature: float, timeout: int
) -> str:
    if not config.api_key.strip():
        raise ValueError(
            "OpenRouter API key required. "
            "Paste it in the sidebar or set OPENROUTER_API_KEY. "
            "Get one at https://openrouter.ai/keys"
        )
    headers = {
        "Authorization": f"Bearer {config.api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": _ascii_header(
            os.environ.get("OPENROUTER_REFERER", "http://localhost:8501")
        ),
        "X-Title": "NL-to-SQL Analytics Agent",
    }
    payload = {
        "model": config.model or DEFAULT_OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 2048,
    }
    try:
        resp = requests.post(
            OPENROUTER_URL, headers=headers, json=payload, timeout=timeout
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.HTTPError as exc:
        msg = str(exc)
        try:
            err = exc.response.json().get("error", {})
            if isinstance(err, dict) and err.get("message"):
                msg = err["message"]
        except Exception:
            pass
        raise RuntimeError(f"OpenRouter error: {msg}") from exc
    except requests.Timeout as exc:
        raise TimeoutError(f"OpenRouter timed out after {timeout}s.") from exc


def check_provider(config: LLMConfig) -> tuple[bool, str]:
    """Health check shown in the Streamlit sidebar."""
    if config.provider == "openrouter":
        if not config.api_key.strip():
            return False, "Paste your OpenRouter API key in the sidebar"
        return True, f"OpenRouter ready — {config.model}"

    model_id = config.model or DEFAULT_OLLAMA_MODEL
    try:
        url = f"{OLLAMA_URL.rstrip('/')}/api/tags"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        tags = resp.json().get("models", [])
        names = {m.get("name", "").split(":")[0] for m in tags}
        base = model_id.split(":")[0]
        if base not in names:
            return False, f"Ollama OK but run: ollama pull {base}"
        return True, f"Ollama OK — {model_id}"
    except Exception as exc:
        return False, f"Ollama unavailable: {exc}"
