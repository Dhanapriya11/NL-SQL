"""Tests for LLM configuration."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_client import LLMConfig, check_provider


def test_openrouter_requires_key():
    cfg = LLMConfig(provider="openrouter", model="google/gemini-2.5-flash", api_key="")
    ok, msg = check_provider(cfg)
    assert ok is False
    assert "API key" in msg


def test_openrouter_with_key():
    cfg = LLMConfig(provider="openrouter", model="google/gemini-2.5-flash", api_key="sk-test")
    ok, msg = check_provider(cfg)
    assert ok is True
    assert "OpenRouter" in msg
