# 🚀 FastAPI Deployment - Getting Started

**Last Updated**: May 2, 2026  
**Status**: ✅ Ready for Production

---

## ⚡ 5-Minute Quick Start

### Step 1: Install Dependencies (1 minute)
```bash
pip install -r api/requirements.txt
```

### Step 2: Start API Server (1 minute)
```bash
python api/main.py
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 3: Test in Another Terminal (1 minute)
```bash
# Health check
python api/client.py health

# Detect damage in test image
python api/client.py detect test.jpg
```

### Step 4: View Documentation (1 minute)
```
Open in browser: http://localhost:8000/docs
```

### Step 5: Done! ✅

---

## 📋 What You Just Created

| File | Purpose | Status |
|------|---------|--------|
| `api/main.py` | FastAPI application (500+ lines) | ✅ Complete |
| `api/client.py` | CLI testing tool | ✅ Complete |
| `api/requirements.txt` | Python dependencies | ✅ Complete |
| `Dockerfile` | Container image | ✅ Complete |
| `docker-compose.yml` | Multi-container setup | ✅ Complete |
| `api/EXAMPLES.md` | 15+ code examples | ✅ Complete |
| `FASTAPI_DEPLOYMENT_GUIDE.md` | Full deployment guide | ✅ Complete |
| `api/README.md` | Quick reference | ✅ Complete |
| `API_IMPLEMENTATION_SUMMARY.md` | Complete summary | ✅ Complete |
| `api/ARCHITECTURE.md` | System architecture | ✅ Complete |

---

## 🎯 Verify Installation

### Test 1: Health Check
```bash
curl http://localhost:8000/api/health
```

Expected output:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "current_model": "best_run2.pt"
}
```

### Test 2: Single Image Detection
```bash
curl -F "file=@test.jpg" http://localhost:8000/api/detect | jq .
```

### Test 3: List Models
```bash
curl http://localhost:8000/api/models
```

### Test 4: API Documentation
```
http://localhost:8000/docs
```

---

## 🐳 Docker Quick Start

### Option A: Docker Container
```bash
# Build image
docker build -t yolo-damage-api:latest .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/model/weights:/app/model/weights:ro \
  -v $(pwd)/outputs:/app/outputs \
  yolo-damage-api:latest

# Test
curl http://localhost:8000/api/health
```

### Option B: Docker Compose (Recommended)
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Test
python api/client.py health

# Stop
docker-compose down
```

---

## 📚 Documentation Structure

```
Start Here (5 min)
├─ api/README.md                    <- Quick start & commands
├─ api/EXAMPLES.md                  <- 15+ code examples
│
Deep Dive (30 min)
├─ FASTAPI_DEPLOYMENT_GUIDE.md      <- Comprehensive guide
├─ API_IMPLEMENTATION_SUMMARY.md    <- Complete overview
└─ api/ARCHITECTURE.md              <- System architecture

Reference
├─ api/.env.example                 <- Configuration template
├─ Dockerfile                       <- Docker image
└─ docker-compose.yml              <- Docker Compose config
```

---

## 🔥 Common Commands

### Development
```bash
# Start with hot reload
python api/main.py

# Or with uvicorn
uvicorn api.main:app --reload --port 8000

# Test endpoints
python api/client.py health
python api/client.py detect test.jpg
python api/client.py batch data/raw/test/images
```

### Production
```bash
# 4 worker processes
uvicorn api.main:app --workers 4 --host 0.0.0.0 --port 8000

# 8 worker processes
uvicorn api.main:app --workers 8 --host 0.0.0.0 --port 8000

# With custom configuration
source api/.env
uvicorn api.main:app --host $HOST --port $PORT --workers 4
```

### Docker
```bash
# Build
docker build -t yolo-damage-api:latest .

# Run single container
docker run -p 8000:8000 yolo-damage-api:latest

# Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## 🧪 Testing Workflows

### Test 1: Single Image Detection
```bash
python api/client.py detect test.jpg
```

Output:
```
======================================================================
  YOLOv11 Damage Detection with Severity Scoring
======================================================================

DETECTIONS (2 damages found):
──────────────────────────────────────────────────────────────────────

1. BONNET-DENT
   Confidence:           0.820 (82.0/100)
   Area:                 15.89% of image (100.0/100 severity)
   Location Weight:      1.00x
   ➜ COMBINED SEVERITY:  91.0/100 [CRITICAL]

2. HEADLIGHT-DAMAGE
   Confidence:           0.299 (29.9/100)
   Area:                 3.21% of image (21.0/100 severity)
   Location Weight:      1.40x
   ➜ COMBINED SEVERITY:  27.8/100 [MEDIUM]

──────────────────────────────────────────────────────────────────────
VEHICLE DAMAGE ASSESSMENT:
──────────────────────────────────────────────────────────────────────
Total damages found:     2
Average severity:        59.4/100 [SUBSTANTIAL]
```

### Test 2: Batch Processing
```bash
python api/client.py batch data/raw/test/images --confidence 0.3
```

### Test 3: Python Script
```python
import requests

# Single image
with open("test.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/detect",
        files={"file": f},
        params={"confidence": 0.25}
    )

result = response.json()
print(f"Damages: {result['total_damages']}")
print(f"Average Severity: {result['statistics']['average_severity']}/100")
```

### Test 4: cURL
```bash
# Single image
curl -F "file=@test.jpg" http://localhost:8000/api/detect | jq .

# Pretty print
curl -F "file=@test.jpg" http://localhost:8000/api/detect | jq '.detections[] | {class, severity: .combined_severity}'
```

---

## 🔌 API Response Examples

