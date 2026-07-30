import pytest
from unittest.mock import MagicMock
from src.mi_bot.core.personalities import get_personality_prompt

def test_personality_prompt():
    """Verify that the personality prompt is returned correctly."""
    prompt = get_personality_prompt("amigo")
    assert "Alex" in prompt
    assert "tecnología" in prompt

def test_invalid_personality_fallback():
    """Verify fallback to 'amigo' for unknown keys."""
    prompt = get_personality_prompt("unknown_key")
    assert "Alex" in prompt

def test_config_load():
    """Verify that settings load properly (default values)."""
    from src.mi_bot.core.config import settings
    assert settings.API_PORT == 8000
