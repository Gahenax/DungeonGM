# ⚡ Quick Start - Cripta Prototype

## 📦 Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
- ~6GB free disk space (for Ollama model)
- Modern CPU (Intel i5+, AMD Ryzen 5+)

## 🚀 Setup (5 minutes)

### 1. Clone & Navigate
```bash
git clone https://github.com/Gahenax/DungeonGM.git
cd DungeonGM
```

### 2. Start Backend Services
```bash
docker compose up -d
```

You'll see:
```
Creating cripta-ollama ... done
Creating cripta-ollama-helper ... done
Creating cripta-backend ... done
```

### 3. Wait for Ollama Model Download
First time will take ~3-5 minutes. Check progress:
```bash
docker logs cripta-ollama-helper -f
```

When you see `✅ Model pull complete!`, it's ready.

### 4. Verify Backend Health
```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","service":"cripta-backend","version":"0.1.0"}

# Test dice
curl "http://localhost:8000/dice/roll?notation=1d20+5"

# Test Ollama
curl http://localhost:11434/api/tags
```

### 5. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run tauri dev
```

Tauri window will open. Backend is running on `http://localhost:8000`.

## 🎮 Test a Game Action

### Via Browser (Quick)
```bash
# Dice roll
curl "http://localhost:8000/dice/roll?notation=2d6+2"

# Process action
curl -X POST http://localhost:8000/action \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "combat",
    "description": "I attack the goblin with my sword",
    "character_id": "hero_1"
  }'
```

### Via Swagger UI
Open: http://localhost:8000/docs

- Expand `/action` endpoint
- Click "Try it out"
- Fill in request body
- Click "Execute"

## 📊 Monitor Services

```bash
# Check running containers
docker ps

# View logs
docker logs cripta-backend -f      # Backend
docker logs cripta-ollama -f       # LLM

# Check database
sqlite3 data/campaigns.db ".tables"
```

## 🛑 Stop Services

```bash
# Stop all containers
docker compose stop

# Remove containers
docker compose down

# Remove with volumes (reset database)
docker compose down -v
```

## ⚠️ Troubleshooting

### Backend won't start
```bash
# Check logs
docker logs cripta-backend

# Rebuild image
docker compose build --no-cache cripta-backend
docker compose up -d
```

### Ollama model not loading
```bash
# Check manually
docker exec cripta-ollama ollama list
docker exec cripta-ollama ollama pull qwen2.5:1.5b
```

### Port already in use
```bash
# Change ports in docker-compose.yml:
# cripta-backend: 8001:8000
# cripta-ollama: 11435:11434
```

### High memory usage
- Ollama + model ~2-3GB
- Reduce via `OLLAMA_NUM_GPU=0` in env
- Or set `--memory-limit` in docker-compose

## 📈 Next Steps

1. Review [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)
2. Run test suite: `bash tests/test_backend.sh`
3. Build UI components in `frontend/src/pages/`
4. Add voice I/O (Whisper + Piper)
5. Deploy for QA testing
