"""Tests for prompt engine."""

import pytest
from sst_tts_translator.prompt import PromptEngine


def test_prompt_engine_initialization():
    """Test prompt engine initialization."""
    engine = PromptEngine()
    assert engine is not None


def test_translate_to_structured_prompt():
    """Test translating natural text to structured prompt."""
    engine = PromptEngine()
    
    text = "create a FastAPI endpoint for user authentication"
    prompt = engine.translate_to_structured_prompt(
        natural_text=text,
        task_type="code_generation",
        include_cot=True
    )
    
    assert "<task type='code_generation'>" in prompt
    assert text in prompt
    assert "<reasoning>" in prompt


def test_extract_intent():
    """Test intent extraction."""
    engine = PromptEngine()
    
    # Test create intent
    assert engine._extract_intent("create a new API", "default") == "create"
    
    # Test modify intent
    assert engine._extract_intent("change the function", "default") == "modify"
    
    # Test debug intent
    assert engine._extract_intent("fix the bug", "default") == "debug"


def test_extract_entities():
    """Test entity extraction."""
    engine = PromptEngine()
    
    text = "create a Python FastAPI REST API"
    entities = engine._extract_entities(text)
    
    assert entities.get("language") == "python"
    assert entities.get("framework") == "fastapi"
    assert entities.get("pattern") == "rest api"
