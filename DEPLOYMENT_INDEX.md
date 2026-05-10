# 📚 Deployment Resources Index

**Status**: ✅ Complete Deployment Package  
**Last Updated**: May 10, 2026

---

## 🎯 Choose Your Path

### 👨‍💻 Just Starting? Read This First
**→ [QUICK_START.md](QUICK_START.md)** (5 min read)
- Quick setup in 2 minutes
- Verify your deployment works
- Deploy to cloud in 15 minutes

### 🚀 Ready to Deploy Locally?
1. Run: `bash deploy.sh` (automated setup)
2. Start: `cd api && uvicorn main:app --reload`
3. Test: `python3 test_deployment.py`

### ☁️ Ready to Deploy to Cloud?
**→ [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** (Complete guide)

**Quick Options:**
- **Railway** (⭐ Recommended): 5 min setup, $5/month
- **Render**: 10 min setup, free tier
- **AWS**: 20 min setup, $10-50/month
- **Google Cloud**: 20 min setup, pay-as-you-go
- **Docker**: Any hosting with Docker support

### 📱 Integrating with Flutter?
**→ [api/FLUTTER_INTEGRATION.md](api/FLUTTER_INTEGRATION.md)** (Complete guide)
- HTTP client setup
- Image picker integration
- Complete example screens
- Troubleshooting

---

## 📁 Files Created for Deployment

### Core Deployment Files
| File | Purpose | Status |
|------|---------|--------|
| `deploy.sh` | Automated setup script | ✅ Ready |
| `test_deployment.py` | Deployment verification | ✅ Ready |
| `api/.env.example` | Configuration template | ✅ Ready |
| `api/.env.production` | Production config | ✅ Ready |
| `Dockerfile` | Docker image definition | ✅ Ready |
| `docker-compose.yml` | Multi-container setup | ✅ Ready |

### Documentation Files
| File | Purpose | Audience |
|------|---------|----------|
| `QUICK_START.md` | 5-minute quick start | Everyone |
| `DEPLOYMENT_GUIDE.md` | Complete deployment options | DevOps/Developers |
| `api/FLUTTER_INTEGRATION.md` | Flutter integration guide | Mobile Developers |
| `api/README.md` | API quick reference | Developers |
| `api/EXAMPLES.md` | Code examples | Developers |
| `api/ARCHITECTURE.md` | System architecture | Architects |

---

## 🚀 Deployment Timeline

### Today: Local Deployment (10 minutes)
```bash
# 1. Setup (2 min)
bash deploy.sh

# 2. Start (1 min)
cd api && uvicorn main:app --reload

# 3. Test (2 min)
python3 test_deployment.py

# 4. Done! ✅
```

### Tomorrow: Cloud Deployment (5-15 minutes)
```bash
# Choose one:
# Option 1: Railway (5 min)
# - Go to railway.app
# - Connect GitHub
# - Deploy

# Option 2: Render (10 min)
# - Go to render.com
# - Create web service
# - Deploy

# Option 3: Docker (Any platform)
# - Build: docker build -t api .
# - Run: docker run -p 8000:8000 api
```

### Next Week: Flutter Integration
```bash
# 1. Update Flutter app with API URL
# 2. Test with deployed API
# 3. Submit to App Stores
```

---

## 📊 Deployment Comparison

### Local Development
- ⏱️ Setup: 2 minutes
- 💰 Cost: Free
- 🔧 Maintenance: Very Low
- ✅ Best for: Testing & development

### Docker Container
- ⏱️ Setup: 5 minutes
- 💰 Cost: Free (+ hosting)
- 🔧 Maintenance: Low
- ✅ Best for: Consistent environments

### Railway (⭐ Recommended)
- ⏱️ Setup: 5 minutes
- 💰 Cost: $5/month
- 🔧 Maintenance: Very Low
- ✅ Best for: Small projects, quick deployment

### AWS/GCP
- ⏱️ Setup: 20-30 minutes
- 💰 Cost: $10-100+/month
- 🔧 Maintenance: Medium-High
- ✅ Best for: Enterprise, heavy workloads

---

## 🎯 Step-by-Step: Local Deployment

### Step 1: Run Setup Script
```bash
cd /Users/muhammad/Documents/Workspaces/University/ARCADIA/Project
bash deploy.sh
```

**What it does:**
- ✅ Checks Python 3 installation
- ✅ Creates virtual environment (`venv/`)
- ✅ Installs all dependencies
- ✅ Creates `.env` configuration file
- ✅ Shows startup commands

### Step 2: Start API
```bash
# Development (auto-reload on changes)
cd api
uvicorn main:app --reload

# Or production (4 workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 3: Access API
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

### Step 4: Test Deployment
```bash
python3 test_deployment.py
```

**Expected Output:**
```
✓ Connection Test - PASS
✓ Health Check - PASS
✓ Models Endpoint - PASS
✓ Configuration - PASS
✓ Detection - PASS
✓ Batch Detection - PASS

✓ All tests passed (6/6)
```

---

## 🎯 Step-by-Step: Cloud Deployment (Railway)

### Step 1: Create Railway Account
- Go to https://railway.app
- Sign up with GitHub
- Authorize Railway to access your repositories

### Step 2: Deploy
- Click "New Project"
- Select "Deploy from GitHub repo"
- Select your ARCADIA repository
- Click "Deploy"

### Step 3: Configure
- Go to Variables tab
- Add environment variables:
  ```
  DEVICE=cpu
  MODEL_NAME=best_run2.pt
  ENVIRONMENT=production
  DEBUG=False
  ```

### Step 4: Get URL
- Your API is live at: `https://your-project.up.railway.app`
- Test: `curl https://your-project.up.railway.app/api/health`

### Step 5: Monitor
- View logs in Railway Dashboard
- Monitor resource usage
- Set up error alerts

---

## 🔧 Configuration Guide

### Development Environment (`api/.env`)
```bash
HOST=0.0.0.0
PORT=8000
DEVICE=cpu  # Use mps for Mac Silicon, cuda for NVIDIA GPU
ENVIRONMENT=development
DEBUG=True
```

### Production Environment (`api/.env.production`)
```bash
HOST=0.0.0.0
PORT=8000
WORKERS=4  # Number of worker processes
DEVICE=cpu
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=["https://your-domain.com"]
```

### Model Configuration
```bash
# Available models in model/weights/
MODEL_NAME=best_run2.pt

# Detection parameters
CONFIDENCE_THRESHOLD=0.25  # Higher = fewer detections
IOU_THRESHOLD=0.45        # Higher = more detections
```

---

## ✅ Pre-Deployment Checklist

### Before Local Deployment
- [ ] Python 3.8+ installed
- [ ] Model file exists (`model/weights/best_run2.pt`)
- [ ] Enough disk space for dependencies (~2GB)
- [ ] Port 8000 is available

### Before Cloud Deployment
- [ ] API tested locally
- [ ] `.env` configured correctly
- [ ] Model file accessible
- [ ] Docker build successful
- [ ] All tests pass

### Before Flutter Integration
- [ ] API deployed and accessible
- [ ] Public URL obtained
- [ ] CORS configured
- [ ] Test with cURL works
- [ ] Flutter dependencies installed

---

## 🐛 Troubleshooting

### Problem: "Module not found"
```bash
# Install dependencies again
pip install -r api/requirements.txt
```

### Problem: "Port 8000 already in use"
```bash
# Use different port
uvicorn main:app --port 8001

# Or kill process using 8000
lsof -i :8000  # Find PID
kill -9 <PID>  # Kill process
```

### Problem: "Model file not found"
```bash
# Check if model exists
ls -la model/weights/

# Verify path in .env
cat api/.env | grep MODEL_NAME
```

### Problem: "API timeout on first request"
- This is normal! First request loads the model (~20s)
- Subsequent requests are much faster (100-150ms)

### Problem: "High memory usage"
```bash
# Use CPU instead of GPU
export DEVICE=cpu

# Reduce batch size
export MAX_BATCH_SIZE=10

# Restart API
```

---

## 📞 Support & Resources

### Quick Links
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Uvicorn Documentation**: https://www.uvicorn.org
- **Railway Docs**: https://railway.app/docs
- **Render Docs**: https://docs.render.com
- **Flutter Docs**: https://flutter.dev/docs

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Files to Read
1. Start with: `QUICK_START.md` (5 min)
2. For details: `DEPLOYMENT_GUIDE.md` (15 min)
3. For Flutter: `api/FLUTTER_INTEGRATION.md` (20 min)
4. For API: `api/EXAMPLES.md` (code examples)

---

## 🎉 You're Ready!

Everything is set up for deployment. Choose your path:

### 🚀 Quick Local Test
```bash
bash deploy.sh
cd api && uvicorn main:app --reload
python3 test_deployment.py
```

### ☁️ Deploy to Cloud
```bash
# Railway (5 minutes)
1. Go to railway.app
2. Connect GitHub
3. Select repository
4. Click Deploy
```

### 📱 Integrate with Flutter
```bash
# Update Flutter app with API URL
DamageDetectionService(baseUrl: 'https://your-api-url.com')
```

---

**Status**: ✅ All Systems Ready for Deployment

**Next Step**: Run `bash deploy.sh` now! 🚀

