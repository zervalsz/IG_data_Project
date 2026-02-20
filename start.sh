#!/bin/bash

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Instagram Creator Content Lab${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if backend is running
if pgrep -f "uvicorn.*api.server:app" > /dev/null; then
    echo -e "${GREEN}✓ Backend already running${NC}"
else
    echo -e "${YELLOW}○ Starting backend server...${NC}"
    cd backend
    nohup uvicorn api.server:app --host 0.0.0.0 --port 5001 --reload > /tmp/backend.log 2>&1 &
    sleep 3
    if pgrep -f "uvicorn.*api.server:app" > /dev/null; then
        echo -e "${GREEN}✓ Backend started on http://localhost:5001${NC}"
    else
        echo -e "${YELLOW}! Check /tmp/backend.log for errors${NC}"
    fi
    cd ..
fi

# Check if frontend is running
if lsof -ti:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend already running${NC}"
else
    echo -e "${YELLOW}○ Starting frontend server...${NC}"
    cd xhs-analyser-frontend
    pnpm dev > /tmp/frontend.log 2>&1 &
    sleep 5
    if lsof -ti:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend started on http://localhost:3000${NC}"
    else
        echo -e "${YELLOW}! Check /tmp/frontend.log for errors${NC}"
    fi
    cd ..
fi

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Services:${NC}"
echo -e "  Frontend:  http://localhost:3000"
echo -e "  Backend:   http://localhost:5001"
echo -e "  API Docs:  http://localhost:5001/docs"
echo ""
echo -e "${BLUE}Features:${NC}"
echo -e "  📊 Style-Based Generator - /style-generator"
echo -e "  📈 Trend-Based Generator - /trend-generator"
echo -e "  👥 Creator Profiles      - /creator/[id]"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  Backend:  tail -f /tmp/backend.log"
echo -e "  Frontend: tail -f /tmp/frontend.log"
echo -e "${BLUE}======================================${NC}"
