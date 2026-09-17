"""UI Element parser and normalizer (Spec 6.2, Spec 12 - Member 3).
Transforms raw XML nodes into clean, normalized, deduplicated ElementModel objects.
"""
import re
from typing import List, Dict, Any, Set
from src.core.models import ElementModel


class ElementParser:
    """Normalizes and sanitizes raw UI elements."""

    @staticmethod
    def classify_type(node: Dict[str, Any]) -> str:
        """Classifies the element type from Android class name and attributes."""
        cls = (node.get("class") or "").lower()
        is_clickable = bool(node.get("clickable", False))

        if any(k in cls for k in ["edittext", "textinput", "searchbox", "searchautocomplete"]):
            return "input"
        elif "checkbox" in cls:
            return "checkbox"
        elif "radio" in cls:
            return "radio"
        elif any(k in cls for k in ["switch", "togglebutton"]):
            return "switch"
        elif any(k in cls for k in ["imagebutton", "floatingactionbutton"]) or ("button" in cls):
            return "button"
        elif "imageview" in cls:
            # Clickable images in Android apps act as icon buttons (e.g. back arrow, search, overflow)
            return "button" if is_clickable else "image"
        elif "textview" in cls:
            return "button" if is_clickable else "text"
        elif any(k in cls for k in ["scrollview", "recyclerview", "listview", "gridview"]):
            return "scroll"
        elif is_clickable:
            return "button"
        return "view"

    @staticmethod
    def _sanitize_id_token(token: str) -> str:
        """Cleans a string to be a clean, URL/ID-safe token."""
        clean = re.sub(r"[^a-zA-Z0-9_]", "_", token.strip().lower())
        clean = re.sub(r"_+", "_", clean).strip("_")
        return clean[:24]

    def generate_id(self, node: Dict[str, Any], index: int, seen_ids: Set[str]) -> str:
        """Generates a stable, semantic, and unique ID for an element on a screen."""
        base_id = ""
        res_id = (node.get("resource_id") or "").strip()
        if res_id:
            if "/" in res_id:
                token = res_id.split("/")[-1]
            else:
                token = res_id
            clean_res = self._sanitize_id_token(token)
            if clean_res:
                base_id = clean_res

        if not base_id:
            text = (node.get("text") or node.get("content_desc") or "").strip()
            if text:
                clean_text = self._sanitize_id_token(text)
                if clean_text:
                    base_id = f"elem_{clean_text}"

        if not base_id:
            elem_type = self.classify_type(node)
            base_id = f"{elem_type}_{index:03d}"

        # Ensure uniqueness across the screen
        candidate = base_id
        suffix = 1
        while candidate in seen_ids:
            suffix += 1
            candidate = f"{base_id}_{suffix}"

        seen_ids.add(candidate)
        return candidate

    @staticmethod
    def is_valid_bounds(bounds: List[int]) -> bool:
        """Validates that element bounds have positive area and sensible coordinates."""
        if not bounds or len(bounds) != 4:
            return False
        x1, y1, x2, y2 = bounds
        return (x2 > x1) and (y2 > y1) and (x1 >= 0) and (y1 >= 0)

    def parse_elements(self, raw_nodes: List[Dict[str, Any]]) -> List[ElementModel]:
        """Parses a list of raw nodes into normalized ElementModels."""
        elements: List[ElementModel] = []
        seen_ids: Set[str] = set()

        for idx, node in enumerate(raw_nodes):
            is_clickable = bool(node.get("clickable", False))
            elem_type = self.classify_type(node)
            is_input = elem_type == "input"

            # Prefer text, fallback to content_desc
            text = (node.get("text") or "").strip()
            content_desc = (node.get("content_desc") or "").strip()
            display_text = text if text else content_desc

            # Filter out non-interactive, non-input empty containers
            if not is_clickable and not display_text and not is_input:
                continue

            bounds = node.get("bounds", [0, 0, 0, 0])
            if not self.is_valid_bounds(bounds):
                # If bounds are completely invalid, skip unless it's an actionable element
                if not (is_clickable or is_input):
                    continue
                bounds = [0, 0, 0, 0]

            elem_id = self.generate_id(node, idx + 1, seen_ids)
            elements.append(
                ElementModel(
                    id=elem_id,
                    type=elem_type,
                    text=display_text,
                    bounds=bounds,
                    clickable=is_clickable or (elem_type == "button"),
                    input=is_input
                )
            )

        return elements


element_parser = ElementParser()
