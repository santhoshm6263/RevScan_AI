"""Exploration Orchestrator for RevScan AI (Spec 12 - Member 5).
Coordinates Android controller, AI Agent, UI Parser, Screen Analyzer, and Knowledge Generator.
"""
import logging
import threading
import time
from typing import Optional

from src.core.config import settings
from src.core.state import state_manager
from src.core.models import ScanStatusResponse, ActionModel
from src.android.adb_controller import adb_controller
from src.android.screenshot import screenshot_manager
from src.android.ui_parser import ui_parser
from src.knowledge.element_parser import element_parser
from src.knowledge.screen_analyzer import screen_analyzer
from src.knowledge.design_analyzer import design_analyzer
from src.knowledge.knowledge_pack import knowledge_generator
from src.agent.explorer import explorer_agent

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrator manages the end-to-end autonomous exploration loop."""

    def __init__(self):
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start_scan(self, package_name: str) -> bool:
        """Start autonomous scan in a background thread."""
        with self._lock:
            if self.is_running:
                return False

            self.is_running = True

            # Initialize Knowledge structures and screen analyzer
            knowledge_generator.reset()
            app_name = package_name.split(".")[-1].capitalize() if package_name else "App"
            knowledge_generator.set_app_info(name=app_name, package=package_name)
            screen_analyzer.reset()

            # Initialize scan state
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
        with self._lock:
            self.is_running = False
            state_manager.stop_scan()

    def get_status(self) -> ScanStatusResponse:
        """Get the current scan status."""
        return state_manager.get_status_response()

    def _run_loop(self, package_name: str):
        """Autonomous exploration loop (Spec 2.0 & Spec 8.0)."""
        logger.info(f"[Orchestrator] Launching autonomous exploration for '{package_name}'...")

        try:
            # 1. Wake & unlock device, then launch target app
            adb_controller.wake_and_unlock()
            adb_controller.launch_app(package_name)
            time.sleep(1.0)

            previous_screen_id: Optional[str] = None
            previous_action_str: Optional[str] = None
            step = 0

            while self.is_running and step < settings.MAX_STEPS:
                step += 1
                logger.info(f"[Orchestrator] --- Starting Step {step}/{settings.MAX_STEPS} ---")

                # Step 1: Dump UI Hierarchy XML and parse raw nodes
                xml_filename = f"hierarchy_step_{step}.xml"
                xml_path = ui_parser.dump_hierarchy(xml_filename)
                raw_nodes = ui_parser.parse_xml(xml_path) if xml_path else []

                # Step 2: Normalize UI elements
                elements = element_parser.parse_elements(raw_nodes)

                # Step 3: Capture screenshot
                screenshot_filename = f"screen_step_{step}.png"
                screenshot_path = screenshot_manager.capture_screenshot(screenshot_filename)
                rel_screenshot_path = (
                    screenshot_manager.get_relative_path(screenshot_path)
                    if screenshot_path else ""
                )

                # Step 4: Extract design system attributes
                if screenshot_path:
                    design_info = design_analyzer.analyze(screenshot_path)
                    knowledge_generator.set_design_info(design_info)

                # Step 5: Detect & classify screen (with deduplication)
                screen, is_new = screen_analyzer.analyze_or_get_screen(
                    elements=elements,
                    screenshot_path=rel_screenshot_path
                )
                knowledge_generator.add_screen(screen)

                # Step 6: Record transition if coming from another screen
                if previous_screen_id and previous_action_str and previous_screen_id != screen.id:
                    knowledge_generator.add_transition(
                        from_screen=previous_screen_id,
                        action=previous_action_str,
                        to_screen=screen.id
                    )

                if screen.id not in state_manager.visited_screens:
                    state_manager.visited_screens.append(screen.id)

                # Update live state
                state_manager.update_status(
                    status="running",
                    step=step,
                    screens_found=len(knowledge_generator.screens_map),
                    actions_executed=len(state_manager.visited_actions)
                )

                # Step 7: Build compact screen context for AI decision
                compact_elements = [e.model_dump() for e in elements]
                screen_context = {
                    "screen_id": screen.id,
                    "screen_name": screen.name,
                    "purpose": screen.purpose,
                    "elements": compact_elements,
                    "previous_actions": list(state_manager.visited_actions),
                    "app_package": package_name
                }

                # Step 8: AI Agent selects next action
                action: ActionModel = explorer_agent.decide(
                    screen_context=screen_context,
                    history=state_manager.visited_actions
                )

                logger.info(f"[Orchestrator] AI selected action: {action.model_dump()}")

                if action.type == "finish":
                    logger.info("[Orchestrator] AI Agent decided exploration is complete.")
                    break

                # Step 9: Execute action on Android device via ADB
                adb_controller.execute_action(action, elements=elements)

                # Step 10: Record executed action in Knowledge Pack and State
                knowledge_generator.add_action_to_screen(screen.id, action)
                act_repr = f"{action.type}:{action.target_id or action.direction or ''}"

                previous_screen_id = screen.id
                previous_action_str = act_repr

                state_manager.visited_actions.append(action.model_dump())
                state_manager.update_status(
                    status="running",
                    step=step,
                    screens_found=len(knowledge_generator.screens_map),
                    actions_executed=len(state_manager.visited_actions)
                )

                # UI stabilization pause
                time.sleep(1.0)

            # Exploration finished
            with self._lock:
                knowledge_generator.steps_count = len(state_manager.visited_actions)
                knowledge_generator.generate_pack()

                if self.is_running:
                    state_manager.update_status(
                        status="completed",
                        step=step,
                        screens_found=len(knowledge_generator.screens_map),
                        actions_executed=len(state_manager.visited_actions)
                    )
                else:
                    state_manager.update_status(
                        status="stopped",
                        step=step,
                        screens_found=len(knowledge_generator.screens_map),
                        actions_executed=len(state_manager.visited_actions)
                    )
                self.is_running = False

            logger.info(f"[Orchestrator] Exploration ended successfully for '{package_name}'.")

        except Exception as e:
            logger.exception(f"[Orchestrator] Error during exploration: {e}")
            with self._lock:
                self.is_running = False
                state_manager.update_status(status="error", error_message=str(e))


orchestrator = Orchestrator()
