# Railway Deployment Guide - YOLOv11 Damage Detection API

**Last Updated**: May 10, 2026  
**Status**: ✅ Complete Railway Setup

---

## 📋 Table of Contents

1. [Quick Summary](#quick-summary)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Railway Configuration](#railway-configuration)
5. [Deployment Process](#deployment-process)
6. [Post-Deployment](#post-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Costs](#costs)

---

## 🎯 Quick Summary

### What is Railway?
Railway is a modern platform for deploying web applications with:
- ✅ Easy GitHub integration
- ✅ Automatic deployments on push
- ✅ Free tier available
- ✅ PostgreSQL/MySQL support
- ✅ Environment variables management
- ✅ Logs and monitoring

### Your Deployment Flow

```
Your Local Code
        ↓
GitHub Repository (push code)
        ↓
Railway (detects push)
        ↓
Builds Docker container
        ↓
Runs your API
        ↓
Public URL: https://yourapp.up.railway.app
```

---

## ✅ Prerequisites

1. **GitHub Account** (free at github.com)
2. **Railway Account** (free at railway.app)
3. **Code pushed to GitHub**

---

## 🚀 Step-by-Step Setup

### Step 1: Initialize Git Repository

```bash
cd /Users/muhammad/Documents/Workspaces/University/ARCADIA/Project

# Initialize git
git init

# Configure git (first time only)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: YOLOv11 damage detection API with FastAPI"
```

### Step 2: Create GitHub Repository

1. Go to **github.com** and sign in
2. Click **+ New** (top right) → **New repository**
3. Repository name: `car-damage-detection` (or any name)
4. Description: `YOLOv11 Damage Detection API with FastAPI`
5. Choose **Public** (Railway can access it)
6. Click **Create repository**

### Step 3: Push Code to GitHub

```bash
# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/car-damage-detection.git

# Rename branch to main
git branch -M main

# Push code
git push -u origin main

# You'll be asked for GitHub password/token - use Personal Access Token
```

**Getting GitHub Personal Access Token:**
1. Go to **Settings** → **Developer settings** → **Personal access tokens**
2. Click **Generate new token**
3. Name it: `railway-deploy`
4. Select scopes: `repo`, `read:user`
5. Generate and copy token
6. Use token as password when pushing

### Step 4: Create Railway Account

1. Go to **railway.app**
2. Click **Sign up** (GitHub recommended)
3. Authorize GitHub access
4. Done! ✅

### Step 5: Deploy on Railway

1. Go to **railway.app/dashboard**
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Select your repository: `car-damage-detection`
5. Railway auto-detects Python project ✅
6. Configure variables (see below)
7. Deploy! 🚀

---

## ⚙️ Railway Configuration

### Create `Procfile` in Project Root

This tells Railway how to start your API:

```
# /Procfile (no extension)
web: cd api && python main.py --host 0.0.0.0 --port $PORT
```

### Create `railway.json` (Optional)

```json
{
  "build": {
    "builder": "dockerfile"
  }
}
```

### Environment Variables on Railway

1. In Railway dashboard, go to **Variables**
2. Add these variables:

```
HOST=0.0.0.0
PORT=8000
MODEL_NAME=yolov11n
DEVICE=cpu
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45
MAX_FILE_SIZE=52428800
ALLOWED_FORMATS=jpg,jpeg,png,bmp,gif
LOG_LEVEL=INFO
```

⚠️ **Important**: 
- Use `HOST=0.0.0.0` (not localhost)
- `PORT` is provided by Railway (don't set manually)
- Use `DEVICE=cpu` (no GPU on free tier)

### Update `api/main.py` for Railway

Make sure your FastAPI app reads from environment:

```python
import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEVICE = os.getenv("DEVICE", "cpu")

# When running:
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,  # Important for production
    )
```

---

## 📦 Deployment Process

### Full Workflow

**1. Make Changes Locally**
```bash
# Edit your code
# Test locally: python api/main.py
```

**2. Commit & Push to GitHub**
```bash
git add .
git commit -m "Fix: Updated API endpoints"
git push origin main
```

**3. Railway Auto-Deploys**
- Railway detects push to GitHub
- Pulls latest code
- Builds Docker image
- Starts container
- Your API is live! 🎉

**4. Access Your API**
```
https://yourproject-production.up.railway.app/api/health
```

### Manual Deployment (If Auto-Deploy Fails)

1. Railway dashboard → Project
2. Click **Deploy**
3. Select branch: **main**
4. Click **Deploy**

---

## ✅ Post-Deployment

### Test Your API

```bash
# Replace with your Railway URL
RAILWAY_URL="https://yourproject-production.up.railway.app"

# Test health check
curl $RAILWAY_URL/api/health

# Test root endpoint
curl $RAILWAY_URL/

# Test detection (with image file)
curl -X POST $RAILWAY_URL/api/detect \
  -F "file=@/path/to/image.jpg"
```

### Get Your Public URL

1. Railway Dashboard → Your Project
2. Click **Deployments** tab
3. Find your deployment
4. Click **View**
5. Copy the URL: `https://yourproject-production.up.railway.app`

### View Logs

```bash
# In Railway dashboard
# Click project → Logs tab
# See real-time logs and errors
```

---

## 📝 Project Structure for Railway

```
Project/
├── api/
│   ├── main.py              ✅ Your FastAPI app
│   ├── requirements.txt     ✅ Python dependencies
│   ├── .env.example         ✅ Environment template
│   └── yolov11n.pt          ⚠️ Large file (see below)
├── Procfile                 ✅ How to start app (NEW)
├── railway.json             ✅ Railway config (OPTIONAL)
├── .gitignore               ✅ What to exclude (NEW)
└── README.md
```

### Create `.gitignore` file

```
# /​.gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
*.pt
*.pth
outputs/
runs/
.DS_Store
```

---

## ⚠️ Important: Model File Size

### Problem
Your `yolov11n.pt` model is ~6-12 MB. Railway has limits:
- Free tier: 500 MB total
- Deployments: Fast (small files better)

### Solution 1: Download Model on Startup (RECOMMENDED)
Edit `api/main.py`:

```python
def load_model():
    """Load YOLO model from file or download"""
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading {MODEL_NAME}...")
        model = YOLO(f"{MODEL_NAME}.pt")
        model.save(MODEL_PATH)
    else:
        model = YOLO(MODEL_PATH)
    return model

# On Railway first startup:
# - If model not found, download automatically
# - Subsequent deployments use cached model
```

### Solution 2: Add to `.gitignore`
```bash
echo "*.pt" >> .gitignore
git rm --cached api/yolov11n.pt
git commit -m "Remove model file from git"
git push
```

---

## 🔒 Secure Your API

### Add API Key Authentication (Optional)

```python
# In api/main.py
from fastapi import HTTPException, Header

API_KEY = os.getenv("API_KEY", "your-secret-key")

@app.post("/api/detect")
async def detect(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of code
```

### Set Railway Secret Variable
```
API_KEY=super-secret-key-12345
```

---

## 🧪 Troubleshooting

### Issue: "Build failed"

**Check logs:**
```
Railway Dashboard → Logs
```

**Common causes:**
- Missing `requirements.txt`
- Python syntax errors
- Missing dependencies

**Fix:**
```bash
# Test locally first
python -m pip install -r api/requirements.txt
python api/main.py
```

### Issue: "Application crashed"

**Check environment variables:**
- `PORT` must be read from `$PORT` env var
- `HOST` must be `0.0.0.0`

```python
# Correct:
port = int(os.getenv("PORT", 8000))
host = os.getenv("HOST", "0.0.0.0")

# Wrong:
port = 8000  # ❌ Fixed port
host = "127.0.0.1"  # ❌ Localhost only
```

### Issue: "502 Bad Gateway"

**Likely causes:**
- API takes too long to start (model loading)
- Memory issues
- Port not responding

**Solution:**
```python
# Add startup check
@app.on_event("startup")
async def startup():
    print("Loading model...")
    global model
    model = load_model()
    print("Model loaded!")
```

### Issue: "File too large"

**Solution:** Use `.gitignore` to exclude model file

```bash
echo "*.pt" >> .gitignore
git add -A
git commit -m "Update gitignore"
git push
```

### Issue: "Connection timeout"

**Causes:**
- API is loading model (takes time on first startup)
- Railway is starting container

**Solution:**
- Wait 30-60 seconds for first request
- Increase Railway timeout in settings

---

## 💰 Costs

### Railway Pricing

**Free Tier:**
- ✅ 500 MB storage
- ✅ $5 credit/month
- ✅ Perfect for testing
- ✅ Pay as you go after

**Typical Usage:**
- Your API: ~$5-10/month
- Database (if added): ~$5/month

**Estimate for your app:**
- Small project: **~$5-10/month**
- Medium project: **~$20-30/month**

---

## 📊 Next Steps

**After Deployment:**

1. ✅ Test API endpoints
2. ✅ Update Flask integration guide with Railway URL
3. ✅ Monitor logs and performance
4. ✅ Scale if needed (click "Add Instance")

---

## 🎉 Your Deployment URL

Once deployed, your API will be at:

```
https://yourproject-production.up.railway.app
```

**Update Flutter app:**
```dart
DamageDetectionService(
  baseUrl: 'https://yourproject-production.up.railway.app'
)
```

---

## 📚 Useful Commands

```bash
# Create Procfile
echo "web: cd api && python main.py --host 0.0.0.0 --port \$PORT" > Procfile

# Test locally with Railway variables
PORT=8000 HOST=0.0.0.0 python api/main.py

# View git remote
git remote -v

# See deployment branches
git branch -a

# Recent commits
git log --oneline -10
```

---

## ✅ Deployment Checklist

- [ ] GitHub account created
- [ ] Railway account created
- [ ] Local git repository initialized
- [ ] Code committed locally
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Environment variables set
- [ ] Procfile created
- [ ] First deployment successful
- [ ] API endpoints tested
- [ ] Public URL obtained
- [ ] Flutter app updated with new URL
- [ ] Logs monitored for errors

---

**Status**: ✅ Ready to Deploy!

Your backend will be live in < 5 minutes! 🚀

