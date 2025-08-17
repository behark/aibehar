#!/bin/bash
set -euo pipefail

echo "🎊 DIMENSIONAL AI PLATFORM - FULL STACK STARTUP"
printf '%*s\n' 60 '' | tr ' ' '='

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Resolve paths
SCRIPT_DIR="$(cd -- "$(dirname "$0")" >/dev/null 2>&1; pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"            # ai-behar
REPO_ROOT="$(cd "$PROJECT_ROOT/.." && pwd)"             # workspace root
BACKEND_MODULE="ai-behar.integrations.api_gateway.api_server:app"
WEBUI_PATH="$PROJECT_ROOT/open-webui"

# Settings (override with env vars)
PORT_BACKEND="${PORT_BACKEND:-18800}"
PORT_FRONTEND="${PORT_FRONTEND:-3000}"
FRONTEND_START="${FRONTEND_START:-1}"
# Open WebUI backend settings
PORT_WEBUI_BACKEND="${PORT_WEBUI_BACKEND:-8080}"

# Optional: autostart Ollama for local models (set OLLAMA_AUTOSTART=1)
OLLAMA_AUTOSTART="${OLLAMA_AUTOSTART:-0}"
OLLAMA_MODELS_DIR_DEFAULT="$REPO_ROOT/.ai-platform-hidden/models/ollama_models"
export OLLAMA_MODELS="${OLLAMA_MODELS:-$OLLAMA_MODELS_DIR_DEFAULT}"
export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1}"
export OLLAMA_PORT="${OLLAMA_PORT:-11434}"
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-5m}"

# Python/venv
PY="${PYTHON_EXE:-$REPO_ROOT/.venv/bin/python}"
if [ ! -x "$PY" ]; then PY=python3; fi
export PYTHONPATH="$REPO_ROOT:$PROJECT_ROOT"

echo -e "${GREEN}🚀 Starting API Gateway (uvicorn) on :$PORT_BACKEND...${NC}"
cd "$REPO_ROOT"
nohup "$PY" -m uvicorn "$BACKEND_MODULE" --host 0.0.0.0 --port "$PORT_BACKEND" --reload > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID (log: $PROJECT_ROOT/backend.log)"

# Health check loop
echo -e "${BLUE}⏳ Waiting for backend to become healthy...${NC}"
for i in {1..20}; do
    sleep 1
    if curl -sf "http://127.0.0.1:$PORT_BACKEND/api/v2/status" >/dev/null; then
        echo -e "${GREEN}✅ Backend is running and healthy${NC}"
        break
    fi
    if ! ps -p "$BACKEND_PID" >/dev/null 2>&1; then
        echo -e "${RED}❌ Backend crashed during startup${NC}"
        echo "--- tail backend.log ---"
        tail -n 120 "$PROJECT_ROOT/backend.log" || true
        exit 1
    fi
done

if ! curl -sf "http://127.0.0.1:$PORT_BACKEND/api/v2/status" >/dev/null; then
    echo -e "${RED}❌ Backend failed health check${NC}"
    tail -n 120 "$PROJECT_ROOT/backend.log" || true
    kill "$BACKEND_PID" 2>/dev/null || true
    exit 1
fi

# --- Optionally start Ollama (on-demand models) ---
if [ "$OLLAMA_AUTOSTART" = "1" ] && command -v ollama >/dev/null 2>&1; then
    echo -e "${GREEN}🤖 Ensuring Ollama is running on ${OLLAMA_HOST}:${OLLAMA_PORT}${NC}"
    OLLAMA_LISTEN="${OLLAMA_HOST}:${OLLAMA_PORT}"
    if ss -ltn "( sport = :$OLLAMA_PORT )" | grep -q LISTEN; then
        echo -e "${BLUE}ℹ️  Ollama already listening on :$OLLAMA_PORT${NC}"
    else
        echo -e "${BLUE}📦 Starting ollama serve with models dir: $OLLAMA_MODELS${NC}"
        export OLLAMA_MODELS
        nohup ollama serve --host "$OLLAMA_HOST" --port "$OLLAMA_PORT" > "$PROJECT_ROOT/ollama.log" 2>&1 &
        OLLAMA_PID=$!
        echo "Ollama PID: $OLLAMA_PID (log: $PROJECT_ROOT/ollama.log)"
        # Simple wait loop
        for i in {1..15}; do
            sleep 1
            if ss -ltn "( sport = :$OLLAMA_PORT )" | grep -q LISTEN; then
                echo -e "${GREEN}✅ Ollama is up on :$OLLAMA_PORT${NC}"
                break
            fi
        done
    fi
