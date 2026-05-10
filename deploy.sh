#!/bin/bash

# 🚀 Quick Deployment Script
# Automates local API deployment setup

set -e

echo "╔════════════════════════════════════════════╗"
echo "║   YOLOv11 Damage Detection API Deployment  ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo -e "${BLUE}[1/6]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"
echo ""

# Step 2: Create virtual environment
echo -e "${BLUE}[2/6]${NC} Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Step 3: Activate virtual environment
echo -e "${BLUE}[3/6]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 4: Install dependencies
echo -e "${BLUE}[4/6]${NC} Installing dependencies..."
echo "This may take 3-5 minutes on first run..."
pip install -q -r api/requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 5: Setup .env file
echo -e "${BLUE}[5/6]${NC} Setting up configuration..."
if [ ! -f "api/.env" ]; then
    cp api/.env.example api/.env
    echo -e "${GREEN}✓ Configuration file created: api/.env${NC}"
    echo ""
    echo "📝 Edit api/.env to customize settings:"
    echo "   - DEVICE: cpu or mps or cuda"
    echo "   - MODEL_NAME: path to your model file"
    echo "   - CONFIDENCE_THRESHOLD: detection confidence"
else
    echo -e "${GREEN}✓ Configuration file already exists${NC}"
fi
echo ""

# Step 6: Show startup options
echo -e "${BLUE}[6/6]${NC} Ready to deploy!"
echo ""
echo -e "${GREEN}✓ Deployment setup complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Start your API with one of these commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Option 1: Development (auto-reload)${NC}"
echo "  cd api && uvicorn main:app --reload"
echo ""
echo -e "${YELLOW}Option 2: Production (4 workers)${NC}"
echo "  cd api && uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000"
echo ""
echo -e "${YELLOW}Option 3: Docker${NC}"
echo "  docker-compose up -d"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 API will be available at: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "🌐 For cloud deployment, see: DEPLOYMENT_GUIDE.md"
echo ""
