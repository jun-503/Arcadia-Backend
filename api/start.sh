#!/bin/bash

# Quick Start Script for YOLOv11 Damage Detection API
# Usage: bash api/start.sh [dev|prod|docker]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 YOLOv11 Damage Detection API - Quick Start"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if model exists
if [ ! -f "$PROJECT_DIR/model/weights/best_run2.pt" ]; then
    echo "⚠️  Warning: Model not found at model/weights/best_run2.pt"
    echo "   Using alternative model or download the model first."
fi

MODE=${1:-dev}

case $MODE in
    dev)
        echo "📝 Starting in DEVELOPMENT mode..."
        echo "   - Hot reload enabled"
        echo "   - Debug mode on"
        echo "   - Port 8000"
        echo ""
        echo "✅ Installation instructions:"
        echo "   pip install -r api/requirements.txt"
        echo ""
        echo "✅ API will be available at:"
        echo "   - Main: http://localhost:8000"
        echo "   - Docs: http://localhost:8000/docs"
        echo "   - ReDoc: http://localhost:8000/redoc"
        echo ""
        echo "Starting server..."
        cd "$PROJECT_DIR"
        uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
        ;;
    
    prod)
        echo "⚙️  Starting in PRODUCTION mode..."
        echo "   - Multiple workers (4)"
        echo "   - Debug mode off"
        echo "   - Port 8000"
        echo ""
        echo "✅ API will be available at:"
        echo "   - Main: http://localhost:8000"
        echo "   - Docs: http://localhost:8000/docs"
        echo ""
        
        # Create logs directory if it doesn't exist
        mkdir -p "$PROJECT_DIR/logs"
        
        echo "Starting server..."
        cd "$PROJECT_DIR"
        uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
        ;;
    
    docker)
        echo "🐳 Starting with Docker..."
        
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not found. Please install Docker first."
            echo "   https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        
        echo "📦 Building Docker image..."
        docker build -t yolo-damage-api:latest .
        
        echo ""
        echo "🚀 Starting Docker container..."
        docker run --rm -p 8000:8000 \
            -v $(pwd)/model/weights:/app/model/weights:ro \
            -v $(pwd)/data:/app/data:ro \
            -v $(pwd)/outputs:/app/outputs \
            -e PYTHONUNBUFFERED=1 \
            yolo-damage-api:latest
        ;;
    
    docker-compose)
        echo "🐳 Starting with Docker Compose..."
        
        if ! command -v docker-compose &> /dev/null; then
            echo "❌ Docker Compose not found. Please install Docker Compose first."
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        docker-compose up
        ;;
    
    test)
        echo "🧪 Testing API..."
        
        # Wait for server to start
        sleep 2
        
        echo ""
        echo "📡 Testing endpoints..."
        
        # Test health
        echo -n "  Health check... "
        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo "✅"
        else
            echo "❌"
            exit 1
        fi
        
        # Test models
        echo -n "  Models endpoint... "
        if curl -s http://localhost:8000/api/models > /dev/null; then
            echo "✅"
        else
            echo "❌"
        fi
        
        # Test detection if image exists
        if [ -f "$PROJECT_DIR/test.jpg" ]; then
            echo -n "  Detection endpoint... "
            if curl -s -F "file=@$PROJECT_DIR/test.jpg" \
                     http://localhost:8000/api/detect > /dev/null; then
                echo "✅"
            else
                echo "❌"
            fi
        fi
        
        echo ""
        echo "✅ All tests passed!"
        ;;
    
    *)
        echo "Usage: bash api/start.sh [mode]"
        echo ""
        echo "Modes:"
        echo "  dev             - Development mode (hot reload, debug on)"
        echo "  prod            - Production mode (4 workers, debug off)"
        echo "  docker          - Start with Docker container"
        echo "  docker-compose  - Start with Docker Compose"
        echo "  test            - Run tests"
        echo ""
        echo "Examples:"
        echo "  bash api/start.sh dev"
        echo "  bash api/start.sh prod"
        echo "  bash api/start.sh docker"
        exit 1
        ;;
esac
