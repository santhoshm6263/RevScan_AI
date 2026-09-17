# RevScan AI — PROJECT SPEC
Version: 1.0
Purpose: AI Build Challenge — RevRag In-App Agent Track
Team: 5 developers
Development time: ~2.5 hours
Target: Working end-to-end prototype

---

## 1. Project Objective

Build RevScan AI, an autonomous Android application explorer.

The system receives an unfamiliar Android app running on an emulator and automatically:
1. Observes the current screen.
2. Reads the Android UI hierarchy.
3. Identifies interactive elements.
4. Uses AI to decide the next action.
5. Executes the action through ADB.
6. Detects newly discovered screens.
7. Records screenshots, elements, actions, and transitions.
8. Generates a compact App Knowledge Pack.
9. Displays the discovered app structure in a web dashboard.

### Core value proposition
> **Turn an unfamiliar Android application into a compact, structured, AI-readable App Knowledge Pack without manually recording user flows.**

---

## 2. Final User Flow

```text
User
 │
 ▼
Open RevScan AI Dashboard
 │
 ▼
Select / configure target Android app
 │
 ▼
Click "Start Autonomous Scan"
 │
 ▼
Orchestrator starts exploration
 │
 ├── Capture screenshot
 ├── Read UI hierarchy
 ├── Normalize UI elements
 ├── Detect current screen
 ├── Send compact context to AI
 ├── AI selects next action
 ├── Execute action through ADB
 └── Record result
 │
 ▼
Repeat until:
 ├── exploration limit reached
 ├── no useful actions remain
 └── app exploration is complete
 │
 ▼
Generate Knowledge Pack
 │
 ├── Screens
 ├── Elements
 ├── Actions
 ├── Transitions
 ├── Journeys
 └── Basic design information
 │
 ▼
Dashboard
 │
 ├── Overview
 ├── App Map
 ├── Screens
 └── Knowledge Pack
```

---

## 3. Technology Stack

### Backend / Automation
- Python 3.11+
- FastAPI
- ADB
- Android UIAutomator
- XML parsing
- JSON

### AI
- Use a single configurable LLM/VLM provider through an abstraction: `AIProvider`
- The application must not directly couple business logic to a specific AI vendor.

### Frontend
- Streamlit
- HTML/CSS only where required

### Storage
- No external database for MVP.
- Use: `JSON files`, `PNG screenshots`

### Development
- Git / GitHub / AI coding assistants

---

## 4. Application Architecture

```text
                    ┌──────────────────────┐
                    │      Dashboard       │
                    │      Streamlit       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Orchestrator      │
                    │  Exploration Loop    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
       │   Android   │  │  AI Agent   │  │  Knowledge   │
       │ Controller  │  │             │  │  Generator   │
       └──────┬──────┘  └─────────────┘  └───────┬──────┘
              │                                  │
              ▼                                  ▼
       Android Emulator                   Knowledge Pack
```

### Architecture rule
- The Orchestrator is the only component responsible for coordinating modules.
- Modules must remain independently testable.

---

## 5. Folder Structure

```text
revrag-scanner/
│
├── PROJECT_SPEC.md
├── README.md
├── requirements.txt
├── .env.example
├── run.py
│
├── src/
│   │
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── state.py
│   │   ├── models.py
│   │   └── config.py
│   │
│   ├── android/
│   │   ├── adb_controller.py
│   │   ├── ui_parser.py
│   │   └── screenshot.py
│   │
│   ├── agent/
│   │   ├── explorer.py
│   │   ├── ai_provider.py
│   │   ├── prompts.py
│   │   └── action_schema.py
│   │
│   └── knowledge/
│       ├── screen_analyzer.py
│       ├── element_parser.py
│       ├── design_analyzer.py
│       └── knowledge_pack.py
│
├── api/
│   └── main.py
│
├── dashboard/
│   ├── app.py
│   ├── components.py
│   └── styles.py
│
├── data/
│   ├── screenshots/
│   ├── ui_trees/
│   ├── knowledge/
│   └── scan_state.json
│
└── tests/
    └── test_basic.py
```

---

## 6. Data Model

### 6.1 Screen
```json
{
  "id": "screen_001",
  "name": "Login",
  "purpose": "User authentication",
  "screenshot": "screenshots/screen_001.png",
  "elements": [],
  "actions": [],
  "next_screens": []
}
```

