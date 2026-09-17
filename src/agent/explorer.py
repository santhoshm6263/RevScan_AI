"""Explorer AI Agent (Spec 12 - Member 2).
Decides next action based on compact screen context and exploration history.
"""
import logging
from typing import Dict, Any, List, Optional, Set
from src.agent.ai_provider import get_ai_provider, AIProvider
from src.agent.action_schema import validate_action, extract_json_from_text
from src.agent.prompts import EXPLORATION_SYSTEM_PROMPT, format_screen_context_prompt
from src.core.models import ActionModel

logger = logging.getLogger(__name__)


class ExplorerAgent:
    """Agent responsible for selecting actions during autonomous exploration."""

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()

    def decide(self, screen_context: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> ActionModel:
        """Decides the next action given screen context and exploration history."""
        ctx = dict(screen_context)
        hist = history if history is not None else ctx.get("previous_actions", [])
        ctx["previous_actions"] = hist

        # Extract valid target element IDs from screen_context
        elements = ctx.get("elements", [])
        valid_target_ids: Set[str] = set()
        for elem in elements:
            if isinstance(elem, dict) and elem.get("id"):
                valid_target_ids.add(elem["id"])

        try:
            formatted_prompt = EXPLORATION_SYSTEM_PROMPT
            raw_action = self.provider.generate_action(formatted_prompt, ctx)

            # Validate generated action against allowed schema & valid element targets
            action = validate_action(raw_action, valid_target_ids=valid_target_ids if valid_target_ids else None)

            # If validation failed with strict target check, attempt loose check before falling back
            if not action:
                action = validate_action(raw_action)

            if action:
                # Detect repetitive action loop
                if self._is_looping_action(action, hist):
                    logger.info(f"[ExplorerAgent] Detected repetitive action {action}, switching to scroll/back.")
                    return ActionModel(type="scroll", direction="down")
                return action

        except Exception as e:
            logger.error(f"[ExplorerAgent] AI decision exception: {e}")

        # Fallback heuristic: tap unvisited clickable element or scroll
        fallback_action = self._fallback_action(elements, hist)
        return fallback_action

    def _is_looping_action(self, action: ActionModel, history: List[Dict[str, Any]]) -> bool:
        """Returns True if the exact same action was performed repeatedly in recent steps."""
        if not history or action.type in ("scroll", "back", "wait", "finish"):
            return False

        recent = history[-3:]
        repeat_count = 0
        for item in reversed(recent):
            if not isinstance(item, dict):
                continue
            if item.get("type") == action.type and item.get("target_id") == action.target_id:
                repeat_count += 1
            else:
                break

        return repeat_count >= 2

    def _fallback_action(self, elements: List[Dict[str, Any]], history: List[Dict[str, Any]]) -> ActionModel:
        """Generates a safe fallback action when AI decision fails or loops."""
        tapped_targets = {
            h.get("target_id") for h in history if isinstance(h, dict) and h.get("type") == "tap"
        }

        # Try to find un-tapped clickable button/element
        for elem in elements:
            if not isinstance(elem, dict):
                continue
            elem_id = elem.get("id")
            if elem_id and elem_id not in tapped_targets and elem.get("clickable", True):
                return ActionModel(type="tap", target_id=elem_id)

        # Default fallback
        if len(history) > 10:
            return ActionModel(type="finish")
        return ActionModel(type="back")


explorer_agent = ExplorerAgent()

