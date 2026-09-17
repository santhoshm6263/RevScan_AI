"""Action schemas and validation for AI agent decisions (Spec 6.3, Spec 9)."""
import re
import json
from typing import Dict, Any, Optional, Set, Union
from src.core.models import ActionModel

ALLOWED_ACTION_TYPES = {"tap", "scroll", "type", "back", "wait", "finish"}
ALLOWED_DIRECTIONS = {"up", "down", "left", "right"}


def extract_json_from_text(raw_input: Union[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extracts a JSON object from text or dict, stripping markdown fences or commentary."""
    if isinstance(raw_input, dict):
        return raw_input

    if not isinstance(raw_input, str) or not raw_input.strip():
        return None

    text = raw_input.strip()

    # Stripping markdown ```json ... ``` blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # Find first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    return None


def validate_action(
    raw_action: Union[Dict[str, Any], str],
    valid_target_ids: Optional[Set[str]] = None
) -> Optional[ActionModel]:
    """Validates raw output into a strictly formatted ActionModel."""
    action_dict = extract_json_from_text(raw_action)
    if not action_dict or not isinstance(action_dict, dict):
        return None

    action_type = action_dict.get("type")
    if action_type not in ALLOWED_ACTION_TYPES:
        return None

    target_id = action_dict.get("target_id")

    # Validate target_id against screen elements if provided
    if valid_target_ids is not None and action_type in ("tap", "type"):
        if not target_id or target_id not in valid_target_ids:
            return None

    if action_type == "tap":
        if not target_id:
            return None
        return ActionModel(type="tap", target_id=target_id)

    elif action_type == "type":
        if not target_id:
            return None
        text = action_dict.get("text") or "test@example.com"
        return ActionModel(type="type", target_id=target_id, text=str(text))

    elif action_type == "scroll":
        direction = action_dict.get("direction", "down")
        if direction not in ALLOWED_DIRECTIONS:
            direction = "down"
        return ActionModel(type="scroll", direction=direction)

    elif action_type in ("back", "wait", "finish"):
        return ActionModel(type=action_type)

    return None

