"""Android automation module for RevScan AI (Spec 12 - Member 1).
Provides ADB controller, screenshot manager, and UIAutomator hierarchy parser.
"""
from src.android.adb_controller import ADBController, adb_controller
from src.android.screenshot import ScreenshotManager, screenshot_manager
from src.android.ui_parser import UIParser, ui_parser

__all__ = [
    "ADBController",
    "adb_controller",
    "ScreenshotManager",
    "screenshot_manager",
    "UIParser",
    "ui_parser",
]
