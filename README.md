# 🌱 PlantGuard AI

AI-powered plant disease detection with intelligent chatbot and voice responses.

## Features

- 🔍 Disease Detection (ResNet50)
- 💬 AI Chatbot (Groq)
- 🔊 Voice Responses (ElevenLabs)
- 🌤️ Weather Integration

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Environment Variables

Set these in Vercel Dashboard or `.env` file:

```
GROQ_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
WEATHER_API_KEY=your_key
```

## Deploy

```bash
vercel
```
