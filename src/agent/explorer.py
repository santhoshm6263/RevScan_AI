"""Explorer AI Agent (Spec 12 - Member 2).
Decides next action based on compact screen context and exploration history.
"""
from typing import Dict, Any, List, Optional
from src.agent.ai_provider import get_ai_provider, AIProvider
from src.agent.action_schema import validate_action
from src.agent.prompts import EXPLORATION_SYSTEM_PROMPT
from src.core.models import ActionModel


class ExplorerAgent:
    """Agent responsible for selecting actions during autonomous exploration."""

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()

    def decide(self, screen_context: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> ActionModel:
        """Decides the next action given screen context and exploration history."""
        ctx = dict(screen_context)
        if history is not None:
            ctx["previous_actions"] = history

        try:
            raw_action = self.provider.generate_action(EXPLORATION_SYSTEM_PROMPT, ctx)
            action = validate_action(raw_action)
            if action:
                return action
        except Exception as e:
            print(f"[ExplorerAgent] AI decision failed: {e}")

        # Graceful fallback (Spec 14 - Rule 8)
        return ActionModel(type="back")


explorer_agent = ExplorerAgent()
