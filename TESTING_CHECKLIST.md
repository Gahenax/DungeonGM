# 🧪 Testing Checklist - Phase de Pruebas

Usa esta lista para validar que el prototipo está **listo para QA**.

## ✅ Infrastructure

- [ ] Docker Compose levanta sin errores
- [ ] Todos los contenedores healthchecks pasan
- [ ] Backend accesible en `http://localhost:8000`
- [ ] Ollama accesible en `http://localhost:11434`
- [ ] SQLite database creada en `/data/campaigns.db`
- [ ] No errores en logs: `docker compose logs`

## ✅ Backend Health

```bash
# Test todos estos endpoints

# 1. Health check
curl http://localhost:8000/health
# Expected: {"status":"ok", ...}

# 2. Status
curl http://localhost:8000/status
# Expected: all services "ready"

# 3. Get current campaign
curl http://localhost:8000/campaign/current
# Expected: {} or campaign data

# 4. Get current character
curl http://localhost:8000/character/current
# Expected: {} or character data
```

- [ ] Todos los endpoints responden
- [ ] No hay errores 500
- [ ] Respuestas JSON válidas

## ✅ Dice Engine

```bash
# Test various notations
curl "http://localhost:8000/dice/roll?notation=1d20"
curl "http://localhost:8000/dice/roll?notation=2d6+3"
curl "http://localhost:8000/dice/roll?notation=3d8-1"
curl "http://localhost:8000/dice/roll?notation=1d100"
```

- [ ] Rolls devuelven `total` consistente
- [ ] Rolls devuelven array `rolls`
- [ ] Notación inválida retorna error 400
- [ ] Modificadores aplicados correctamente
- [ ] Límites razonables (no > 100d1000)

## ✅ Combat System

```bash
# Process combat action
curl -X POST http://localhost:8000/action \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "combat",
    "description": "I attack the goblin",
    "character_id": "test_hero"
  }'
```

- [ ] Request procesado sin error
- [ ] Respuesta contiene `narrative`
- [ ] Hit/miss generado aleatoriamente
- [ ] Daño calculado si hit=true
- [ ] Acción logueada en database

## ✅ LLM Integration (Ollama)

```bash
# Check model available
docker exec cripta-ollama ollama list
# Expected: qwen2.5:1.5b listed

# Test inference
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"qwen2.5:1.5b","prompt":"Hello","stream":false}'
```

- [ ] Model `qwen2.5:1.5b` disponible
- [ ] Inference responde en < 5 segundos
- [ ] Respuesta contiene `response` field
- [ ] Backend puede conectarse a Ollama

## ✅ Database

```bash
# Check database structure
sqlite3 data/campaigns.db ".tables"
# Expected: actions, campaigns, characters

# Check WAL mode enabled
sqlite3 data/campaigns.db "PRAGMA journal_mode;"
# Expected: wal

# Inspect schema
sqlite3 data/campaigns.db ".schema characters"
```

- [ ] Todas las tablas creadas
- [ ] WAL mode habilitado
- [ ] Schema válido
- [ ] Datos persistidos después de `docker compose stop`

## ✅ Frontend (Tauri)

```bash
cd frontend
npm run tauri dev
```

- [ ] Ventana Tauri abre sin errores
- [ ] Consola sin warnings
- [ ] Backend URL correcto (`http://localhost:8000`)
- [ ] Network requests exitosos (check DevTools)
- [ ] Ningún CORS error

## ✅ API Responses

### Valid Response Format
```json
{
  "success": true,
  "message": "Action processed",
  "game_state": {...},
  "narrative": "The goblin lunges...",
  "audio_url": null
}
```

- [ ] Respuestas consistentes
- [ ] Narrativas generadas (no vacías)
- [ ] Ningún stack traces en respuestas
- [ ] Error responses con `success: false`

## ✅ Concurrent Load

```bash
# Simular 10 requests paralelos
for i in {1..10}; do
  curl -X POST http://localhost:8000/action \
    -H "Content-Type: application/json" \
    -d '{"action_type":"combat","description":"Attack"}' &
done
wait
```

- [ ] Todos los requests completados
- [ ] Sin corrupted database
- [ ] Sin SQLite locked errors
- [ ] Todos los datos persistidos

## ✅ Performance

| Operation | Target | Status |
|-----------|--------|--------|
| Health check | < 100ms | ☐ |
| Dice roll | < 50ms | ☐ |
| Combat action | < 2s | ☐ |
| Narrative generation | < 5s | ☐ |
| Database write | < 100ms | ☐ |

```bash
# Medir tiempo
time curl "http://localhost:8000/dice/roll?notation=1d20"
```

## ✅ Error Handling

### Test Invalid Inputs
```bash
# Invalid dice notation
curl "http://localhost:8000/dice/roll?notation=invalid"
# Expected: 400 Bad Request

# Malformed JSON
curl -X POST http://localhost:8000/action \
  -H "Content-Type: application/json" \
  -d '{invalid json}'
# Expected: 422 Unprocessable Entity

# Missing fields
curl -X POST http://localhost:8000/action \
  -H "Content-Type: application/json" \
  -d '{"description":"test"}'
# Expected: 422 (missing action_type)
```

- [ ] 400 Bad Request para invalid notation
- [ ] 422 Unprocessable Entity para schema mismatch
- [ ] 503 Service Unavailable si backend down
- [ ] Mensajes de error útiles (no genéricos)

## ✅ Cleanup & Shutdown

```bash
# Clean shutdown
docker compose stop

# Verify containers stopped
docker ps | grep cripta
# Expected: empty

# Remove containers
docker compose down
```

- [ ] Sin hanging processes
- [ ] Containers stopped gracefully
- [ ] No orphaned volumes

## 📋 Summary

**Total Checks**: _____ / _____

**Status**: 
- [ ] Ready for QA ✅
- [ ] Needs fixes ⚠️
- [ ] Blocked 🚫

**Issues Found**:
1. ___________
2. ___________
3. ___________

**Notes**:
___________
