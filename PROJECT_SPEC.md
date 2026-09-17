# RevScan AI — PROJECT SPEC

**Version:** 1.0
**Purpose:** AI Build Challenge — RevRag In-App Agent Track
**Team:** 5 developers
**Development time:** ~2.5 hours
**Target:** Working end-to-end prototype

---

# 1. Project Objective

Build **RevScan AI**, an autonomous Android application explorer.

The system receives an unfamiliar Android app running on an emulator and automatically:

1. Observes the current screen.
2. Reads the Android UI hierarchy.
3. Identifies interactive elements.
4. Uses AI to decide the next action.
5. Executes the action through ADB.
6. Detects newly discovered screens.
7. Records screenshots, elements, actions, and transitions.
8. Generates a compact **App Knowledge Pack**.
9. Displays the discovered app structure in a web dashboard.

### Core value proposition

> **Turn an unfamiliar Android application into a compact, structured, AI-readable App Knowledge Pack without manually recording user flows.**

---

# 2. Final User Flow

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

# 3. Technology Stack

## Backend / Automation

* Python 3.11+
* FastAPI
* ADB
* Android UIAutomator
* XML parsing
* JSON

## AI

Use a single configurable LLM/VLM provider through an abstraction:

```text
AIProvider
```

The application must not directly couple business logic to a specific AI vendor.

## Frontend

* Streamlit
* HTML/CSS only where required

## Storage

No external database for MVP.

Use:

```text
JSON files
PNG screenshots
```

## Development

* Git
* GitHub
* AI coding assistants

---

# 4. Application Architecture

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

The **Orchestrator is the only component responsible for coordinating modules.**

Modules must remain independently testable.

---

# 5. Folder Structure

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

# 6. Data Model

## 6.1 Screen

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

## 6.2 Element

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

## 6.3 Action

Allowed action types:

```text
tap
scroll
type
back
wait
finish
```

Example:

```json
{
  "type": "tap",
  "target_id": "element_001"
}
```

## 6.4 Transition

```json
{
  "from": "screen_001",
  "action": "tap:element_001",
  "to": "screen_002"
}
```

---

# 7. Knowledge Pack

The final output must be:

```text
data/knowledge/knowledge-pack.json
```

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

* JSON
* Compact
* Human-readable
* AI-readable
* Deterministic where possible
* Independent of raw UI-tree data

Raw UI trees must **not** be placed directly into the Knowledge Pack.

---

# 8. API Contracts

Base URL:

```text
http://localhost:8000
```

## Start Scan

```http
POST /scan/start
```

Request:

```json
{
  "package_name": "com.example.demo"
}
```

Response:

```json
{
  "status": "started",
  "package_name": "com.example.demo"
}
```

---

## Stop Scan

```http
POST /scan/stop
```

Response:

```json
{
  "status": "stopped"
}
```

---

## Scan Status

```http
GET /scan/status
```

Response:

```json
{
  "status": "running",
  "step": 5,
  "screens_found": 3,
  "actions_executed": 5
}
```

Allowed status values:

```text
idle
running
completed
stopped
error
```

---

## Get Screens

```http
GET /screens
```

Response:

```json
{
  "screens": [
    {
      "id": "screen_001",
      "name": "Login",
      "purpose": "User authentication"
    }
  ]
}
```

---

## Get Screen

```http
GET /screens/{screen_id}
```

Response:

```json
{
  "id": "screen_001",
  "name": "Login",
  "purpose": "User authentication",
  "screenshot": "screenshots/screen_001.png",
  "elements": []
}
```

---

## Get Knowledge Pack

```http
GET /knowledge-pack
```

Response:

```json
{
  "app": {},
  "scan": {},
  "design": {},
  "screens": [],
  "journeys": [],
  "transitions": []
}
```

---

# 9. AI Agent Contract

The AI receives a compact screen context.

Example:

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

The AI must return **only valid JSON**.

Example:

```json
{
  "type": "tap",
  "target_id": "login"
}
```

For typing:

```json
{
  "type": "type",
  "target_id": "email",
  "text": "test@example.com"
}
```

For scrolling:

```json
{
  "type": "scroll",
  "direction": "down"
}
```

