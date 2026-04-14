# OmniBooth AI - Zero-Trust Sales Intelligence

## 1. Chosen Vertical
B2B Sales / Enterprise Trade Show Automation

## 2. Approach and Logic
Our objective was to solve the "Enterprise IP Leak" problem at trade shows while gamifying the attendee experience. We built a multimodal, multi-agent architecture using FastAPI and Angular. 
The logic is split into two interfaces:
* **The Kiosk (Attendee Facing):** Uses native HTML5 Web Speech (Voice-to-Voice) to allow users to interact hands-free with the AI, generating real-time technical contextual responses.
* **The Dashboard (Exhibitor Facing):** A secure RAG (Retrieval-Augmented Generation) pipeline that ingests proprietary company data. We implemented an Agentic Critic Loop that automatically routes leads, scrapes the live internet for competitor analysis, and drafts verified sales proposals.

## 3. How the Solution Works
1.  **Ingestion:** Exhibitors upload proprietary technical specs into the MongoDB Knowledge Vault (RAG).
2.  **Interaction:** Attendees use the Voice-to-Voice Kiosk to ask complex engineering questions.
3.  **Agentic Analysis:** Exhibitors input messy conversation notes into the Dashboard. 
    * *Agent A* categorizes lead temperature.
    * *Agent C* (if a competitor is mentioned) live-searches the internet to build a Battle Card.
    * *Agent B* cross-references the notes with the RAG vault and the web scrape to generate a highly accurate, verified email draft and action items.
4.  **Alerting:** If a lead is categorized as "Hot," a Python asynchronous webhook instantly fires a Discord notification to the sales team.

## 4. Assumptions Made
* Exhibitors require high fault-tolerance; therefore, strict `try/except` fallbacks were implemented for all third-party APIs (e.g., DuckDuckGo search limits).
* Attendees in noisy trade show environments may prefer voice input over typing, prompting the HTML5 Speech API integration.