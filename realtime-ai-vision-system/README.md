# Real-Time AI Vision System

A production-style real-time AI vision and object information dashboard built with a React frontend and a FastAPI backend.

## Features

- Live camera panel with dark AI dashboard styling
- Real-time object detection workflow structure
- Right-side object, confidence, and material panel
- AI question and response interface
- WebSocket-ready backend architecture
- SQLite database setup for detection history
- Environment-based configuration

## Project Structure

```text
realtime-ai-vision-system/
├── backend/
│   ├── api/
│   ├── core/
│   ├── services/
│   ├── database/
│   ├── schemas/
│   ├── utils/
│   └── main.py
├── frontend/
├── src/
├── data/
├── models/
├── tests/
├── .env.example
├── .gitignore
├── package.json
├── vite.config.js
├── index.html
└── README.md
```

## Installation

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Environment Setup

Copy `.env.example` to `.env` and configure values as needed.

## Basic API

- `GET /` -> root application check
- `GET /api/health` -> backend health status
- `GET /api/detections` -> mock detection payload

## Future Enhancements

- YOLO integration
- Material classifier integration
- WebSocket stream updates
- Full detection history persistence
- AI Q&A using image + object context
