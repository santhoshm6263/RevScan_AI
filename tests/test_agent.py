"""Comprehensive unit tests for Module: AI Explorer (src/agent/)."""
import pytest
from src.agent.ai_provider import (
    get_ai_provider,
    MockAIProvider,
    GeminiAIProvider,
    OpenAIAIProvider,
    OllamaAIProvider
)
from src.agent.prompts import (
    EXPLORATION_SYSTEM_PROMPT,
    format_screen_context_prompt
)
from src.agent.action_schema import (
    extract_json_from_text,
    validate_action
)
from src.agent.explorer import ExplorerAgent, explorer_agent
from src.core.models import ActionModel
from src.core.config import settings


def test_extract_json_from_text():
    """Test extracting JSON from various raw string formats."""
    # Direct dict
    res = extract_json_from_text({"type": "tap", "target_id": "btn_1"})
    assert res == {"type": "tap", "target_id": "btn_1"}

    # Markdown block with json fence
    raw_markdown = """Here is the next action:
```json
{
  "type": "type",
  "target_id": "input_email",
  "text": "test@example.com"
}
```
Hope this helps!"""
    res = extract_json_from_text(raw_markdown)
    assert res is not None
    assert res["type"] == "type"
    assert res["target_id"] == "input_email"
    assert res["text"] == "test@example.com"

    # Plain text containing JSON object
    raw_text = 'Sure, the action is {"type": "scroll", "direction": "down"}'
    res = extract_json_from_text(raw_text)
    assert res == {"type": "scroll", "direction": "down"}

    # Invalid input
    assert extract_json_from_text("Invalid non-json text") is None


def test_validate_action():
    """Test action schema validation."""
    # Valid tap
    action = validate_action({"type": "tap", "target_id": "btn_login"})
    assert isinstance(action, ActionModel)
    assert action.type == "tap"
    assert action.target_id == "btn_login"

    # Valid scroll with direction fallback
    action = validate_action({"type": "scroll"})
    assert isinstance(action, ActionModel)
    assert action.type == "scroll"
    assert action.direction == "down"

    # Valid type action
    action = validate_action({"type": "type", "target_id": "field_user", "text": "john"})
    assert isinstance(action, ActionModel)
    assert action.type == "type"
    assert action.text == "john"

    # Invalid target check
    valid_targets = {"btn_submit", "field_email"}
    assert validate_action({"type": "tap", "target_id": "unknown_btn"}, valid_target_ids=valid_targets) is None
    assert validate_action({"type": "tap", "target_id": "btn_submit"}, valid_target_ids=valid_targets) is not None

    # Invalid action type
    assert validate_action({"type": "fly_to_moon"}) is None


def test_format_screen_context_prompt():
    """Test formatting screen context prompt."""
    screen_context = {
        "screen": {"id": "screen_001", "name": "LoginScreen"},
        "elements": [
            {"id": "usr_input", "type": "input", "text": "Username", "clickable": True},
            {"id": "btn_submit", "type": "button", "text": "Submit", "clickable": True}
        ],
        "previous_actions": [{"type": "tap", "target_id": "usr_input"}]
    }
    prompt_str = format_screen_context_prompt(screen_context)
    assert "screen_001" in prompt_str
    assert "usr_input" in prompt_str
    assert "btn_submit" in prompt_str


def test_mock_ai_provider():
    """Test MockAIProvider decision logic."""
    provider = MockAIProvider()
    screen_context = {
        "elements": [
            {"id": "email_input", "type": "input", "text": "Email", "clickable": True},
            {"id": "login_btn", "type": "button", "text": "Login", "clickable": True}
        ],
        "previous_actions": []
    }

    # First decision should be typing into un-typed input
    action = provider.generate_action(EXPLORATION_SYSTEM_PROMPT, screen_context)
    assert action["type"] == "type"
    assert action["target_id"] == "email_input"

    # Update previous_actions to mark input typed
    screen_context["previous_actions"].append(action)

    # Second decision should tap un-tapped button
    action2 = provider.generate_action(EXPLORATION_SYSTEM_PROMPT, screen_context)
    assert action2["type"] == "tap"
    assert action2["target_id"] == "login_btn"


def test_explorer_agent_decide():
    """Test ExplorerAgent end-to-end decision flow with loop detection and fallback."""
    agent = ExplorerAgent(provider=MockAIProvider())

    screen_context = {
        "screen": {"id": "screen_main", "name": "Main"},
        "elements": [
            {"id": "btn_home", "type": "button", "text": "Home", "clickable": True},
            {"id": "btn_settings", "type": "button", "text": "Settings", "clickable": True}
        ]
    }

    action = agent.decide(screen_context, history=[])
    assert isinstance(action, ActionModel)
    assert action.type == "tap"
    assert action.target_id == "btn_home"


def test_explorer_agent_loop_detection():
    """Test loop detection in ExplorerAgent."""
    agent = ExplorerAgent(provider=MockAIProvider())

    # Mock screen context where Mock provider wants to tap btn_home repeatedly
    screen_context = {
        "screen": {"id": "screen_stuck", "name": "StuckScreen"},
        "elements": [
            {"id": "btn_home", "type": "button", "text": "Home", "clickable": True}
        ]
    }

    # Simulate that btn_home was tapped twice in recent history
    repeating_history = [
        {"type": "tap", "target_id": "btn_home"},
        {"type": "tap", "target_id": "btn_home"}
    ]

    action = agent.decide(screen_context, history=repeating_history)
    # Should detect loop and return scroll action instead of tapping btn_home again
    assert action.type == "scroll"
    assert action.direction == "down"


def test_get_ai_provider_factory():
    """Test get_ai_provider factory for configured providers."""
    # Test mock
    settings.AI_PROVIDER = "mock"
    p = get_ai_provider()
    assert isinstance(p, MockAIProvider)

    # Test gemini
    settings.AI_PROVIDER = "gemini"
    p = get_ai_provider()
    assert isinstance(p, GeminiAIProvider)

    # Test openai
    settings.AI_PROVIDER = "openai"
    p = get_ai_provider()
    assert isinstance(p, OpenAIAIProvider)

    # Test ollama
    settings.AI_PROVIDER = "ollama"
    p = get_ai_provider()
    assert isinstance(p, OllamaAIProvider)

    # Reset to default
    settings.AI_PROVIDER = "mock"
