#!/bin/bash

# Railway Deployment Quick Setup Script
# Run this to initialize git and prepare for Railway deployment

echo "🚀 Railway Deployment Setup"
echo "================================"

# Check if git is initialized
if [ ! -d .git ]; then
    echo "✅ Initializing git repository..."
    git init
    
    echo "✅ Configuring git user (first time only)..."
    git config user.name "Car Damage Detection"
    git config user.email "app@railway.app"
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "✅ Adding files to git..."
git add .

# Create initial commit
echo "✅ Creating initial commit..."
git commit -m "Initial commit: YOLOv11 damage detection API with FastAPI"

# Show status
echo ""
echo "📊 Current Status:"
echo "================================"
git log --oneline -1
git status

echo ""
echo "📝 Next Steps:"
echo "================================"
echo "1. Create GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Name: car-damage-detection"
echo "   - Make it PUBLIC"
echo ""
echo "2. Add GitHub remote (replace YOUR_USERNAME):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/car-damage-detection.git"
echo ""
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. Deploy on Railway:"
echo "   - Go to https://railway.app"
echo "   - Click 'New Project' → 'Deploy from GitHub repo'"
echo "   - Select your repository"
echo "   - Add environment variables"
echo "   - Deploy!"
echo ""
echo "================================"
echo "✅ Setup complete!"
