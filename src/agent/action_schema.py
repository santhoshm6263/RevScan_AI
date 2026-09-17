"""Action schemas and validation for AI agent decisions (Spec 6.3, Spec 9)."""
from typing import Dict, Any, Optional
from src.core.models import ActionModel

ALLOWED_ACTION_TYPES = {"tap", "scroll", "type", "back", "wait", "finish"}
ALLOWED_DIRECTIONS = {"up", "down", "left", "right"}


def validate_action(action_dict: Dict[str, Any]) -> Optional[ActionModel]:
    """Validates raw dictionary into an ActionModel."""
    try:
        action_type = action_dict.get("type")
        if action_type not in ALLOWED_ACTION_TYPES:
            return None

        if action_type == "scroll" and "direction" not in action_dict:
            action_dict["direction"] = "down"

        return ActionModel(**action_dict)
    except Exception:
        return None
