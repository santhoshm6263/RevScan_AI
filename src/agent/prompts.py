"""System prompts for AI exploration agent (Spec 9, Spec 12 - Member 2)."""
import json
from typing import Dict, Any

EXPLORATION_SYSTEM_PROMPT = """You are RevScan AI, an autonomous Android exploration agent.
Your objective is to explore an Android application screen by screen to build a complete App Knowledge Pack.

Rules:
1. You will receive the current screen context and previous actions.
2. Select the next most productive action to discover new screens or interactive functionality.
3. Prioritize unexplored buttons, tabs, links, and input forms.
4. Do not repeat actions already performed on the current screen.
5. You must respond with ONLY a single valid JSON object matching the action schema. No explanations, no markdown formatting, just pure JSON.

Allowed actions:
- Tap: {"type": "tap", "target_id": "<element_id>"}
- Type: {"type": "type", "target_id": "<element_id>", "text": "<text_to_type>"}
- Scroll: {"type": "scroll", "direction": "down|up|left|right"}
- Back: {"type": "back"}
- Wait: {"type": "wait"}
- Finish: {"type": "finish"}
"""


def format_screen_context_prompt(screen_context: Dict[str, Any]) -> str:
    """Formats compact screen context for LLM prompt strictly according to Spec 9."""
    screen_info = screen_context.get("screen", {})
    if isinstance(screen_info, str):
        screen_info = {"id": screen_info, "name": screen_info}

    elements = screen_context.get("elements", [])
    formatted_elements = []
    for elem in elements:
        if isinstance(elem, dict):
            formatted_elements.append({
                "id": elem.get("id", ""),
                "type": elem.get("type", "view"),
                "text": elem.get("text", ""),
                "clickable": elem.get("clickable", True),
                "input": elem.get("input", False)
            })

    prev_actions = screen_context.get("previous_actions", [])

    compact_context = {
        "screen": {
            "id": screen_info.get("id", "unknown_screen"),
            "name": screen_info.get("name", "Unknown")
        },
        "elements": formatted_elements,
        "previous_actions": prev_actions
    }
    return json.dumps(compact_context, indent=2)

