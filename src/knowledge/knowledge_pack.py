"""Knowledge Pack generator and manager (Spec 7.0, Spec 12 - Member 3).
Compiles, manages, serializes, and restores the App Knowledge Pack.
"""
import json
import os
import threading
from typing import Dict, Any, List, Optional
from src.core.config import settings
from src.core.models import (
    KnowledgePackModel,
    ScreenModel,
    TransitionModel,
    JourneyModel,
    JourneyStep,
    ActionModel,
    AppInfo,
    ScanMeta,
    DesignInfo
)
from src.knowledge.design_analyzer import design_analyzer


class KnowledgeGenerator:
    """Compiles, manages, and exports the App Knowledge Pack."""

    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file or settings.KNOWLEDGE_PACK_FILE
        self._lock = threading.Lock()
        self.screens_map: Dict[str, ScreenModel] = {}
        self.transitions: List[TransitionModel] = []
        self.journeys: List[JourneyModel] = []
        self.app_info: AppInfo = AppInfo()
        self.design_info: DesignInfo = DesignInfo()
        self.steps_count: int = 0
        self.pack: KnowledgePackModel = KnowledgePackModel()

        # Load previous pack if it exists
        self.load()

    def reset(self):
        """Clears all in-memory knowledge structures for a fresh exploration run."""
        with self._lock:
            self.screens_map.clear()
            self.transitions.clear()
            self.journeys.clear()
            self.app_info = AppInfo()
            self.design_info = DesignInfo()
            self.steps_count = 0
            self.pack = KnowledgePackModel()

    def set_app_info(self, name: str, package: str):
        """Sets application metadata."""
        with self._lock:
            self.app_info = AppInfo(name=name, package=package)

    def set_design_info(self, design: DesignInfo):
        """Sets design system information."""
        with self._lock:
            self.design_info = design

    def add_screen(self, screen: ScreenModel):
        """Adds or updates a discovered screen."""
        with self._lock:
            if screen.id in self.screens_map:
                existing = self.screens_map[screen.id]
                # Merge actions and next_screens without duplicates
                action_set = {(a.type, a.target_id, a.text, a.direction) for a in existing.actions}
                for a in screen.actions:
                    key = (a.type, a.target_id, a.text, a.direction)
                    if key not in action_set:
                        existing.actions.append(a)
                        action_set.add(key)

                for nxt in screen.next_screens:
                    if nxt not in existing.next_screens:
                        existing.next_screens.append(nxt)

                if screen.screenshot and not existing.screenshot:
                    existing.screenshot = screen.screenshot
                if screen.elements and not existing.elements:
                    existing.elements = screen.elements
            else:
                self.screens_map[screen.id] = screen

    def add_action_to_screen(self, screen_id: str, action: ActionModel):
        """Records an action executed on a specific screen."""
        with self._lock:
            if screen_id in self.screens_map:
                screen = self.screens_map[screen_id]
                action_set = {(a.type, a.target_id, a.text, a.direction) for a in screen.actions}
                key = (action.type, action.target_id, action.text, action.direction)
                if key not in action_set:
                    screen.actions.append(action)

    def add_transition(self, from_screen: str, action: str, to_screen: str):
        """Records a transition between two screens."""
        with self._lock:
            # Check for duplicate transition
            for t in self.transitions:
                if t.from_screen == from_screen and t.action == action and t.to_screen == to_screen:
                    return

            transition = TransitionModel(**{"from": from_screen, "action": action, "to": to_screen})
            self.transitions.append(transition)

            if from_screen in self.screens_map:
                if to_screen not in self.screens_map[from_screen].next_screens:
                    self.screens_map[from_screen].next_screens.append(to_screen)

    def add_journey(self, journey: JourneyModel):
        """Adds a user journey flow."""
        with self._lock:
            self.journeys.append(journey)

    def build_journeys(self) -> List[JourneyModel]:
        """Synthesizes user journey flows automatically from discovered transitions."""
        if not self.transitions:
            return self.journeys

        journeys: List[JourneyModel] = []
        visited_edges = set()

        # Build adjacency graph
        adj: Dict[str, List[tuple]] = {}
        in_degree: Dict[str, int] = {}
        for s_id in self.screens_map:
            adj[s_id] = []
            in_degree[s_id] = 0

        for t in self.transitions:
            adj.setdefault(t.from_screen, []).append((t.to_screen, t.action))
            in_degree[t.to_screen] = in_degree.get(t.to_screen, 0) + 1
            if t.from_screen not in in_degree:
                in_degree[t.from_screen] = 0

        # Root screens are those with 0 in-degree, or fallback to first discovered screen
        root_screens = [s for s, deg in in_degree.items() if deg == 0 and s in self.screens_map]
        if not root_screens and self.screens_map:
            root_screens = [list(self.screens_map.keys())[0]]

        journey_idx = 1
        for root in root_screens:
            # Simple DFS to generate paths
            def dfs(curr: str, path: List[JourneyStep], visited: Set):
                if len(path) >= 5 or curr not in adj or not adj[curr]:
                    if len(path) > 1:
                        journeys.append(
                            JourneyModel(
                                id=f"journey_{len(journeys) + 1:03d}",
                                name=f"Flow from {self.screens_map.get(root, ScreenModel(id=root, name=root)).name}",
                                description=f"Navigation flow starting from {root}",
                                steps=list(path)
                            )
                        )
                    return

                for nxt, act in adj[curr]:
                    edge = (curr, act, nxt)
                    if edge not in visited:
                        visited.add(edge)
                        nxt_name = self.screens_map[nxt].name if nxt in self.screens_map else nxt
                        path.append(JourneyStep(screen_id=nxt, action=act, screen_name=nxt_name))
                        dfs(nxt, path, visited)
                        path.pop()

            root_name = self.screens_map[root].name if root in self.screens_map else root
            initial_step = JourneyStep(screen_id=root, action="launch", screen_name=root_name)
            from typing import Set
            dfs(root, [initial_step], set())

        # If no multi-step journeys could be built, create a single journey with all transitions
        if not journeys and self.transitions:
            steps = []
            for t in self.transitions:
                f_name = self.screens_map.get(t.from_screen, ScreenModel(id=t.from_screen, name=t.from_screen)).name
                steps.append(JourneyStep(screen_id=t.from_screen, action=t.action, screen_name=f_name))
            if steps:
                journeys.append(
                    JourneyModel(
                        id="journey_001",
                        name="Exploration Journey",
                        description="General application exploration path",
                        steps=steps
                    )
                )

        self.journeys = journeys
        return self.journeys

    def generate_pack(self) -> KnowledgePackModel:
        """Generates, serializes, and persists the Knowledge Pack JSON."""
        with self._lock:
            screens_list = list(self.screens_map.values())
            total_elements = sum(len(s.elements) for s in screens_list)

            # Auto-synthesize journeys if none registered
            if not self.journeys and self.transitions:
                self.build_journeys()

            self.pack = KnowledgePackModel(
                app=self.app_info,
                scan=ScanMeta(
                    version="1.0",
                    screens_found=len(screens_list),
                    elements_found=total_elements,
                    steps=self.steps_count
                ),
                design=self.design_info,
                screens=screens_list,
                journeys=self.journeys,
                transitions=self.transitions
            )

            self.save()
            return self.pack

    def export_ai_summary(self) -> str:
        """Generates a compact, AI-readable markdown summary of the application structure."""
        with self._lock:
            lines = [
                f"# App Knowledge Pack: {self.app_info.name} ({self.app_info.package})",
                f"- Screens Discovered: {len(self.screens_map)}",
                f"- Transitions: {len(self.transitions)}",
                f"- Theme: {self.design_info.theme} (Primary: {self.design_info.primary_color}, Background: {self.design_info.background_color})",
                "",
                "## Screens & Key Interactive Elements:"
            ]

            for s in self.screens_map.values():
                lines.append(f"### {s.name} (`{s.id}`) - {s.purpose}")
                interactive = [e for e in s.elements if e.clickable or e.input]
                if interactive:
                    for e in interactive[:10]:  # Keep compact
                        tag = "INPUT" if e.input else "BUTTON"
                        lines.append(f"  - [{tag}] `{e.id}`: \"{e.text}\"")
                if s.next_screens:
                    lines.append(f"  - Leads to: {', '.join(s.next_screens)}")
                lines.append("")

            if self.transitions:
                lines.append("## Screen Transitions:")
                for t in self.transitions:
                    lines.append(f"- `{t.from_screen}` --[{t.action}]--> `{t.to_screen}`")

            return "\n".join(lines)

    def save(self):
        """Persists the Knowledge Pack to disk."""
        try:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(self.pack.model_dump(by_alias=True), f, indent=2)
        except Exception as e:
            print(f"[KnowledgeGenerator] Error saving knowledge pack: {e}")

    def load(self) -> Optional[KnowledgePackModel]:
        """Loads Knowledge Pack from disk if it exists and restores in-memory structures."""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.pack = KnowledgePackModel(**data)

                    # Restore in-memory mappings
                    self.app_info = self.pack.app
                    self.design_info = self.pack.design
                    self.steps_count = self.pack.scan.steps
                    self.screens_map = {s.id: s for s in self.pack.screens}
                    self.transitions = list(self.pack.transitions)
                    self.journeys = list(self.pack.journeys)
                    return self.pack
            except Exception as e:
                print(f"[KnowledgeGenerator] Error loading knowledge pack from {self.output_file}: {e}")
        return None


knowledge_generator = KnowledgeGenerator()
