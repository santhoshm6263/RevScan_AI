"""UIAutomator XML dump parser (Spec 12 - Member 1).
Dumps the device UI hierarchy and parses XML elements into raw node trees
with comprehensive attribute extraction and offline fallback support.
"""
import os
import re
import time
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from src.android.adb_controller import adb_controller
from src.core.config import settings


class UIParser:
    """Extracts and parses Android UI hierarchy XML."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or settings.UI_TREES_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def dump_hierarchy(
        self,
        filename: Optional[str] = None,
        compressed: bool = True
    ) -> Optional[str]:
        """Dumps UI hierarchy from device to local file.
        Uses uiautomator dump with compressed flag by default, with automatic
        retry and offline sample fallback when no device is attached.
        """
        if not filename:
            filename = f"hierarchy_{int(time.time() * 1000)}.xml"

        local_path = os.path.join(self.output_dir, filename)
        remote_path = "/sdcard/revscan_window_dump.xml"

        if adb_controller.is_connected():
            # 1. Try uiautomator dump
            dump_cmd = ["shell", "uiautomator", "dump"]
            if compressed:
                dump_cmd.append("--compressed")
            dump_cmd.append(remote_path)

            ok, _ = adb_controller.run_cmd(dump_cmd, timeout=15)
            if not ok and compressed:
                # Fallback without --compressed flag
                ok, _ = adb_controller.run_cmd(["shell", "uiautomator", "dump", remote_path], timeout=15)

            if ok:
                # 2. Pull dump file
                pull_ok, _ = adb_controller.run_cmd(["pull", remote_path, local_path], timeout=15)
                # 3. Clean up remote temp file
                adb_controller.run_cmd(["shell", "rm", remote_path], timeout=5)

                if pull_ok and os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                    return local_path

        # Fallback: write sample hierarchy for offline testing/development
        sample_xml = self.get_sample_hierarchy_xml()
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(sample_xml)
        return local_path

    @staticmethod
    def parse_bounds(bounds_str: str) -> List[int]:
        """Parses bounds string '[x1,y1][x2,y2]' into [x1, y1, x2, y2]."""
        if not bounds_str:
            return [0, 0, 0, 0]
        matches = re.findall(r"\[(-?\d+),(-?\d+)\]", bounds_str)
        if len(matches) == 2:
            try:
                return [
                    int(matches[0][0]),
                    int(matches[0][1]),
                    int(matches[1][0]),
                    int(matches[1][1]),
                ]
            except ValueError:
                pass
        return [0, 0, 0, 0]

    def parse_xml_string(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parses XML string directly and extracts all interactive/display nodes."""
        if not xml_content or not xml_content.strip():
            return []

        try:
            root = ET.fromstring(xml_content)
        except Exception:
            return []

        nodes: List[Dict[str, Any]] = []
        for elem in root.iter("node"):
            attrib = elem.attrib
            bounds = self.parse_bounds(attrib.get("bounds", ""))
            index_str = attrib.get("index", "0")
            try:
                node_index = int(index_str)
            except ValueError:
                node_index = 0

            node_data = {
                "class": attrib.get("class", ""),
                "resource_id": attrib.get("resource-id", ""),
                "text": attrib.get("text", ""),
                "content_desc": attrib.get("content-desc", ""),
                "clickable": attrib.get("clickable", "false") == "true",
                "focusable": attrib.get("focusable", "false") == "true",
                "scrollable": attrib.get("scrollable", "false") == "true",
                "enabled": attrib.get("enabled", "true") == "true",
                "focused": attrib.get("focused", "false") == "true",
                "selected": attrib.get("selected", "false") == "true",
                "password": attrib.get("password", "false") == "true",
                "checkable": attrib.get("checkable", "false") == "true",
                "checked": attrib.get("checked", "false") == "true",
                "bounds": bounds,
                "package": attrib.get("package", ""),
                "index": node_index,
            }
            nodes.append(node_data)
        return nodes

    def parse_xml(self, xml_path: str) -> List[Dict[str, Any]]:
        """Parses XML file and extracts all interactive/display nodes."""
        if not os.path.exists(xml_path):
            return []

        try:
            with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return self.parse_xml_string(content)
        except Exception:
            return []

    @staticmethod
    def get_sample_hierarchy_xml() -> str:
        """Returns standard Android UIAutomator XML string for testing and mock mode."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.example.demo" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[0,0][1080,1920]">
    <node index="0" text="" resource-id="" class="android.widget.LinearLayout" package="com.example.demo" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[0,0][1080,1920]">
      <node index="0" text="RevScan Demo" resource-id="com.example.demo:id/title" class="android.widget.TextView" package="com.example.demo" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[50,100][1030,220]" />
      <node index="1" text="Enter Email" resource-id="com.example.demo:id/input_email" class="android.widget.EditText" package="com.example.demo" content-desc="Email field" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="true" password="false" selected="false" bounds="[100,300][980,420]" />
      <node index="2" text="Password" resource-id="com.example.demo:id/input_password" class="android.widget.EditText" package="com.example.demo" content-desc="Password field" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="true" password="true" selected="false" bounds="[100,450][980,570]" />
      <node index="3" text="Sign In" resource-id="com.example.demo:id/btn_login" class="android.widget.Button" package="com.example.demo" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[100,620][980,740]" />
      <node index="4" text="Create New Account" resource-id="com.example.demo:id/btn_register" class="android.widget.Button" package="com.example.demo" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[100,770][980,890]" />
    </node>
  </node>
</hierarchy>"""


ui_parser = UIParser()
