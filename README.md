# 🎮 CRIPTA: Virtual Dungeon Master - D&D 5.5

> A local-first, AI-powered dungeon master for solo D&D 5.5 adventures.

## 🎯 Core Features

- **📖 Tauri Desktop App**: React + TypeScript frontend
- **🤖 Local LLM Narrator**: Ollama + Qwen2.5 (1.5B parameters)
- **🎲 Deterministic Rules Engine**: D&D 5.5 combat, dice, spells
- **🗣️ Voice I/O**: Whisper (STT) + Piper (TTS) - Spanish
- **📊 Local Database**: SQLite with WAL mode for concurrency
- **🐳 Docker Compose**: Backend isolation with service mesh

## 🏗️ Architecture

```
Tauri Frontend (React + TS)
        ↓
Tauri Core (Rust Lifecycle Controller)
        ↓
Docker Compose Network
├── FastAPI Backend (Python)
│   ├── Dice Engine
│   ├── Combat Engine
│   ├── Rule Evaluator
│   └── Orchestrator
├── Ollama Server (LLM Inference)
│   └── qwen2.5:1.5b model
└── SQLite Database (Persistent)
```

## 🚀 Quick Start

### Requirements
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+ (for development)
- Rust (for Tauri building)

### Setup

```bash
# 1. Start backend services
docker compose up -d

# 2. Wait for Ollama model download (~5 min)
sleep 300

# 3. Verify backend health
curl http://localhost:8000/health

# 4. Test dice roller
curl "http://localhost:8000/dice/roll?notation=1d20+5"

# 5. Start frontend (new terminal)
cd frontend
npm install
npm run tauri dev
```

## 📋 Testing Checklist

See [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) for validation procedures.

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Fast setup guide
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Phase validation
- Backend API: `http://localhost:8000/docs` (Swagger UI)

## 🛠️ Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Testing

```bash
# Run backend health checks
bash tests/test_backend.sh

# Run pytest suite
pytest tests/pytest_tests.py -v
```

## 📄 License

MIT
