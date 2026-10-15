#!/bin/bash
# Start both servers with one command:  ./start.sh
#   bridge :8378 (model API) + app :8000 (UI + API)
cd "$(dirname "$0")"
# clear any stale servers first so the new code actually loads
pkill -f "uvicorn src.opencode_bridge" 2>/dev/null
pkill -f "uvicorn webapp.backend.app" 2>/dev/null
sleep 3
mkdir -p /tmp/opencode
# drop stale root-owned logs from sudo runs so non-sudo starts can write
rm -f /tmp/opencode/bridge.log /tmp/opencode/app.log 2>/dev/null
.venv/bin/uvicorn src.opencode_bridge:app --port 8378 &>/tmp/opencode/bridge.log &
.venv/bin/uvicorn webapp.backend.app:app --port 8000 &>/tmp/opencode/app.log &
sleep 8
curl -s -o /dev/null -w "bridge :8378  %{http_code}\n" localhost:8378/v1/models
curl -s -o /dev/null -w "app    :8000  %{http_code}\n" localhost:8000/api/health
echo "Open http://localhost:8000  (stop with ./stop.sh)"
