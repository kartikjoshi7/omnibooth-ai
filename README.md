# OmniBooth AI

> **Smart Venue Assistant & Crowd Intelligence Platform for Physical Events**

![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)
![Angular](https://img.shields.io/badge/angular-%23DD0031.svg?style=for-the-badge&logo=angular&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)

🚀 **Live Production Demo:** [https://omnibooth-ai-828381244603.asia-south1.run.app](https://omnibooth-ai-828381244603.asia-south1.run.app)

---

## 📖 Project Overview

Managing crowd flow, wait times, and real-time coordination at large-scale physical events — stadiums, cinema halls, metro stations, and trade expos — remains a chaotic, manual process. Venue operators lack real-time intelligence, and attendees endure long queues, confusing navigation, and zero personalized guidance.

**OmniBooth AI** solves this by deploying a **Smart Venue Assistant Kiosk** at physical event venues, paired with a **Real-Time Venue Operations Dashboard** for operators. Attendees interact with the kiosk using voice commands or camera input to ask about crowd levels, wait times, navigation, and venue facilities. Behind the scenes, an **Agentic AI Pipeline** powered by Google Gemini instantly classifies query urgency, searches for live venue/event data, and generates verified, context-aware guidance — all in real time.

---

## 🎯 Chosen Vertical: Physical Event Experience

This project directly addresses the **Physical Event Experience** challenge. OmniBooth AI fundamentally enhances the physical event experience for both **attendees** and **venue operators** by:

- **For Attendees:** Deploying voice-enabled, AI-powered kiosks that provide instant answers about crowd density, wait times, venue navigation, and event schedules — eliminating the frustration of long queues and confusing venues.
- **For Operators:** Providing a real-time operations dashboard with crowd sentiment heatmaps and AI-generated action items, enabling proactive crowd management and real-time coordination.

The system bridges the gap between physical venue interactions and digital intelligence, transforming a standard physical event into an **AI-driven, highly efficient ecosystem** for crowd management and attendee satisfaction.

---

## 🏗️ System Architecture & Tech Stack

OmniBooth AI is engineered around a strict separation of concerns, operating across a serverless environment optimized for real-time crowd intelligence at scale.

```
┌──────────────────────────────────────────────────────────────────┐
│                        GOOGLE CLOUD RUN                         │
│  ┌────────────────────┐        ┌───────────────────────────┐    │
│  │   Angular Frontend │  HTTP  │      FastAPI Backend      │    │
│  │  ┌──────────────┐  │◄──────►│  ┌─────────────────────┐  │    │
│  │  │ Venue Kiosk  │  │        │  │  Agent A: Classifier │  │    │
│  │  │ (Voice/Cam)  │  │        │  │  Agent B: Verifier   │  │    │
│  │  ├──────────────┤  │        │  │  Agent C: Analyst    │  │    │
│  │  │ Ops Dashboard│  │        │  └─────────────────────┘  │    │
│  │  ├──────────────┤  │        │  ┌─────────────────────┐  │    │
│  │  │Crowd Heatmap │  │        │  │  Venue Info Base    │  │    │
│  │  └──────────────┘  │        │  └─────────────────────┘  │    │
│  └────────────────────┘        └───────────┬───────────────┘    │
│                                            │                     │
└────────────────────────────────────────────┼─────────────────────┘
                                             │
                    ┌────────────────────────┬┼────────────────────┐
                    │                        ││                    │
              ┌─────▼─────┐          ┌───────▼▼──┐         ┌──────▼──────┐
              │ MongoDB   │          │  Google   │         │  Discord    │
              │ Atlas     │          │  Gemini   │         │  Webhooks   │
              │ (Motor)   │          │  2.5 Flash│         │  (Alerts)   │
              └───────────┘          └──────────┘         └─────────────┘
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI Engine** | Google Gemini 2.5 Flash | Multi-agent reasoning for crowd intelligence and guidance |
| **Frontend** | Angular 21, TypeScript | Standalone components, Web Speech API, Camera API |
| **Backend** | Python, FastAPI, Motor | Async REST API, agentic crowd intelligence pipeline |
| **Database** | MongoDB Atlas | Attendee query storage, venue info base, analytics aggregation |
| **Secrets** | Google Cloud Secret Manager | Zero-trust credential injection for API keys |
| **Security** | CORS allowlist, Pydantic validation | Origin-locked CORS, input length constraints |
| **Logging** | Google Cloud Logging | Structured production telemetry via Cloud Logging SDK |
| **Storage** | Google Cloud Storage | Venue asset persistence (maps, crowd snapshots) |
| **Deployment** | Docker, Google Cloud Run | Multi-stage build, serverless container hosting |
| **CI/CD** | Google Cloud Build | Automated test → build → deploy pipeline |
| **Alerting** | Discord Webhooks | Real-time notifications for urgent crowd situations |

- **Google Cloud Ecosystem**: Natively integrates **Google Cloud Secret Manager** for zero-trust credential injection, **Google Cloud Logging** for structured production telemetry, **Google Cloud Storage** for venue asset management, and deployed via **Google Cloud Build/Run**.

---

## ⚡ Core Features

### Agentic AI Crowd Intelligence Pipeline
The query processing engine uses a **3-agent cascade** where each agent has a distinct role:
1. **Agent A (Classifier):** Analyzes attendee queries, classifies urgency (Hot/Warm/Cold), drafts an AI-powered guidance response, and detects if the attendee mentions a specific venue area or event.
2. **Agent C (Market Analyst):** If a specific venue area or event is mentioned, performs a live DuckDuckGo web search to gather real-time event information, schedules, and crowd reports.
3. **Agent B (Verifier):** Cross-references the AI-generated guidance against the Venue Information Base to eliminate hallucinations and ensure accurate crowd navigation advice.

### Security & Trust
- 🔒 **Zero-Trust Architecture**: No API keys, secrets, or server logic exposed to the client. All AI processing occurs server-side.
- 🔐 **CORS Allowlist**: Origins restricted to the production Cloud Run URL and localhost development servers only.
- ✅ **Input Validation**: Pydantic models enforce `min_length`/`max_length` constraints on all user-submitted text fields to prevent injection and abuse.

### Multimodal Venue Interaction
- 🎙️ **Voice Input**: Hands-free kiosk operation via the browser's native Web Speech API — attendees can ask questions naturally.
- 📷 **Camera Capture**: Live camera feed for spatial context (e.g., scanning a venue map or signage), sent to Gemini as base64 multimodal input.
- 🔊 **Text-to-Speech Output**: AI responses are spoken aloud using `SpeechSynthesis` for a fully hands-free attendee experience.

### Accessibility (WCAG 2.1 AA)
- ♿ **Semantic HTML**: Proper use of `<header>`, `<main>`, `<section>`, `<nav>` elements throughout.
- ⌨️ **Keyboard Navigation**: Skip-to-content link, visible `:focus-visible` outlines on all interactive elements.
- 🏷️ **ARIA Support**: `role`, `aria-label`, `aria-modal`, `aria-live="polite"` attributes on all dynamic content regions.
- 🎨 **Reduced Motion**: `prefers-reduced-motion` media query for users who disable animations.

### Real-Time Crowd Monitoring
- 📊 **Crowd Sentiment Heatmap**: Live dashboard with 5-second polling showing real-time query urgency distribution across a rolling 10-minute window.
- 🚨 **High-Volume Alerts**: Automatic Discord webhook notifications when urgent queries spike above threshold — enabling proactive crowd management.
- 📈 **Structured Logging**: JSON-formatted logs with timestamps, levels, and module names — fully compatible with Google Cloud Logging.

---

## 🧪 Testing

The backend includes a comprehensive **PyTest** suite with **16 tests** across 6 test classes, covering:

| Test Class | Tests | Coverage |
|-----------|-------|----------|
| `TestLeadCapture` | 4 | Success, missing notes, empty notes, cold sentiment |
| `TestGetLeads` | 2 | Empty database, populated database |
| `TestGenerateVisual` | 3 | Success, multimodal input, invalid AI response |
| `TestUploadDocs` | 2 | Success, missing text field |
| `TestAnalytics` | 1 | Returns valid list |
| `TestEdgeCases` | 4 | Oversized input, oversized docs, unknown routes, models endpoint |

All external dependencies (Gemini SDK, MongoDB) are mocked with `unittest.mock.patch`. Tests run automatically in the CI/CD pipeline via Google Cloud Build.

```bash
# Run the test suite
cd backend
pip install -r requirements.txt
pytest test_main.py -v
```

---

## 💻 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/kartikjoshi7/omnibooth-ai.git
cd omnibooth-ai
```

### 2. Backend Initialization
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory (see `.env.example` for reference):
```env
GEMINI_API_KEY="your_gemini_key_here"
MONGODB_URI="your_mongodb_atlas_connection_string"
WEBHOOK_URL="your_discord_webhook_url"
```

Start the FastAPI server:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Initialization
```bash
cd frontend
npm install
npm run start
```

Navigate to `http://localhost:4200` to access the Venue Assistant Kiosk and Operations Dashboard.

### 4. Run Tests
```bash
cd backend
pytest test_main.py -v
```

---

## 🤔 Assumptions Made

1. **Network Availability:** Assumes the venue has stable internet connectivity to reach Google Cloud Run and the Google Generative AI SDK for real-time crowd intelligence processing.
2. **Device Hardware:** Assumes the kiosk host device has a functional microphone and camera for native Web Speech API and Camera API integration.
3. **Data Privacy:** Assumes attendees consent to voice and image processing at the kiosk. No personally identifiable information (PII) is permanently stored beyond the session.
4. **Venue Scale:** The system is designed for venues handling hundreds to thousands of concurrent attendees, with MongoDB Atlas providing horizontal scalability.

---

## 🏆 Credits

This project was built for the **Hack2Skill PromptWars Hackathon** by Kartik Joshi.