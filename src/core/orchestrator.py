"""Exploration Orchestrator for RevScan AI.
Coordinates Android controller, AI Agent, and Knowledge Generator.
"""
import threading
import time
from typing import Optional
from src.core.config import settings
from src.core.state import state_manager
from src.core.models import ScanStatusResponse, KnowledgePackModel


class Orchestrator:
    """Orchestrator manages the autonomous exploration loop."""

    def __init__(self):
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

    def start_scan(self, package_name: str) -> bool:
        """Start autonomous scan in a background thread."""
        if self.is_running:
            return False

        self.is_running = True
        state_manager.start_scan(package_name)

        self._thread = threading.Thread(
            target=self._run_loop,
            args=(package_name,),
            daemon=True
        )
        self._thread.start()
        return True

    def stop_scan(self):
        """Stop the currently running scan."""
        self.is_running = False
        state_manager.stop_scan()

    def get_status(self) -> ScanStatusResponse:
        """Get the current scan status."""
        return state_manager.get_status_response()

    def _run_loop(self, package_name: str):
        """Main exploration loop stub (to be fully integrated with modules)."""
        print(f"[Orchestrator] Starting exploration loop for {package_name}...")
        try:
            step = 0
            while self.is_running and step < settings.MAX_STEPS:
                step += 1
                # 1. Observe current screen
                # 2. Extract UI hierarchy
                # 3. Analyze & detect screen
                # 4. Prompt AI for next action
                # 5. Execute action via ADB
                # 6. Record result & transition
                state_manager.update_status(
                    status="running",
                    step=step,
                    screens_found=min(step, 3),
                    actions_executed=step
                )
                time.sleep(1)

            if self.is_running:
                state_manager.update_status(status="completed")
            self.is_running = False
            print(f"[Orchestrator] Exploration ended for {package_name}")
        except Exception as e:
            print(f"[Orchestrator] Error during exploration: {e}")
            self.is_running = False
            state_manager.update_status(status="error", error_message=str(e))


orchestrator = Orchestrator()