For finishing:

```json
{
  "type": "finish"
}
```

---

# 10. Frontend Pages

The dashboard must contain only these pages.

## 10.1 Dashboard

Show:

* Target app
* Scan status
* Start Scan button
* Stop Scan button
* Number of screens
* Number of elements
* Number of journeys
* Number of actions

---

## 10.2 App Map

Display:

```text
Login
  ↓
Home
 ├── Products
 │     ↓
 │   Details
 │
 └── Profile
```

The map can use a simple visual representation.

No complex graph framework is required.

---

## 10.3 Screens

Display a list of discovered screens.

Clicking a screen shows:

* Screenshot
* Screen name
* Purpose
* Elements
* Actions
* Next screens
* Basic design information

---

## 10.4 Knowledge Pack

Display:

* JSON preview
* Screen count
* Element count
* Journey count
* Export/download option if simple to implement

---

# 11. Shared UI / Design Rules

All frontend code must follow the same design.

### Colors

```text
Primary:    #2563EB
Background: #F8FAFC
Surface:    #FFFFFF
Text:       #0F172A
Muted:      #64748B
Success:    #16A34A
Danger:     #DC2626
Border:     #E2E8F0
```

### Style

* Clean developer-tool appearance
* White cards
* Light background
* Rounded corners
* Consistent spacing
* Minimal shadows
* Clear hierarchy
* No unnecessary animations

### Buttons

Primary action:

```text
START AUTONOMOUS SCAN
```

Use the same primary color everywhere.

### Terminology

Always use:

```text
Scan
Screen
Element
Action
Journey
Knowledge Pack
App Map
```

Do not introduce different terminology for the same concepts.

---

# 12. Module Responsibilities

## Member 1 — Android Automation

Responsible for:

```text
ADB
Android emulator
Screenshot capture
UI hierarchy extraction
Tap
Swipe
Back
Text input
App launch
```

Owned folder:

```text
src/android/
```

---

## Member 2 — AI Explorer

Responsible for:

```text
AI provider
AI prompts
Action schema
Next-action decision
Exploration reasoning
```

Owned folder:

```text
src/agent/
```

Interface:

```python
agent.decide(screen_context, history)
```

---

## Member 3 — Knowledge Generator

Responsible for:

```text
Screen analysis
Element normalization
Screen deduplication
Design extraction
Knowledge Pack generation
```

Owned folder:

```text
src/knowledge/
```

Interface:

```python
knowledge.add_screen(observation)
knowledge.generate_pack()
```

---

## Member 4 — Dashboard

Responsible for:

```text
Dashboard
App Map
Screen viewer
Knowledge Pack viewer
UI styling
```

Owned folder:

```text
dashboard/
```

---

## Member 5 — Integration / Orchestrator

Responsible for:

```text
Exploration loop
State management
FastAPI
Module integration
Configuration
Testing
Demo reliability
```

Owned folders:

```text
src/core/
api/
```

---

# 13. File Ownership

| Member   | Allowed to modify   |
| -------- | ------------------- |
| Member 1 | `src/android/`      |
| Member 2 | `src/agent/`        |
| Member 3 | `src/knowledge/`    |
| Member 4 | `dashboard/`        |
| Member 5 | `src/core/`, `api/` |

### Shared files

These require team agreement:

```text
src/core/models.py
requirements.txt
run.py
PROJECT_SPEC.md
```

Do not modify shared contracts without informing the entire team.

---

# 14. Integration Rules

### Rule 1

The Orchestrator controls the exploration loop.

```text
Android → Orchestrator → AI → Orchestrator → Android
```

### Rule 2

The AI must never directly execute ADB commands.

Bad:

```text
AI → adb
```

Correct:

```text
AI → Action JSON → Orchestrator → Android Controller
```

### Rule 3

The Dashboard must never directly control ADB.

Correct:

```text
Dashboard → API → Orchestrator
```

### Rule 4

The AI should return semantic targets.

Use:

```json
{
  "type": "tap",
  "target_id": "login_button"
}
```

Do NOT make the AI return raw coordinates unless absolutely necessary.

### Rule 5

The Android module converts element bounds into coordinates.

