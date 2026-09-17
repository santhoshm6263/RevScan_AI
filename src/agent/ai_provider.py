"""AI Provider abstraction for RevScan AI (Spec 3, Spec 12 - Member 2).
Decouples LLM/VLM vendor specifics from exploration business logic.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
from src.core.config import settings


class AIProvider(ABC):
    """Abstract interface for AI Providers."""

    @abstractmethod
    def generate_action(self, prompt: str, screen_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a next-action JSON from screen context."""
        pass


class MockAIProvider(AIProvider):
    """Deterministic Mock AI Provider for testing and local development."""

    def generate_action(self, prompt: str, screen_context: Dict[str, Any]) -> Dict[str, Any]:
        elements = screen_context.get("elements", [])
        prev_actions = screen_context.get("previous_actions", [])

        # Find first clickable element not yet tapped
        tapped_targets = {
            a.get("target_id") for a in prev_actions if a.get("type") == "tap"
        }

        for elem in elements:
            elem_id = elem.get("id")
            elem_type = elem.get("type")
            if elem_id not in tapped_targets:
                if elem_type == "input":
                    return {
                        "type": "type",
                        "target_id": elem_id,
                        "text": "test@example.com"
                    }
                elif elem.get("clickable", True):
                    return {
                        "type": "tap",
                        "target_id": elem_id
                    }

        # If no unvisited clickable element found, scroll or finish
        if len(prev_actions) > 5:
            return {"type": "finish"}
        return {"type": "scroll", "direction": "down"}


def get_ai_provider() -> AIProvider:
    """Factory to retrieve configured AI Provider."""
    provider_name = settings.AI_PROVIDER.lower()
    if provider_name == "mock":
        return MockAIProvider()
    # Default fallback to Mock
    return MockAIProvider()
