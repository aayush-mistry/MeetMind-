# MeetMind

**MeetMind** is an AI-powered meeting assistant that captures, summarizes, and follows up on meeting discussions. This repository contains both the backend AI agents and the modern frontend built with Vite.

## 📦 Project Structure

```tree
.
├─ backend/
│   ├─ app/
│   │   ├─ __init__.py
│   │   ├─ main.py
│   │   ├─ models.py
│   │   ├─ database.py
│   │   ├─ extractor.py
│   │   ├─ scheduler.py
│   │   └─ ... (other modules)
│   └─ meeting_agent.db
├─ src/
│   ├─ App.jsx
│   ├─ index.jsx
│   └─ ... (React components)
├─ index.html
├─ package.json
├─ vite.config.js
├─ README.md
└─ .gitignore
```

- `backend/` – AI agents, business logic, and API server.
- Frontend source files are at the project root (`src/` and config files).
- `README.md` – Documentation.


## 🚀 Quick Start

1. **Install frontend dependencies** (already done):
   ```bash
   npm install
   ```
2. **Start the frontend dev server**:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000/`.
3. **Start the backend server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   Backend API is reachable at `http://localhost:8000/` and WebSocket at `ws://localhost:8000/ws/meeting/demo_meeting`.
3. **Backend** – See the backend README for instructions on starting the AI agents.

## 🎯 Features

- Real‑time transcription and note‑taking.
- Automatic meeting summary generation.
- Follow‑up action item extraction.
- Dark‑mode ready UI with smooth animations.

## 🛠️ Tech Stack

- **Frontend**: Vite, modern JavaScript, CSS (glassmorphism UI).
- **Backend**: Python AI agents, REST API.

## 🏛️ Architecture

```mermaid
flowchart LR
    subgraph Frontend
        UI[UI (React components)] -->|WebSocket| WS[WebSocket Client]
        UI -->|REST| API[API Calls]
    end
    subgraph Backend
        WS -->|WS| BE[FastAPI WS Endpoint]
        API -->|HTTP| BE
        BE --> DB[(SQLite DB)]
        BE --> AI[AI Extraction Engine]
    end
    DB -->|stores| Data[Meeting Data]
    AI -->|processes| Data
```

## 📄 License

MIT License – see the [LICENSE](LICENSE) file for details.

---

*Enjoy using MeetMind for smarter, more productive meetings!*
