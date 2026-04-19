# AI-Powered LPU Campus Treasure Hunt Platform

An interactive, AI-driven treasure hunt platform tailored for Lovely Professional University (LPU). Students interact with a beautiful chatbot UI to answer campus-specific riddles, use hints, and race against the clock to appear on the global leaderboard!

## Background
Navigating a large and complex university campus like Lovely Professional University (LPU) can be overwhelming for new students and visitors. Traditional campus maps are static and offer little engagement. To solve this, gamification techniques can be applied to transform navigation into an interactive experience. This platform replaces static mapping with a dynamic, riddle-based "Treasure Hunt" enhanced by Generative AI.

## Objectives
1. **Interactive Navigation:** Provide a dynamic, map-based web application using Leaflet.js to guide users.
2. **Generative AI Integration:** Utilize the Google Gemini 1.5 Flash API to serve as an intelligent, responsive "Tour Guide."
3. **Domain Constraint:** Apply strict Prompt Engineering to ensure the AI strictly acts as an LPU Domain Expert and refuses out-of-domain queries.
4. **Model Configuration:** Control AI output behavior by manually tuning `Temperature` and `Top-p` parameters based on the specific context of the request (factual chat vs. cryptic hints).
5. **Premium User Interface:** Offer a responsive, dark-themed UI featuring advanced CSS-coded architectural art (mimicking the LPU Admissions Block).

## Stack
- Backend: Python (Flask)
- Frontend: HTML/CSS/JS (Vanilla + Modern aesthetics, CSS Art)
- DB: JSON file database for persistent session memory
- AI: Google Gemini API (`google-generativeai`)

## Setup
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your_api_key_here"
python app.py
```
Then navigate to `http://127.0.0.1:5000` to start playing!

## Authors
- Developed for INT428: Domain-Specific Generative AI Chatbot Using APIs.