### 6.2 Element
```json
{
  "id": "element_001",
  "type": "button",
  "text": "Login",
  "bounds": [100, 500, 900, 600],
  "clickable": true,
  "input": false
}
```

### 6.3 Action
Allowed action types:
`tap`, `scroll`, `type`, `back`, `wait`, `finish`

Example:
```json
{
  "type": "tap",
  "target_id": "element_001"
}
```

### 6.4 Transition
```json
{
  "from": "screen_001",
  "action": "tap:element_001",
  "to": "screen_002"
}
```

---

## 7. Knowledge Pack

The final output must be: `data/knowledge/knowledge-pack.json`

Format:
```json
{
  "app": {
    "name": "Demo App",
    "package": "com.example.demo"
  },
  "scan": {
    "version": "1.0",
    "screens_found": 0,
    "elements_found": 0,
    "steps": 0
  },
  "design": {
    "primary_color": "#2563EB",
    "background_color": "#FFFFFF",
    "theme": "light"
  },
  "screens": [],
  "journeys": [],
  "transitions": []
}
```

The Knowledge Pack must be:
- JSON
- Compact
- Human-readable
- AI-readable
- Deterministic where possible
- Independent of raw UI-tree data

Raw UI trees must not be placed directly into the Knowledge Pack.

---

## 8. API Contracts

Base URL: `http://localhost:8000`

- `POST /scan/start` -> Body: `{"package_name": "com.example.demo"}` -> Response: `{"status": "started", "package_name": "com.example.demo"}`
- `POST /scan/stop` -> Response: `{"status": "stopped"}`
- `GET /scan/status` -> Response: `{"status": "idle"|"running"|"completed"|"stopped"|"error", "step": 5, "screens_found": 3, "actions_executed": 5}`
- `GET /screens` -> Response: `{"screens": [...]}`
- `GET /screens/{screen_id}` -> Response: `{"id": "screen_001", ...}`
- `GET /knowledge-pack` -> Response: Knowledge Pack JSON

---

## 9. AI Agent Contract

The AI receives a compact screen context:
```json
{
  "screen": {
    "id": "screen_001",
    "name": "Login"
  },
  "elements": [
    {
      "id": "email",
      "type": "input",
      "text": "Email"
    },
    {
      "id": "login",
      "type": "button",
      "text": "Login"
    }
  ],
  "previous_actions": []
}
```

The AI must return only valid JSON:
- Tap: `{"type": "tap", "target_id": "login"}`
- Type: `{"type": "type", "target_id": "email", "text": "test@example.com"}`
- Scroll: `{"type": "scroll", "direction": "down"}`
- Finish: `{"type": "finish"}`

---

## 10. Frontend Pages

- **10.1 Dashboard**: Target app, scan status, start/stop buttons, counters (screens, elements, journeys, actions).
- **10.2 App Map**: Visual representation of screen hierarchy/transitions.
- **10.3 Screens**: Screen list & detail viewer (screenshot, name, purpose, elements, actions, next screens).
- **10.4 Knowledge Pack**: JSON viewer, summary statistics, download option.

---

## 11. Shared UI / Design Rules

### Colors
- Primary: `#2563EB`
- Background: `#F8FAFC`
- Surface: `#FFFFFF`
- Text: `#0F172A`
- Muted: `#64748B`
- Success: `#16A34A`
- Danger: `#DC2626`
- Border: `#E2E8F0`

### Style
- Clean developer-tool appearance
- White cards, Light background, Rounded corners, Minimal shadows
- Button primary action: `START AUTONOMOUS SCAN`

### Terminology
Always use: `Scan`, `Screen`, `Element`, `Action`, `Journey`, `Knowledge Pack`, `App Map`

---

## 12. Module Responsibilities & Ownership

- Member 1: `src/android/` (ADB, UIAutomator, Screenshot)
- Member 2: `src/agent/` (AI provider, prompts, action schema, decision)
- Member 3: `src/knowledge/` (Screen analysis, element parser, design analyzer, knowledge pack)
- Member 4: `dashboard/` (Streamlit dashboard, components, styles)
- Member 5: `src/core/`, `api/` (Orchestrator, state, models, config, API)
