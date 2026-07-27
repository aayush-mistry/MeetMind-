# MeetMind

**MeetMind** is an AI-powered meeting assistant that captures, summarizes, and follows up on meeting discussions. This repository contains both the backend AI agents and the modern frontend built with Vite.

## 📦 Project Structure

```tree
.
├─ backend/
│   ├─ app/
│   │   ├─ services/
│   │   │   ├─ ai/ (Multi-provider AI integrations)
│   │   ├─ main.py
│   │   ├─ models.py
│   │   ├─ extractor.py
│   │   └─ ...
│   └─ .env
├─ frontend/
│   ├─ src/
│   ├─ package.json
│   └─ vite.config.js
└─ README.md
```

- `backend/` – Fast API server, Database, and plug-and-play AI service layer.
- `frontend/` – React/Vite UI application.
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
- **Provider-Agnostic AI**: Plug and play with Groq, Gemini, OpenAI, or OpenRouter.
- Dark‑mode ready UI with smooth animations.

## 🤖 AI Configuration
The backend is completely AI-provider agnostic. Switch your AI backend instantly without modifying source code by updating `backend/.env`:

```ini
# Available options: groq, gemini, openai, openrouter
AI_PROVIDER=groq

# Corresponding API Keys
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

## 🛠️ Tech Stack

- **Frontend**: Vite, modern JavaScript, CSS (glassmorphism UI).
- **Backend**: Python AI agents, REST API.

## 🏛️ Architecture

```
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
