# 🚀 Backend Deployment Guide

**Status**: Complete Deployment Package  
**Last Updated**: May 10, 2026

---

## 📋 Quick Deployment Options

Choose one based on your needs:

| Option | Best For | Setup Time | Cost | Maintenance |
|--------|----------|-----------|------|-------------|
| **Local Development** | Testing locally | 5 min | Free | None |
| **Docker (Local)** | Containerized local dev | 10 min | Free | Low |
| **Railway** | Quick cloud deployment ⭐ | 5 min | $5/mo | Very Low |
| **Render** | Free tier available | 10 min | Free-$12 | Low |
| **AWS EC2** | Full control, scalable | 20 min | $10-50/mo | High |
| **Google Cloud** | Enterprise features | 20 min | Pay-as-you-go | High |
| **Azure** | Windows/hybrid friendly | 20 min | Pay-as-you-go | High |

---

## ⚡ Option 1: Local Development (5 minutes)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd /Users/muhammad/Documents/Workspaces/University/ARCADIA/Project

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r api/requirements.txt
```

### Step 2: Configure Environment

```bash
# Create .env file from template
cp api/.env.example api/.env

# Edit api/.env and set:
# HOST=0.0.0.0
# PORT=8000
# DEVICE=mps  (or cpu if no GPU)
# MODEL_NAME=best_run2.pt
```

### Step 3: Run Server

```bash
# Option A: Simple start
cd api
python3 main.py

# Option B: With auto-reload (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option C: Production-ready (4 workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Access API**: http://localhost:8000

---

## 🐳 Option 2: Docker Deployment (10 minutes)

### Step 1: Build Docker Image

```bash
cd /Users/muhammad/Documents/Workspaces/University/ARCADIA/Project

# Build image
docker build -t damage-detection-api:latest -f Dockerfile .

# Verify build
docker images | grep damage-detection
```

### Step 2: Run Container

```bash
# Run with local port 8000
docker run -p 8000:8000 \
  -e DEVICE=cpu \
  -e MODEL_NAME=best_run2.pt \
  --name damage-api \
  damage-detection-api:latest

# Run in background
docker run -d -p 8000:8000 \
  -e DEVICE=cpu \
  --name damage-api \
  damage-detection-api:latest

# Check logs
docker logs -f damage-api
```

### Step 3: Test API

```bash
# Health check
curl http://localhost:8000/api/health

# Get models
curl http://localhost:8000/api/models
```

### Step 4: Stop Container

```bash
docker stop damage-api
docker rm damage-api
```

### Using Docker Compose (Easiest)

```bash
cd /Users/muhammad/Documents/Workspaces/University/ARCADIA/Project

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## 🚀 Option 3: Railway Deployment (⭐ RECOMMENDED - 5 minutes)

Railway is the **easiest and fastest** cloud deployment option.

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your GitHub account

### Step 2: Deploy from GitHub

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Select your ARCADIA repository
4. Railway auto-detects it's a Python app
5. Click "Deploy"

### Step 3: Configure Environment Variables

In Railway Dashboard:
- Go to your project → Variables
- Add these environment variables:

```
HOST=0.0.0.0
PORT=8000
DEVICE=cpu
MODEL_NAME=best_run2.pt
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45
MAX_FILE_SIZE_MB=50
ENVIRONMENT=production
DEBUG=False
```

### Step 4: Set Port Binding

- Go to Settings
- Port: 8000
- Ensure "Expose" is enabled

### Step 5: Get Public URL

- Your API will be available at: `https://your-project.up.railway.app`
- Test it: `https://your-project.up.railway.app/api/health`

### Step 6: Monitor Deployment

```bash
# View logs (in Railway Dashboard)
# Settings → View Logs

# Or use Railway CLI
railway logs
```

**Cost**: $5/month (free tier: 500 hours/month)

---

## 🌐 Option 4: Render Deployment (10 minutes)

### Step 1: Connect GitHub

