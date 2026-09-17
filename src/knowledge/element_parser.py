"""UI Element parser and normalizer (Spec 12 - Member 3).
Transforms raw XML nodes into clean, normalized ElementModel objects.
"""
from typing import List, Dict, Any
from src.core.models import ElementModel


class ElementParser:
    """Normalizes raw UI elements."""

    @staticmethod
    def classify_type(node: Dict[str, Any]) -> str:
        """Classifies the element type from Android class name and attributes."""
        cls = node.get("class", "").lower()
        if "edittext" in cls or "textinput" in cls:
            return "input"
        elif "button" in cls or "imagebutton" in cls:
            return "button"
        elif "imageview" in cls:
            return "image"
        elif "textview" in cls:
            return "text"
        elif "checkbox" in cls:
            return "checkbox"
        elif "switch" in cls:
            return "switch"
        elif "radio" in cls:
            return "radio"
        return "view"

    @staticmethod
    def generate_id(node: Dict[str, Any], index: int) -> str:
        """Generates a stable semantic ID for an element."""
        res_id = node.get("resource_id", "")
        if res_id and "/" in res_id:
            return res_id.split("/")[-1]
        text = node.get("text", "").strip()
        if text:
            clean_text = "".join(c for c in text.lower() if c.isalnum() or c == "_")[:20]
            if clean_text:
                return f"elem_{clean_text}_{index}"
        return f"element_{index:03d}"

    def parse_elements(self, raw_nodes: List[Dict[str, Any]]) -> List[ElementModel]:
        """Parses a list of raw nodes into normalized ElementModels."""
        elements = []
        for idx, node in enumerate(raw_nodes):
            # Only include interactive or meaningful visible content
            is_clickable = node.get("clickable", False)
            text = (node.get("text") or node.get("content_desc") or "").strip()
            elem_type = self.classify_type(node)
            is_input = elem_type == "input"

            # Filter out non-interactive empty containers
            if not is_clickable and not text and not is_input:
                continue

            elem_id = self.generate_id(node, idx + 1)
            elements.append(
                ElementModel(
                    id=elem_id,
                    type=elem_type,
                    text=text,
                    bounds=node.get("bounds", [0, 0, 0, 0]),
                    clickable=is_clickable,
                    input=is_input
                )
            )
        return elements


element_parser = ElementParser()
