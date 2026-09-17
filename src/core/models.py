"""Data models for RevScan AI adhering strictly to PROJECT_SPEC.md."""
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ElementModel(BaseModel):
    """UI Element model (Spec 6.2)."""
    id: str
    type: str  # button, input, text, view, etc.
    text: str = ""
    bounds: List[int] = Field(default_factory=lambda: [0, 0, 0, 0])  # [x1, y1, x2, y2]
    clickable: bool = True
    input: bool = False


class ActionModel(BaseModel):
    """Exploration action model (Spec 6.3)."""
    type: Literal["tap", "scroll", "type", "back", "wait", "finish"]
    target_id: Optional[str] = None
    text: Optional[str] = None
    direction: Optional[Literal["up", "down", "left", "right"]] = None


class TransitionModel(BaseModel):
    """Transition between screens model (Spec 6.4)."""
    model_config = ConfigDict(populate_by_name=True)

    from_screen: str = Field(alias="from")
    action: str
    to_screen: str = Field(alias="to")


class ScreenModel(BaseModel):
    """Screen model (Spec 6.1)."""
    id: str
    name: str
    purpose: str = ""
    screenshot: str = ""
    elements: List[ElementModel] = Field(default_factory=list)
    actions: List[ActionModel] = Field(default_factory=list)
    next_screens: List[str] = Field(default_factory=list)


class JourneyStep(BaseModel):
    """A step within a user journey."""
    screen_id: str
    action: str
    screen_name: Optional[str] = None


class JourneyModel(BaseModel):
    """User Journey model."""
    id: str
    name: str
    description: str = ""
    steps: List[JourneyStep] = Field(default_factory=list)


class AppInfo(BaseModel):
    """Application metadata."""
    name: str = "Demo App"
    package: str = "com.example.demo"


class ScanMeta(BaseModel):
    """Scan execution metadata."""
    version: str = "1.0"
    screens_found: int = 0
    elements_found: int = 0
    steps: int = 0


class DesignInfo(BaseModel):
    """Basic design system info."""
    primary_color: str = "#2563EB"
    background_color: str = "#FFFFFF"
    theme: str = "light"


class KnowledgePackModel(BaseModel):
    """App Knowledge Pack model (Spec 7.0)."""
    app: AppInfo = Field(default_factory=AppInfo)
    scan: ScanMeta = Field(default_factory=ScanMeta)
    design: DesignInfo = Field(default_factory=DesignInfo)
    screens: List[ScreenModel] = Field(default_factory=list)
    journeys: List[JourneyModel] = Field(default_factory=list)
    transitions: List[TransitionModel] = Field(default_factory=list)


# API Models (Spec 8.0)
class StartScanRequest(BaseModel):
    package_name: str


class StartScanResponse(BaseModel):
    status: str = "started"
    package_name: str


class StopScanResponse(BaseModel):
    status: str = "stopped"


class ScanStatusResponse(BaseModel):
    status: Literal["idle", "running", "completed", "stopped", "error"]
    step: int = 0
    screens_found: int = 0
    actions_executed: int = 0


class ScreenSummary(BaseModel):
    id: str
    name: str
    purpose: str


class ScreensResponse(BaseModel):
    screens: List[ScreenSummary]