### Single Image Detection (Success)
```json
{
  "timestamp": "2026-05-02T10:30:45.123456",
  "filename": "car.jpg",
  "total_damages": 2,
  "detections": [
    {
      "class": "bonnet-dent",
      "confidence": 0.82,
      "combined_severity": 91.0,
      "severity_level": "CRITICAL",
      "area_percent": 15.89,
      "bbox": [165, 183, 833, 332]
    }
  ],
  "statistics": {
    "average_severity": 59.4,
    "severity_breakdown": {
      "LOW": 0,
      "MEDIUM": 1,
      "HIGH": 0,
      "CRITICAL": 1
    }
  },
  "vehicle_assessment": {
    "average_severity": 59.4,
    "assessment_level": "SUBSTANTIAL"
  }
}
```

### Health Check (Success)
```json
{
  "status": "healthy",
  "timestamp": "2026-05-02T10:30:45.123456",
  "model_loaded": true,
  "current_model": "best_run2.pt"
}
```

### Error Response (Invalid File)
```json
{
  "detail": "Unsupported format. Supported: ['jpg', 'jpeg', 'png', 'bmp', 'gif']"
}
```

---

## ⚙️ Configuration

### Environment Variables

Copy template:
```bash
cp api/.env.example api/.env
```

Edit configuration:
```env
# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Model
MODEL_NAME=best_run2.pt
DEVICE=mps              # gpu, cpu, or mps for Mac M1/M2

# Thresholds
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45

# File limits
MAX_FILE_SIZE_MB=50
MAX_IMAGE_WIDTH=1024
MAX_IMAGE_HEIGHT=1024
MAX_BATCH_SIZE=100

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=production
DEBUG=False
```

---

## 🐛 Troubleshooting

### Issue: Port 8000 already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python api/main.py --port 8001
uvicorn api.main:app --port 8001
```

### Issue: Model not found
```bash
# Check weights directory
ls -la model/weights/

# Ensure model exists or update config
# MODEL_NAME=best_run2.pt in api/.env
```

### Issue: Dependencies not installed
```bash
# Reinstall all dependencies
pip install --upgrade -r api/requirements.txt

# Or specific package
pip install fastapi uvicorn
```

### Issue: Docker build fails
```bash
# Clean build (no cache)
docker build --no-cache -t yolo-damage-api:latest .

# Check logs
docker build -t yolo-damage-api:latest . 2>&1 | tail -50
```

### Issue: Out of memory
```env
# Reduce limits in .env
MAX_FILE_SIZE_MB=25
MAX_IMAGE_WIDTH=512
MAX_IMAGE_HEIGHT=512
MAX_BATCH_SIZE=10
```

---

## 📊 Performance Monitoring

### Check API Health
```bash
# Continuous monitoring
watch -n 1 'curl -s http://localhost:8000/api/health | jq .'

# Check every 5 seconds
while true; do curl -s http://localhost:8000/api/health; sleep 5; done
```

### View Logs
```bash
# Development logs
tail -f logs/api.log

# Error logs only
tail -f logs/error.log

# Live follow
tail -f logs/api.log | grep ERROR
```

### Performance Stats
```bash
# Response time test
time curl -F "file=@test.jpg" http://localhost:8000/api/detect > /dev/null

# Concurrent requests (requires `ab`)
ab -n 100 -c 10 http://localhost:8000/api/health
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All endpoints tested locally
- [ ] Docker image builds successfully
- [ ] Docker Compose starts without errors
- [ ] Configuration file created (.env)
- [ ] Model file exists (model/weights/best_run2.pt)
- [ ] Test images available

### Deployment
- [ ] Push code to version control
- [ ] Build and push Docker image
- [ ] Deploy to cloud platform (AWS/GCP/Azure)
- [ ] Verify health endpoint
- [ ] Test with real requests
- [ ] Set up monitoring
- [ ] Configure logging

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Check performance metrics
- [ ] Document any issues
- [ ] Set up alerts
- [ ] Plan maintenance window

---

## 📞 Need Help?

### Documentation
1. **Quick Start**: api/README.md
2. **Code Examples**: api/EXAMPLES.md (15+ examples)
3. **Full Guide**: FASTAPI_DEPLOYMENT_GUIDE.md
4. **Architecture**: api/ARCHITECTURE.md
5. **Implementation**: API_IMPLEMENTATION_SUMMARY.md

### Common Questions

**Q: How do I change the model?**
```bash
python api/client.py models
curl -X POST "http://localhost:8000/api/model/switch?model_name=yolo11n.pt"
```

**Q: How do I increase throughput?**
```bash
# Use multiple workers
uvicorn api.main:app --workers 8

# Or use GPU
export DEVICE=cuda
python api/main.py
```

**Q: How do I add authentication?**
See example in api/EXAMPLES.md - APIKeyHeader section

**Q: How do I deploy to AWS?**
See FASTAPI_DEPLOYMENT_GUIDE.md - AWS ECS section

---

## ✅ You're All Set!

Your FastAPI deployment is complete and ready:

✅ **API Running** - http://localhost:8000  
✅ **Docs Available** - http://localhost:8000/docs  
✅ **CLI Working** - `python api/client.py`  
✅ **Docker Ready** - `docker-compose up`  
✅ **Cloud Ready** - Deploy to AWS/GCP/Azure  
✅ **Well Documented** - 8000+ words of guides  

### Next Steps:
1. Start the API: `python api/main.py`
2. Access docs: http://localhost:8000/docs
3. Test endpoints: `python api/client.py health`
4. Deploy to cloud (see FASTAPI_DEPLOYMENT_GUIDE.md)

---

**Questions? Check the documentation files or API Swagger UI at /docs**

