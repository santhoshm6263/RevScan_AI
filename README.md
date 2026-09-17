# RevScan AI — Autonomous Android Application Explorer

RevScan AI is an autonomous Android exploration and knowledge extraction system. It explores unfamiliar Android applications running on an emulator, maps out their UI hierarchy and screen flows, and generates a compact, structured, AI-readable **App Knowledge Pack**.

---

## 🏗 System Architecture

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

---

## 📁 Project Structure

```text
revrag-scanner/
│
├── PROJECT_SPEC.md          # Complete project specification
├── README.md                # Project documentation & setup instructions
├── requirements.txt         # Python dependencies
├── .env.example             # Configuration template
├── run.py                   # Service runner (Backend & Frontend)
│
├── src/
│   ├── core/
│   │   ├── config.py        # Settings & environment loading
│   │   ├── models.py        # Pydantic data models (Screen, Element, Action, Knowledge Pack)
│   │   ├── state.py         # State manager (scan_state.json persistence)
│   │   └── orchestrator.py  # Central exploration loop coordinator
│   │
│   ├── android/
│   │   ├── adb_controller.py# ADB connection, tap, text input, swipe, back
│   │   ├── ui_parser.py     # UIAutomator XML dump parser
│   │   └── screenshot.py    # Device screenshot capture manager
│   │
│   ├── agent/
│   │   ├── ai_provider.py   # AIProvider abstraction (Mock, OpenAI, Gemini)
│   │   ├── action_schema.py # Action schema definitions & validation
│   │   ├── prompts.py       # Autonomous exploration prompts
│   │   └── explorer.py      # Explorer decision agent
│   │
│   └── knowledge/
│       ├── element_parser.py# UI element normalization & semantic ID generation
│       ├── screen_analyzer.py# Screen signature hashing & deduplication
│       ├── design_analyzer.py# Dominant color & theme extraction
│       └── knowledge_pack.py# Knowledge Pack JSON compiler & exporter
│
├── api/
│   └── main.py              # FastAPI REST endpoints
│
├── dashboard/
│   ├── app.py               # Streamlit web dashboard
│   ├── components.py        # Reusable UI cards & API client
│   └── styles.py            # Design tokens & CSS styling system
│
├── data/
│   ├── screenshots/         # Captured screen images
│   ├── ui_trees/            # Raw UIAutomator XML dumps
│   ├── knowledge/           # knowledge-pack.json storage
│   └── scan_state.json      # Active exploration status file
│
└── tests/
    └── test_basic.py        # Data model, API contract & state tests
```

---

## 🚀 Quickstart & How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run the Services

#### Option A: Run Both Backend & Frontend (Recommended)
```bash
python run.py
```

#### Option B: Run Backend (FastAPI) Only
```bash
python run.py api
# or: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
API runs on `http://localhost:8000` (Docs: `http://localhost:8000/docs`).

#### Option C: Run Dashboard (Streamlit) Only
```bash
python run.py dashboard
# or: streamlit run dashboard/app.py
```
Dashboard runs on `http://localhost:8501`.

---

## 🧪 Running Tests
```bash
pytest
```
