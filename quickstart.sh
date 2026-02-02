#!/bin/bash
# YANTRAX MVP v6.0 Quick Start Script

echo "🚀 YANTRAX MVP v6.0 - Quick Start"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}✗ Please run this script from the yantrax-rl root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking Python environment${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

echo ""
echo -e "${YELLOW}Step 2: Installing backend dependencies${NC}"
cd backend
pip install -q -r requirements.txt 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install backend dependencies${NC}"
    exit 1
fi
cd ..

echo ""
echo -e "${YELLOW}Step 3: Testing backend import${NC}"
cd backend
if python -c "from main_mvp import app; print('✓ Backend loads successfully')" 2>/dev/null; then
    echo -e "${GREEN}✓ Backend ready${NC}"
else
    echo -e "${RED}✗ Backend import failed${NC}"
    echo "  Run: python -c 'from main_mvp import app' for details"
    cd ..
    exit 1
fi
cd ..

echo ""
echo -e "${YELLOW}Step 4: Checking frontend dependencies${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install -q 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${RED}✗ Failed to install frontend dependencies${NC}"
        cd ..
        exit 1
    fi
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi
cd ..

echo ""
echo -e "${YELLOW}Step 5: Database check${NC}"
cd backend
if [ -f "yantrax.db" ]; then
    echo -e "${GREEN}✓ Database exists${NC}"
    db_size=$(du -h yantrax.db | awk '{print $1}')
    echo "  Size: $db_size"
else
    echo -e "${YELLOW}⚠ Database will be created on first run${NC}"
fi
cd ..

echo ""
echo "=================================="
echo -e "${GREEN}✅ System Ready!${NC}"
echo "=================================="
echo ""
echo "To start the MVP:"
echo ""
echo -e "${YELLOW}Terminal 1 (Backend):${NC}"
echo "  cd backend && python main_mvp.py"
echo ""
echo -e "${YELLOW}Terminal 2 (Frontend):${NC}"
echo "  cd frontend && npm run dev"
echo ""
echo -e "${YELLOW}Terminal 3 (Optional - Test API):${NC}"
echo "  curl http://localhost:5000/"
echo ""
echo "Once running:"
echo "  • Backend: http://localhost:5000"
echo "  • Frontend: http://localhost:5173"
echo "  • Onboarding: http://localhost:5173/onboarding"
echo ""
echo -e "${YELLOW}Next: Add your Perplexity API key${NC}"
echo "  echo 'PERPLEXITY_API_KEY=pplx-YOUR_KEY' >> backend/.env"
echo ""