else
    echo -e "${CYAN}ℹ️  OLLAMA_AUTOSTART=0 or ollama not installed; skipping ollama${NC}"
fi

# --- Start Open WebUI Backend (required by frontend) ---
echo -e "${GREEN}🚀 Starting Open WebUI Backend (uvicorn) on :$PORT_WEBUI_BACKEND...${NC}"
cd "$WEBUI_PATH"

# Ensure backend package is on PYTHONPATH for local dev without install
export PYTHONPATH="$PYTHONPATH:$WEBUI_PATH/backend"

# Ensure Python deps are installed (lightweight check)
if ! "$PY" - <<'PYCHK' >/dev/null 2>&1; then
import importlib, sys
ok = True
try:
    importlib.import_module('open_webui')
except Exception:
    ok = False
sys.exit(0 if ok else 1)
PYCHK
    echo -e "${BLUE}📦 Installing Open WebUI backend dependencies (editable) ...${NC}"
    "$PY" -m pip install -U pip setuptools wheel >/dev/null 2>&1 || true
    "$PY" -m pip install -e . > "$PROJECT_ROOT/openwebui-install.log" 2>&1 || {
        echo -e "${RED}❌ Failed to install Open WebUI backend deps${NC}"
        tail -n 120 "$PROJECT_ROOT/openwebui-install.log" || true
        exit 1
    }
fi

WEBUI_PORT_ACTUAL="$PORT_WEBUI_BACKEND"
if command -v ss >/dev/null 2>&1; then
    if ss -ltn "( sport = :$WEBUI_PORT_ACTUAL )" | grep -q LISTEN; then
        for p in $(seq "$PORT_WEBUI_BACKEND" $((PORT_WEBUI_BACKEND+10))); do
            if ! ss -ltn "( sport = :$p )" | grep -q LISTEN; then WEBUI_PORT_ACTUAL="$p"; break; fi
        done
    fi
elif command -v lsof >/dev/null 2>&1; then
    if lsof -iTCP -sTCP:LISTEN -P | grep -q ":$WEBUI_PORT_ACTUAL "; then
        for p in $(seq "$PORT_WEBUI_BACKEND" $((PORT_WEBUI_BACKEND+10))); do
            if ! lsof -iTCP -sTCP:LISTEN -P | grep -q ":$p "; then WEBUI_PORT_ACTUAL="$p"; break; fi
        done
    fi
fi

nohup "$PY" -m uvicorn open_webui.main:app --host 0.0.0.0 --port "$WEBUI_PORT_ACTUAL" --forwarded-allow-ips '*' > "$PROJECT_ROOT/openwebui-backend.log" 2>&1 &
WEBUI_BACKEND_PID=$!
echo "Open WebUI Backend PID: $WEBUI_BACKEND_PID (log: $PROJECT_ROOT/openwebui-backend.log)"

# Health check loop for Open WebUI backend
echo -e "${BLUE}⏳ Waiting for Open WebUI backend to become healthy...${NC}"
for i in {1..30}; do
    sleep 1
    if curl -sf "http://127.0.0.1:$WEBUI_PORT_ACTUAL/health" >/dev/null; then
        echo -e "${GREEN}✅ Open WebUI backend is running and healthy${NC}"
        break
    fi
    if ! ps -p "$WEBUI_BACKEND_PID" >/dev/null 2>&1; then
        echo -e "${RED}❌ Open WebUI backend crashed during startup${NC}"
        echo "--- tail openwebui-backend.log ---"
        tail -n 120 "$PROJECT_ROOT/openwebui-backend.log" || true
        exit 1
    fi
done

if ! curl -sf "http://127.0.0.1:$WEBUI_PORT_ACTUAL/health" >/dev/null; then
    echo -e "${RED}❌ Open WebUI backend failed health check${NC}"
    tail -n 120 "$PROJECT_ROOT/openwebui-backend.log" || true
    kill "$WEBUI_BACKEND_PID" 2>/dev/null || true
    exit 1
fi

