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

This project directly addresses the Physical Event Experience challenge. By deploying a Zero-Trust Multimodal Kiosk, we fundamentally enhance the Physical Event Experience for both attendees and exhibitors. The system bridges the gap between physical booth interactions and digital lead capture, transforming a standard physical event into an AI-driven, highly efficient ecosystem.

---

## 🏗️ System Architecture & Tech Stack

OmniBooth AI is engineered around a strict separation of concerns, operating across a serverless environment optimized for enterprise scalability. 

- **AI Infrastructure**: Powered by **Google Gemini 2.5 Flash** for rapid multi-agent reasoning and Multimodal processing.
- **Frontend**: Built with **Angular**, **TypeScript**, and native Web Speech APIs.
- **Backend**: Engineered in **Python** using asynchronous **FastAPI** paired with **Motor** (Async MongoDB). 
- **Deployment**: Fully Dockerized and natively hosted on **Google Cloud Run** for zero-downtime scaling.
- **Integrations**: Includes native **Discord Webhooks** for real-time alerting on high-priority leads.

---

## ⚡ Core Features

- 🔒 **Zero-Trust Security**: Strict isolation between the public-facing Kiosk UI and the Backend. Absolutely no API keys are exposed on the frontend.
- 🎙️ **Multimodal Kiosk**: Provides hands-free voice commands and audio recording capabilities. 
- 🧠 **Agentic Reasoning Loop**: A robust multi-step AI inference pipeline executed sequentially: `Classification -> Market Intelligence -> Proposal Generation`.
- 📚 **Proprietary RAG Vault**: Allows administrators to perform secure ingestion of technical specifications and manuals to rigorously anchor proposal drafting and prevent AI hallucinations.

---

## 💻 Local Setup & Installation

Follow these instructions to verify and run the stack locally.

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

Create a `.env` file in the `backend/` directory and configure the following required environment variables:
```env
GEMINI_API_KEY="your_gemini_key_here"
MONGODB_URI="your_mongodb_atlas_connection_string"
WEBHOOK_URL="your_discord_webhook_url"
```

Start the FastAPI execution loop:
```bash
python -m uvicorn main:app --reload
```

### 3. Frontend Initialization
Open a parallel terminal, ensure you have Node.js installed, and run:
```bash
cd frontend
npm install
npm run start
```
Navigate to `http://localhost:4200` to interact with the Kiosk and Exhibitor dashboards natively.

---

## 🏆 Credits

This project was built explicitly for the **Hack2Skill PromptWars Hackathon** by Kartik Joshi.