```text
Element bounds
      ↓
Center point
      ↓
ADB tap
```

### Rule 6

Use JSON as the module communication format.

### Rule 7

No external database is required for MVP.

### Rule 8

The system must continue gracefully if an AI request fails.

Fallback:

```text
AI decision
   ↓ failure
Heuristic action
   ↓ failure
Scroll / Back
```

---

# 15. Exploration Rules

Maximum exploration:

```text
MAX_STEPS = 20
```

Maintain:

```text
visited_screens
visited_actions
```

Prioritize:

1. Unvisited buttons
2. Links
3. Tabs
4. Menu items
5. Input fields
6. Scroll
7. Back

Do not repeatedly perform the same action on the same screen.

Stop when:

* `MAX_STEPS` reached
* No unexplored actions remain
* AI returns `finish`

---

# 16. Screen Deduplication

The same screen must not be stored repeatedly.

Create a normalized screen signature from:

```text
screen structure
+
important UI elements
+
text
```

Example:

```text
Login screen
    ↓
normalized structure
    ↓
hash
    ↓
screen_001
```

If the same screen is encountered again, reuse its ID.

Do not depend only on screenshots because small visual differences may occur between scans.

---

# 17. Rules for AI Coding Agents

Every AI coding agent must follow these rules:

### MUST

* Read `PROJECT_SPEC.md` before coding.
* Modify only assigned folders.
* Preserve existing interfaces.
* Use the shared data models.
* Keep implementation simple.
* Write working MVP code before adding improvements.
* Handle errors without crashing the complete application.
* Use environment variables for API keys.
* Keep AI output strictly JSON.
* Test the module independently before integration.

### MUST NOT

* Rewrite another member's module.
* Change API contracts without agreement.
* Change the Knowledge Pack schema independently.
* Introduce a new framework without team approval.
* Add a database.
* Add authentication.
* Add payments.
* Add unnecessary cloud services.
* Build a second frontend.
* Replace FastAPI/Streamlit with another framework.
* Add complex AI agents or multi-agent systems.
* Hard-code API keys.
* Make the entire application dependent on one AI response succeeding.

---

# 18. Features That Must NOT Be Changed Individually

The following are **frozen project decisions**.

Individual members must NOT independently change:

```text
Project architecture
Python + FastAPI + Streamlit stack
ADB-based Android control
JSON-based storage
Knowledge Pack schema
API endpoint names
Action types
Screen/Element/Transition models
Folder ownership
UI color system
Maximum exploration strategy
Orchestrator architecture
AI semantic-action interface
```

Any change requires agreement from all team members.

---

# 19. MVP Priority

## P0 — Required

```text
ADB connection
Screenshot
UI hierarchy
AI decision
Tap
Scroll
Back
Screen detection
Screen deduplication
Knowledge Pack
Dashboard
App Map
```

## P1 — Only if P0 works

```text
Color extraction
Better journey visualization
Improved screen descriptions
Rebuild preview
```

## P2 — Do NOT build during MVP

```text
Real OTP integration
KYC
Payments
User authentication
Cloud database
Production SDK
Advanced computer vision
Complex multi-agent architecture
Mobile dashboard
```

---

# 20. Success Criteria

The prototype is considered successful if the team can demonstrate:

```text
1. Start scan
       ↓
2. Android app is automatically explored
       ↓
3. AI selects actions
       ↓
4. Actions execute without manual clicking
       ↓
5. Multiple screens are discovered
       ↓
6. Screenshots and elements are recorded
       ↓
7. Transitions are generated
       ↓
8. Knowledge Pack is generated
       ↓
9. Dashboard displays the result
```

### Final demo statement

> **RevScan AI autonomously explores an unfamiliar Android app and transforms its observed interface and behavior into a compact App Knowledge Pack that an AI agent can consume.**

---

# 21. Development Principle

> **Build the smallest complete loop first.**

The required loop is:

```text
OBSERVE
   ↓
UNDERSTAND
   ↓
DECIDE
   ↓
ACT
   ↓
RECORD
   ↓
KNOWLEDGE PACK
   ↓
VISUALIZE
```

Do not add features until this loop works end-to-end.
