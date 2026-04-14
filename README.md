# OmniBooth AI

> **Zero-Trust Multimodal Sales Intelligence & Lead Engineering Kiosk**

![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)
![Angular](https://img.shields.io/badge/angular-%23DD0031.svg?style=for-the-badge&logo=angular&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)

🚀 **Live Production Demo:** [https://omnibooth-ai-828381244603.asia-south1.run.app](https://omnibooth-ai-828381244603.asia-south1.run.app)

---

## 📖 Project Overview

In the modern enterprise ecosystem, traditional trade show lead capture is slow, manual, and highly prone to error. Sales engineers waste countless hours deciphering scribbled notes and piecing together disparate product specs instead of closing deals.

**OmniBooth AI** fundamentally solves this bottleneck by deploying a public-facing, voice-enabled *'JARVIS-style'* Kiosk for booth attendees, which is seamlessly linked to a secure Exhibitor Dashboard. By leveraging a custom **Agentic AI Loop**, OmniBooth instantly qualifies leads as they speak, automatically searches the web for live competitor data, and drafts highly technical, context-aware sales emails—all before the attendee even leaves the booth.

---

## 🎯 Hackathon Problem Statement Alignment

This project directly addresses the **Physical Event Experience** challenge. By deploying a Zero-Trust Multimodal Kiosk, we fundamentally enhance the Physical Event Experience for both attendees and exhibitors. The system bridges the gap between physical booth interactions and digital lead capture, transforming a standard physical event into an AI-driven ecosystem.

---

## 🏗️ System Architecture & Tech Stack

OmniBooth AI is engineered around a strict separation of concerns, operating across a serverless environment optimized for enterprise scalability.

```
┌──────────────────────────────────────────────────────────────────┐
│                        GOOGLE CLOUD RUN                         │
│  ┌────────────────────┐        ┌───────────────────────────┐    │
│  │   Angular Frontend │  HTTP  │      FastAPI Backend      │    │
│  │  ┌──────────────┐  │◄──────►│  ┌─────────────────────┐  │    │
│  │  │ Kiosk Mode   │  │        │  │  Agent A: Writer     │  │    │
│  │  │ (Voice/Cam)  │  │        │  │  Agent B: Engineer   │  │    │
│  │  ├──────────────┤  │        │  │  Agent C: Analyst    │  │    │
│  │  │ CRM Dashboard│  │        │  └─────────────────────┘  │    │
│  │  ├──────────────┤  │        │  ┌─────────────────────┐  │    │
│  │  │ Vibe Heatmap │  │        │  │  RAG Knowledge Vault│  │    │
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
| **AI Engine** | Google Gemini 2.5 Flash | Multi-agent reasoning, multimodal processing |
| **Frontend** | Angular 21, TypeScript | Standalone components, Web Speech API, Camera API |
| **Backend** | Python, FastAPI, Motor | Async REST API, agentic pipeline orchestration |
| **Database** | MongoDB Atlas | Lead storage, RAG knowledge vault, analytics aggregation |
| **Security** | SlowAPI, CORS allowlist | Rate limiting (5 req/min), origin-locked CORS |
| **Logging** | Python `logging` (JSON) | Structured logs compatible with Google Cloud Logging |
| **Deployment** | Docker, Google Cloud Run | Multi-stage build, serverless container hosting |
| **CI/CD** | Google Cloud Build | Automated build → push → deploy pipeline |
| **Alerting** | Discord Webhooks | Real-time "Hot Lead" notifications via async `httpx` |

---

## ⚡ Core Features

### Agentic AI Pipeline
The lead processing engine uses a **3-agent cascade** where each agent has a distinct role:
1. **Agent A (Writer):** Classifies lead intent (Hot/Warm/Cold), drafts a technical proposal email, and detects competitor mentions.
2. **Agent C (Market Analyst):** If a competitor is detected, performs a live DuckDuckGo web search to gather specifications and weaknesses.
3. **Agent B (Engineer):** Cross-references the draft against the RAG Knowledge Vault to eliminate hallucinations, then appends data-driven competitive battle cards.

### Security & Trust
- 🔒 **Zero-Trust Architecture**: No API keys, secrets, or server logic exposed to the client. All AI processing occurs server-side.
- 🛡️ **Rate Limiting**: All mutation endpoints are protected by `slowapi` (5 requests/minute on `/capture-lead` and `/upload-docs`).
- 🔐 **CORS Allowlist**: Origins restricted to the production Cloud Run URL and localhost development servers only.
- ✅ **Input Validation**: Pydantic models enforce `min_length`/`max_length` constraints on all user-submitted text fields.

### Multimodal Interaction
- 🎙️ **Voice Input**: Hands-free operation via the browser's native Web Speech API with auto-generate on speech end.
- 📷 **Camera Capture**: Live camera feed for spatial reference imagery, sent to Gemini as base64 multimodal input.
- 🔊 **Text-to-Speech Output**: AI responses are spoken aloud using `SpeechSynthesis` with preferred voice selection.

### Accessibility (WCAG 2.1 AA)
- ♿ **Semantic HTML**: Proper use of `<header>`, `<main>`, `<section>`, `<nav>` elements throughout.
- ⌨️ **Keyboard Navigation**: Skip-to-content link, visible `:focus-visible` outlines on all interactive elements.
- 🏷️ **ARIA Support**: `role`, `aria-label`, `aria-modal`, `aria-live="polite"` attributes on all dynamic content regions.

### Observability
- 📊 **Structured Logging**: JSON-formatted logs with timestamps, levels, and module names — compatible with Google Cloud Logging ingestion.
- 📈 **Real-Time Analytics**: Live Vibe Heatmap dashboard with 5-second polling and MongoDB aggregation over a rolling 10-minute window.

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

All external dependencies (Gemini SDK, MongoDB) are mocked with `unittest.mock.patch`.

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

Navigate to `http://localhost:4200` to access the Kiosk and Exhibitor Dashboard.

### 4. Run Tests
```bash
cd backend
pytest test_main.py -v
```

---

## 🤔 Assumptions Made

1. **Network Availability:** Assumes the venue has stable internet to reach Google Cloud Run and the Google Generative AI SDK.
2. **Device Hardware:** Assumes the Kiosk host device has a functional microphone for native Web Speech API integration.
3. **Data Privacy:** Assumes attendees consent to voice-processing, as no PII is permanently stored.

---

## 🏆 Credits

This project was built for the **Hack2Skill PromptWars Hackathon** by Kartik Joshi.