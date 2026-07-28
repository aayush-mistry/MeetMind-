# 🎙️ MeetMind

## AI-Powered Meeting Intelligence Platform

Transform meetings into actionable insights with AI-powered transcription, translation, summaries, speaker analytics, and professional meeting minutes.

![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![AI](https://img.shields.io/badge/AI-Multi%20Provider-blueviolet)
![License](https://img.shields.io/badge/License-MIT-success)

**🎤 Record • 📤 Upload • 🤖 Analyze • 📄 Summarize • 📊 Organize**

---

# 📖 About MeetMind

**MeetMind** is an AI-powered meeting assistant designed to simplify the way teams capture, organize, and understand meetings.

Instead of manually taking notes, MeetMind automatically converts meeting audio or video into structured knowledge by generating transcripts, summaries, action items, meeting minutes, and AI-powered insights.

Whether you're attending a live meeting, uploading a recording, or reviewing previous discussions, MeetMind provides everything in one intelligent workspace.

---

# ✨ Features

## 🎙️ Meeting Capture

- 🎤 Live Meeting Recording
- 🎧 Browser Audio Recording
- 📤 Upload Audio Files
- 🎥 Upload Video Files
- 🔄 Real-Time WebSocket Updates

---

## 🤖 AI Meeting Intelligence

- 📝 AI Meeting Summary
- ✅ Action Item Extraction
- 📌 Decision Detection
- ⚠️ Risk & Blocker Detection
- ❓ Question Extraction
- 💡 AI Meeting Insights

---

## 🌍 Language Intelligence

- 🌐 Automatic Language Detection
- 🔄 English Translation
- 🗣️ Multilingual Meeting Support

---

## 👥 Speaker Analytics

- Speaker Identification
- Speaker Timeline
- Speaking Time Analysis
- Speaker Contribution Statistics
- Speaker Renaming

---

## 📄 AI Meeting Minutes (MoM)

Generate professional meeting documentation including:

- Executive Summary
- Agenda
- Key Discussions
- Decisions
- Action Items
- Deadlines
- Risks
- Next Meeting

Export Formats:

- PDF
- DOCX
- Markdown
- TXT

---

## 📅 Productivity

- Meeting History
- Calendar Integration
- AI Chat Assistant
- Analytics Dashboard
- Search Meetings
- Dark Mode

---

# 🚀 AI Workflow

```text
Meeting Audio / Video
            │
            ▼
Speech-to-Text Engine
            │
            ▼
Language Detection
            │
            ▼
English Translation
            │
            ▼
AI Analysis
            │
            ├── Summary
            ├── Action Items
            ├── Decisions
            ├── Risks
            ├── Questions
            └── Meeting Minutes
            │
            ▼
Meeting Database
            │
            ▼
History • AI Chat • Analytics
```

---

# 🏗️ Project Structure

```text
MeetMind
│
├── backend
│   ├── app
│   │   ├── services
│   │   │   ├── ai
│   │   │   │   ├── base_provider.py
│   │   │   │   ├── provider_factory.py
│   │   │   │   ├── groq_provider.py
│   │   │   │   ├── gemini_provider.py
│   │   │   │   ├── openrouter_provider.py
│   │   │   │   └── openai_provider.py
│   │   ├── routes
│   │   ├── models.py
│   │   ├── extractor.py
│   │   ├── scheduler.py
│   │   └── main.py
│   └── .env
│
├── frontend
│   ├── src
│   ├── public
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

# ⚙️ Tech Stack

| Category | Technology |
|----------|------------|
| Frontend | React + Vite |
| Backend | FastAPI |
| Database | SQLite |
| AI Providers | Groq, Gemini, OpenAI, OpenRouter |
| Speech-to-Text | Whisper |
| Translation | Google Translate / AI Translation |
| Communication | REST API + WebSockets |
| Styling | Glassmorphism UI + CSS |

---

# 🤖 AI Provider Support

MeetMind uses a **plug-and-play AI architecture**.

Switch AI providers without modifying application code.

Update your `.env` file:

```env
AI_PROVIDER=groq

GROQ_API_KEY=your_api_key

GEMINI_API_KEY=your_api_key

OPENAI_API_KEY=your_api_key

OPENROUTER_API_KEY=your_api_key
```

Supported Providers:

- ✅ Groq
- ✅ Gemini
- ✅ OpenAI
- ✅ OpenRouter

---

# 🚀 Getting Started

## Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/MeetMind.git

cd MeetMind
```

---

## Install Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```
http://localhost:3000
```

---

## Start Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend:

```
http://localhost:8000
```

WebSocket:

```
ws://localhost:8000/ws/meeting/demo_meeting
```

---

# 📊 System Architecture

```text
                    User
                      │
                      ▼
               React Frontend
                      │
         REST API & WebSocket
                      │
                      ▼
              FastAPI Backend
                      │
     ┌────────────────┼────────────────┐
     ▼                ▼                ▼
 Speech Engine   AI Provider      Database
 (Whisper)    (Groq/Gemini/etc.)  (SQLite)
     │                │
     └────────────┬───┘
                  ▼
          AI Meeting Analysis
                  │
                  ▼
 Summary • Minutes • Action Items • History
```

---

# 📸 Screenshots

> Replace these placeholders with your application screenshots.

| Dashboard | Live Meeting |
|-----------|--------------|
| *(Add Screenshot)* | *(Add Screenshot)* |

| Meeting Summary | AI Chat |
|----------------|---------|
| *(Add Screenshot)* | *(Add Screenshot)* |

| Calendar | Meeting Minutes |
|-----------|----------------|
| *(Add Screenshot)* | *(Add Screenshot)* |

---

# 🛣️ Roadmap

## ✅ Completed

- Live Meeting Recording
- Audio Upload
- Video Upload
- AI Meeting Summary
- Action Item Extraction
- Meeting History
- AI Chat
- Dark Mode
- Multi-Provider AI Support

## 🚧 In Progress

- Google Calendar Integration
- Outlook Calendar Integration
- Speaker Recognition
- Meeting Notifications

## 🔮 Planned

- Semantic Search
- Slack Integration
- Microsoft Teams Integration
- Zoom Integration
- AI Meeting Coach
- Team Workspaces
- Role-Based Access Control
- Cloud Storage Support

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a new branch.

```bash
git checkout -b feature/new-feature
```

3. Commit your changes.

```bash
git commit -m "feat: add new feature"
```

4. Push your branch.

```bash
git push origin feature/new-feature
```

5. Open a Pull Request.

---

# 📄 License

This project is licensed under the **MIT License**.

See the **LICENSE** file for more information.

---

# ⭐ Support

If you found **MeetMind** useful, consider giving this repository a **Star ⭐**.

Your support helps improve the project and motivates future development.

---

**Made with ❤️ using React, FastAPI, Python, and AI**