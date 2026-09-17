"""Knowledge Pack generator and manager (Spec 7.0, Spec 12 - Member 3)."""
import json
import os
from typing import Dict, Any, List, Optional
from src.core.config import settings
from src.core.models import (
    KnowledgePackModel,
    ScreenModel,
    TransitionModel,
    JourneyModel,
    AppInfo,
    ScanMeta,
    DesignInfo
)
from src.knowledge.design_analyzer import design_analyzer


class KnowledgeGenerator:
    """Compiles and exports App Knowledge Pack."""

    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file or settings.KNOWLEDGE_PACK_FILE
        self.pack = KnowledgePackModel()
        self.screens_map: Dict[str, ScreenModel] = {}
        self.transitions: List[TransitionModel] = []
        self.journeys: List[JourneyModel] = []
        self.app_info = AppInfo()
        self.design_info = DesignInfo()
        self.steps_count = 0

    def set_app_info(self, name: str, package: str):
        self.app_info = AppInfo(name=name, package=package)

    def add_screen(self, screen: ScreenModel):
        """Adds or updates a discovered screen."""
        self.screens_map[screen.id] = screen

    def add_transition(self, from_screen: str, action: str, to_screen: str):
        """Records a transition between two screens."""
        transition = TransitionModel(**{"from": from_screen, "action": action, "to": to_screen})
        self.transitions.append(transition)

        if from_screen in self.screens_map:
            if to_screen not in self.screens_map[from_screen].next_screens:
                self.screens_map[from_screen].next_screens.append(to_screen)

    def generate_pack(self) -> KnowledgePackModel:
        """Generates, serializes, and saves the Knowledge Pack JSON."""
        screens_list = list(self.screens_map.values())
        total_elements = sum(len(s.elements) for s in screens_list)

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

    def save(self):
        """Persists the Knowledge Pack to disk."""
        try:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(self.pack.model_dump(by_alias=True), f, indent=2)
        except Exception as e:
            print(f"[KnowledgeGenerator] Error saving knowledge pack: {e}")

    def load(self) -> Optional[KnowledgePackModel]:
        """Loads Knowledge Pack from disk if it exists."""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.pack = KnowledgePackModel(**data)
                    return self.pack
            except Exception as e:
                print(f"[KnowledgeGenerator] Error loading knowledge pack: {e}")
        return None


knowledge_generator = KnowledgeGenerator()
