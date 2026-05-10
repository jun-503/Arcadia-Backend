# Railway Deployment - Quick Reference

## 🚀 5-Minute Deployment Flow

### Step 1: Prepare Locally (2 min)

```bash
cd /Users/muhammad/Documents/Workspaces/University/ARCADIA/Project

# Initialize git
git init
git config user.name "Your Name"
git config user.email "your@email.com"

# Commit all files
git add .
git commit -m "Initial commit: YOLOv11 API"
```

### Step 2: Push to GitHub (2 min)

```bash
# Create repo at github.com (make it PUBLIC)
# Then:

git remote add origin https://github.com/YOUR_USERNAME/car-damage-detection.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Railway (1 min)

1. Go to **railway.app** → Sign up with GitHub
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Choose your repository
5. Set variables (see below)
6. Click **Deploy** ✅

---

## ⚙️ Environment Variables for Railway

Add these in Railway Dashboard → Variables:

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

---

## 📁 Files Already Created for Railway

✅ **Procfile** - Tells Railway how to start your app
✅ **.gitignore** - Excludes model files from git
✅ **requirements.txt** - Python dependencies
✅ **api/main.py** - Your FastAPI application

---

## 🌐 After Deployment

Your API will be available at:

```
https://yourproject-production.up.railway.app
```

**Test it:**

```bash
# Replace with your Railway URL
curl https://yourproject-production.up.railway.app/api/health
```

**Update Flutter app:**

```dart
DamageDetectionService(
  baseUrl: 'https://yourproject-production.up.railway.app'
)
```

---

## 🔄 Update Your App

After deploying, to update:

1. Make changes locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push origin main
   ```
3. Railway auto-deploys! 🎉

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Build failed** | Check Railway logs for errors |
| **App crashed** | Use `HOST=0.0.0.0` not `localhost` |
| **Model file too large** | Railway downloads on startup |
| **Can't deploy** | Make sure git is pushed to GitHub |
| **API timeout** | Wait 30-60s on first request (model loading) |

---

## 📚 Resources

- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- GitHub Docs: https://docs.github.com

---

**Status**: ✅ Ready to Deploy!

Your backend will go live in **< 5 minutes** 🚀