1. Go to [render.com](https://render.com)
2. Sign up and connect GitHub
3. Click "New +"
4. Select "Web Service"
5. Connect to your repository

### Step 2: Configure Service

```
Name: damage-detection-api
Environment: Python 3
Build Command: pip install -r api/requirements.txt
Start Command: cd api && uvicorn main:app --host 0.0.0.0 --port 8000
```

### Step 3: Set Environment Variables

```
HOST=0.0.0.0
PORT=8000
DEVICE=cpu
MODEL_NAME=best_run2.pt
ENVIRONMENT=production
DEBUG=False
```

### Step 4: Deploy

- Click "Create Web Service"
- Render builds and deploys automatically
- Get your URL: `https://damage-detection-api.onrender.com`

**Cost**: Free tier (auto-sleeps after 15 min inactivity)

---

## 🏗️ Option 5: AWS EC2 Deployment (20 minutes)

### Step 1: Launch EC2 Instance

1. Go to AWS Console
2. EC2 → Instances → Launch Instance
3. Select: Ubuntu 22.04 LTS (free tier eligible)
4. Instance type: `t2.micro` (free tier)
5. Security group: Allow HTTP (80), HTTPS (443), Custom TCP (8000)

### Step 2: Connect to Instance

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update
sudo apt upgrade -y
```

### Step 3: Install Dependencies

```bash
# Install Python and pip
sudo apt install -y python3-pip python3-venv

# Install system dependencies
sudo apt install -y libsm6 libxext6 libxrender-dev

# Clone or upload your project
git clone https://github.com/your-username/ARCADIA.git
cd ARCADIA

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r api/requirements.txt
```

### Step 4: Configure Environment

```bash
cp api/.env.example api/.env

# Edit .env
nano api/.env

# Set:
# HOST=0.0.0.0
# PORT=8000
# DEVICE=cpu
# ENVIRONMENT=production
```

### Step 5: Run with Gunicorn/Supervisor

```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/damage-api.service
```

Add this content:

```ini
[Unit]
Description=Damage Detection API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ARCADIA/api
ExecStart=/home/ubuntu/ARCADIA/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable damage-api
sudo systemctl start damage-api
sudo systemctl status damage-api
```

### Step 6: Setup Nginx Reverse Proxy (Optional)

```bash
sudo apt install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/damage-api
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/damage-api /etc/nginx/sites-enabled/

# Test and start Nginx
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Cost**: $0-10/month

---

## ☁️ Option 6: Google Cloud Run (Pay-as-you-go)

### Step 1: Setup Google Cloud

```bash
# Install Google Cloud SDK
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project your-project-id
```

### Step 2: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Step 3: Build and Deploy

```bash
# From project root
gcloud run deploy damage-detection-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 300 \
  --set-env-vars DEVICE=cpu,MODEL_NAME=best_run2.pt,ENVIRONMENT=production
```

### Step 4: Get URL

```bash
gcloud run services list

# Your API URL: https://damage-detection-api-xxxxx.run.app
```

**Cost**: Free tier: 2 million requests/month

---

## 🔒 Security Best Practices

### 1. Use HTTPS

```bash
# Railway/Render: Automatic
# AWS: Use AWS Certificate Manager
# GCP: Automatic

# For self-hosted:
# Use Certbot for Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

### 2. Set Strong Environment Variables

```bash
# Production .env
ENVIRONMENT=production
DEBUG=False
DEVICE=cpu  # or cuda if GPU available
MAX_FILE_SIZE_MB=50
CORS_ORIGINS=["https://your-flutter-app.com"]
```

### 3. Add API Key Authentication (Optional)

Update `api/main.py`:

```python
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "your-secret-key")

@app.post("/api/detect")
async def detect(
    file: UploadFile,
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    # ... rest of function
```

### 4. Monitor Logs

```bash
# Railway
railway logs

# Render
tail -f logs

# AWS
aws logs tail /aws/lambda/damage-api --follow

# Local Docker
docker logs -f damage-api
```

---

## ✅ Deployment Checklist

### Before Deploying
- [ ] API tested locally
- [ ] `.env` configured with production values
- [ ] Model weights (`best_run2.pt`) available
- [ ] All dependencies in `requirements.txt`
- [ ] CORS configured correctly
- [ ] Database (if any) ready

### After Deploying
- [ ] Test health endpoint: `GET /api/health`
- [ ] Test models endpoint: `GET /api/models`
- [ ] Test detection: `POST /api/detect` with test image
- [ ] Check logs for errors
- [ ] Monitor resource usage
- [ ] Set up error alerts
- [ ] Document API URL for Flutter app
- [ ] Update Flutter app with API URL

---

## 🧪 Test Your Deployment

### Test with cURL

```bash
# Replace YOUR_API_URL with your actual URL
API_URL="http://localhost:8000"  # or https://your-deployed-api.com

# 1. Health check
curl $API_URL/api/health

# 2. Get models
curl $API_URL/api/models

# 3. Get config
curl $API_URL/api/config

# 4. Upload image
curl -X POST \
  -F "file=@/path/to/image.jpg" \
  $API_URL/api/detect
```

### Test with Python

```python
import requests
import json

API_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{API_URL}/api/health")
print("Health:", response.json())

# 2. Detect damage
with open("test_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{API_URL}/api/detect", files=files)
    print("Detection:", json.dumps(response.json(), indent=2))
```

### Test with Flutter

```dart
// In Flutter app, use your deployed API URL
DamageDetectionService(
  baseUrl: 'https://your-deployed-api.com',  // Your deployed URL
)
```

---

## 📊 Recommended Deployment Path

### For Development:
1. Start with **Local Development** (Option 1)
2. Test everything works locally
3. Move to **Docker** (Option 2) for consistency

### For Production:
1. **Railway** (Option 3) - Easiest, fastest ⭐
   - Auto-deploys from GitHub
   - $5/month
   - Great for small projects

2. **Render** (Option 4) - Good alternative
   - Free tier available
   - Easy setup

3. **AWS/GCP** (Options 5-6) - For scalability
   - More control
   - Better for growth
   - More complex setup

---

## 🐛 Troubleshooting

### Issue: Module not found error
```bash
# Ensure all dependencies installed
pip install -r api/requirements.txt

# Check if model file exists
ls -la model/weights/
```

### Issue: Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (macOS/Linux)
kill -9 <PID>
```

### Issue: CORS errors in Flutter
```python
# In main.py, ensure CORS is enabled
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific URLs in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: High memory usage
```bash
# Use CPU instead of GPU
export DEVICE=cpu

# Reduce batch size
export MAX_BATCH_SIZE=10
```

### Issue: Model loading fails
```bash
# Ensure model path is correct
export MODEL_NAME=best_run2.pt

# Check if model exists in current directory
find . -name "*.pt" -type f
```

---

## 📞 Support & Next Steps

1. **Deploy to Railway** (easiest)
   - Go to https://railway.app
   - Connect GitHub
   - Deploy in 2 minutes

2. **Get your API URL** and test it

3. **Update Flutter app** with deployed URL

4. **Monitor logs** for any issues

5. **Scale if needed** later

---

**Status**: ✅ Ready for Deployment

Choose your deployment option and let me know if you need help!