if [ "$FRONTEND_START" = "1" ]; then
    echo -e "${PURPLE}🌐 Starting Open WebUI Frontend...${NC}"
    cd "$WEBUI_PATH"
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}📦 Installing frontend dependencies (npm ci)...${NC}"
        npm ci --legacy-peer-deps --no-audit --no-fund || {
            echo -e "${RED}❌ npm ci failed, trying npm install --legacy-peer-deps...${NC}"
            npm install --legacy-peer-deps --no-audit --no-fund || {
                echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
                exit 1
            }
        }
    fi
    # Install known missing deps if not present
    if [ ! -d node_modules/@tiptap/suggestion ] || [ ! -d node_modules/y-protocols ]; then
        echo -e "${BLUE}📦 Installing missing packages (@tiptap/suggestion, y-protocols)...${NC}"
        npm install @tiptap/suggestion y-protocols --legacy-peer-deps --no-audit --no-fund || true
    fi
    # Pick a free port if requested one is in use
    FRONTEND_PORT_ACTUAL="$PORT_FRONTEND"
    if command -v ss >/dev/null 2>&1; then
        if ss -ltn "( sport = :$FRONTEND_PORT_ACTUAL )" | grep -q LISTEN; then
            for p in $(seq "$PORT_FRONTEND" $((PORT_FRONTEND+10))); do
                if ! ss -ltn "( sport = :$p )" | grep -q LISTEN; then FRONTEND_PORT_ACTUAL="$p"; break; fi
            done
        fi
    elif command -v lsof >/dev/null 2>&1; then
        if lsof -iTCP -sTCP:LISTEN -P | grep -q ":$FRONTEND_PORT_ACTUAL "; then
            for p in $(seq "$PORT_FRONTEND" $((PORT_FRONTEND+10))); do
                if ! lsof -iTCP -sTCP:LISTEN -P | grep -q ":$p "; then FRONTEND_PORT_ACTUAL="$p"; break; fi
            done
        fi
    fi
    echo -e "${PURPLE}🌐 Launching Vite dev server on :$FRONTEND_PORT_ACTUAL...${NC}"
    # Pass backend base URL to the frontend for flexibility (still defaults to 8080 in dev)
    export PUBLIC_WEBUI_BASE_URL="http://localhost:$WEBUI_PORT_ACTUAL"
    nohup npm run dev -- --port "$FRONTEND_PORT_ACTUAL" --host 0.0.0.0 > "$PROJECT_ROOT/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID (log: $PROJECT_ROOT/frontend.log)"
else
    FRONTEND_PID=""
    echo -e "${PURPLE}ℹ️  FRONTEND_START=0, skipping frontend${NC}"
fi

printf '%*s\n' 60 '' | tr ' ' '='
echo -e "${GREEN}🎉 PLATFORM STARTED SUCCESSFULLY!${NC}"
printf '%*s\n' 60 '' | tr ' ' '='
echo -e "${CYAN}🔗 ACCESS POINTS:${NC}"
echo -e "   ${BLUE}Backend API:${NC} http://localhost:$PORT_BACKEND"
echo -e "   ${BLUE}Open WebUI Backend:${NC} http://localhost:$WEBUI_PORT_ACTUAL"
echo -e "   ${BLUE}Ollama (if enabled):${NC} http://${OLLAMA_HOST:-127.0.0.1}:${OLLAMA_PORT:-11434}"
if [ -n "${FRONTEND_PID}" ]; then
    echo -e "   ${BLUE}Frontend UI:${NC} http://localhost:${FRONTEND_PORT_ACTUAL:-$PORT_FRONTEND}"
fi
echo -e "   ${BLUE}Health Check:${NC} http://localhost:$PORT_BACKEND/api/v2/status"
echo -e "   ${BLUE}Open WebUI Health:${NC} http://localhost:$WEBUI_PORT_ACTUAL/health"
printf '%*s\n' 60 '' | tr ' ' '='

# PIDs file
echo "$BACKEND_PID ${WEBUI_BACKEND_PID:-} ${FRONTEND_PID:-}" > "$PROJECT_ROOT/platform.pid"

cleanup() {
    echo -e "\n${PURPLE}🛑 Stopping services...${NC}"
    [ -n "${FRONTEND_PID:-}" ] && kill "$FRONTEND_PID" 2>/dev/null || true
    [ -n "${WEBUI_BACKEND_PID:-}" ] && kill "$WEBUI_BACKEND_PID" 2>/dev/null || true
    kill "$BACKEND_PID" 2>/dev/null || true
    rm -f "$PROJECT_ROOT/platform.pid"
    echo -e "${GREEN}✅ Services stopped${NC}"
}
trap cleanup INT TERM

wait "$BACKEND_PID" ${WEBUI_BACKEND_PID:-} ${FRONTEND_PID:-} || true
