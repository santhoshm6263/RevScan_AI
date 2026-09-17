"""State management for RevScan AI."""
import json
import os
import threading
from typing import Dict, Any, Optional
from src.core.config import settings
from src.core.models import ScanStatusResponse


class StateManager:
    """Manages the in-memory and persistent state of the active scan."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(StateManager, cls).__new__(cls)
                    cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.state_file = settings.SCAN_STATE_FILE
        self.status = "idle"
        self.package_name = ""
        self.step = 0
        self.screens_found = 0
        self.actions_executed = 0
        self.visited_screens = []
        self.visited_actions = []
        self.error_message = None
        self._mutex = threading.Lock()
        self.load()

    def update_status(self, status: str, step: Optional[int] = None,
                      screens_found: Optional[int] = None,
                      actions_executed: Optional[int] = None,
                      error_message: Optional[str] = None):
        with self._mutex:
            self.status = status
            if step is not None:
                self.step = step
            if screens_found is not None:
                self.screens_found = screens_found
            if actions_executed is not None:
                self.actions_executed = actions_executed
            if error_message is not None:
                self.error_message = error_message
            self.save()

    def start_scan(self, package_name: str):
        with self._mutex:
            self.package_name = package_name
            self.status = "running"
            self.step = 0
            self.screens_found = 0
            self.actions_executed = 0
            self.visited_screens = []
            self.visited_actions = []
            self.error_message = None
            self.save()

    def stop_scan(self):
        with self._mutex:
            self.status = "stopped"
            self.save()

    def get_status_response(self) -> ScanStatusResponse:
        with self._mutex:
            return ScanStatusResponse(
                status=self.status,
                step=self.step,
                screens_found=self.screens_found,
                actions_executed=self.actions_executed
            )

    def to_dict(self) -> Dict[str, Any]:
        with self._mutex:
            return {
                "status": self.status,
                "package_name": self.package_name,
                "step": self.step,
                "screens_found": self.screens_found,
                "actions_executed": self.actions_executed,
                "visited_screens": self.visited_screens,
                "visited_actions": self.visited_actions,
                "error_message": self.error_message
            }

    def save(self):
        try:
            data = {
                "status": self.status,
                "package_name": self.package_name,
                "step": self.step,
                "screens_found": self.screens_found,
                "actions_executed": self.actions_executed,
                "visited_screens": self.visited_screens,
                "visited_actions": self.visited_actions,
                "error_message": self.error_message
            }
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[StateManager] Failed to save scan state: {e}")

    def load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.status = data.get("status", "idle")
                    self.package_name = data.get("package_name", "")
                    self.step = data.get("step", 0)
                    self.screens_found = data.get("screens_found", 0)
                    self.actions_executed = data.get("actions_executed", 0)
                    self.visited_screens = data.get("visited_screens", [])
                    self.visited_actions = data.get("visited_actions", [])
                    self.error_message = data.get("error_message")
            except Exception as e:
                print(f"[StateManager] Failed to load scan state: {e}")


state_manager = StateManager()
