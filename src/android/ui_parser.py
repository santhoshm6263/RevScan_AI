"""UIAutomator XML dump parser (Spec 12 - Member 1).
Dumps the device UI hierarchy and parses XML elements into raw node trees.
"""
import os
import re
import time
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from src.android.adb_controller import adb_controller
from src.core.config import settings


class UIParser:
    """Extracts and parses Android UI hierarchy XML."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or settings.UI_TREES_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def dump_hierarchy(self, filename: Optional[str] = None) -> Optional[str]:
        """Dumps UI hierarchy from device to local file."""
        if not filename:
            filename = f"hierarchy_{int(time.time() * 1000)}.xml"

        local_path = os.path.join(self.output_dir, filename)
        remote_path = "/sdcard/revscan_window_dump.xml"

        ok, _ = adb_controller.run_cmd(["shell", "uiautomator", "dump", remote_path])
        if not ok:
            return None

        ok, _ = adb_controller.run_cmd(["pull", remote_path, local_path])
        if not ok:
            return None

        adb_controller.run_cmd(["shell", "rm", remote_path])
        return local_path

    @staticmethod
    def parse_bounds(bounds_str: str) -> List[int]:
        """Parses bounds string '[x1,y1][x2,y2]' into [x1, y1, x2, y2]."""
        matches = re.findall(r"\[(\d+),(\d+)\]", bounds_str)
        if len(matches) == 2:
            return [int(matches[0][0]), int(matches[0][1]), int(matches[1][0]), int(matches[1][1])]
        return [0, 0, 0, 0]

    def parse_xml(self, xml_path: str) -> List[Dict[str, Any]]:
        """Parses XML file and extracts all interactive/display nodes."""
        if not os.path.exists(xml_path):
            return []

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception:
            return []

        nodes = []
        for elem in root.iter("node"):
            attrib = elem.attrib
            bounds = self.parse_bounds(attrib.get("bounds", ""))
            node_data = {
                "class": attrib.get("class", ""),
                "resource_id": attrib.get("resource-id", ""),
                "text": attrib.get("text", ""),
                "content_desc": attrib.get("content-desc", ""),
                "clickable": attrib.get("clickable", "false") == "true",
                "focusable": attrib.get("focusable", "false") == "true",
                "scrollable": attrib.get("scrollable", "false") == "true",
                "bounds": bounds,
                "package": attrib.get("package", "")
            }
            nodes.append(node_data)
        return nodes


ui_parser = UIParser()
