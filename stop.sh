#!/bin/bash
# Stop both servers:  ./stop.sh
pkill -f "uvicorn src.opencode_bridge" 2>/dev/null
pkill -f "uvicorn webapp.backend.app" 2>/dev/null
sleep 2
echo "stopped"
