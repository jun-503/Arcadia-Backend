# FastAPI Deployment Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Web Browser │  │   Mobile App │  │  Python SDK  │           │
│  │   (React)    │  │  (iOS/Android)  │  (Requests)  │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                      │
│                    HTTP/HTTPS (JSON)                             │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │    Load Balancer / Proxy    │
              │      (nginx/haproxy)        │
              └──────────────┬──────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐      ┌──────▼──────┐      ┌─────▼────────┐
│  API Worker  │      │  API Worker │      │  API Worker  │
│   (Process)  │      │   (Process) │      │  (Process)   │
│   Port 8000  │      │   Port 8001 │      │  Port 8002   │
└───────┬──────┘      └──────┬──────┘      └─────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │    Shared Resources        │
              ├──────────────────────────────┤
              │  Model Cache (best_run2.pt) │
              │  Device: GPU/MPS/CPU       │
              │  Memory: 50-200MB          │
              └──────────────┬──────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        │            ┌───────▼────────┐          │
        │            │  Inference     │          │
        │            │  YOLOv11 Model │          │
        │            └───────┬────────┘          │
        │                    │                    │
        │            ┌───────▼────────┐          │
        │            │  Post-Process  │          │
        │            │  Severity      │          │
        │            │  Scoring       │          │
        │            └────────────────┘          │
        │                                        │
        ▼                                        ▼
┌──────────────────┐                    ┌──────────────────┐
│  File Storage    │                    │  Logging         │
│  - model/weights │                    │  - logs/api.log  │
│  - data/         │                    │  - logs/error.log│
│  - outputs/      │                    │  - metrics       │
└──────────────────┘                    └──────────────────┘
```

---

## Request Flow Diagram

```
┌─────────────────┐
│  Client Request │
│  POST /detect   │
│  (image file)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  FastAPI Endpoint       │
│  detect_damage()        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Input Validation           │
│  ✓ File format              │
│  ✓ File size                │
│  ✓ Image dimensions         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Image Pre-processing       │
│  • Load from bytes          │
│  • Convert RGBA → RGB       │
│  • Resize if needed         │
│  • Save temporary           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Model Inference            │
│  model.predict(image)       │
│  Time: 100-150ms            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Severity Scoring           │
│  • Area severity (50%)      │
│  • Confidence (30%)         │
│  • Location weight (20%)    │
│  Time: 5-10ms               │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Response Formatting        │
│  • Add timestamps           │
│  • Calculate statistics     │
│  • Generate assessment      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  JSON Response              │
│  {                          │
│    "detections": [...],     │
│    "statistics": {...},     │
│    "vehicle_assessment": {} │
│  }                          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────┐
│  Send to Client │
│  HTTP 200 OK    │
└─────────────────┘
```

---

## Deployment Architecture

### Development (Single Process)
```
┌─────────────────────────┐
│   Development Machine   │
│                         │
│  ┌───────────────────┐  │
│  │  uvicorn app      │  │
│  │  --reload         │  │
│  │  Port: 8000       │  │
│  │  Workers: 1       │  │
│  │  Threads: Auto    │  │
│  └───────────────────┘  │
│                         │
│  ✓ Hot reload          │
│  ✓ Debug mode          │
│  ✓ All requests logged │
│                         │
└─────────────────────────┘
```

### Production (Multi-worker)
```
┌──────────────────────────────────────────┐
│     Production Server (Linux)             │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │         Supervisor/Systemd         │  │
│  └───────────┬────────────────────────┘  │
│              │                            │
│  ┌───────────▼──┐  ┌───────────┐         │
│  │  Uvicorn     │  │ Uvicorn   │ ...    │
│  │  Workers: 4  │  │ Workers:4 │         │
│  │  Port 8000   │  │ Port 8001 │         │
│  └──────┬───────┘  └─────┬─────┘         │
│         │                │               │
│         └────────┬───────┘               │
│                  │                       │
│          ┌───────▼─────────┐            │
│          │   Shared Model  │            │
│          │   Cache         │            │
│          └─────────────────┘            │
│                                           │
│  ✓ Load balanced                         │
│  ✓ Auto-restart                         │
│  ✓ Process monitoring                   │
│                                           │
└──────────────────────────────────────────┘
```

### Docker Deployment
```
┌─────────────────────────────────────┐
│      Docker Container               │
│                                     │
│  ┌───────────────────────────────┐  │
│  │    Python 3.11 Environment    │  │
│  │                               │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  FastAPI Application    │  │  │
│  │  │  + Uvicorn Server       │  │  │
│  │  │  (4 workers)            │  │  │
│  │  └─────────────────────────┘  │  │
│  │                               │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Model: best_run2.pt    │  │  │
│  │  │  (Volume mounted)       │  │  │
│  │  └─────────────────────────┘  │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│  Port: 8000 (exposed)               │
│  Memory: 2-4GB                      │
│  CPU: 2-4 cores                     │
│                                     │
└─────────────────────────────────────┘
```

### Docker Compose (Recommended)
```
┌────────────────────────────────────────────┐
│         Docker Compose Stack               │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │         nginx (Port 80/443)          │  │
│  │         Load Balancer                │  │
│  └──────┬─────────────────┬─────────────┘  │
│         │                 │                 │
│  ┌──────▼───┐      ┌──────▼───┐           │
│  │   API    │      │   API    │           │
│  │Container │      │Container │           │
│  │Port 8000 │      │Port 8000 │           │
│  └────┬─────┘      └────┬─────┘           │
│       │                 │                  │
│       └─────────┬───────┘                  │
│               ┌─▼──────────────────────┐  │
│               │   Shared Volumes       │  │
│               │ • model/weights/       │  │
│               │ • data/                │  │
│               │ • outputs/             │  │
│               └────────────────────────┘  │
│                                            │
└────────────────────────────────────────────┘
```

---

## Database Response Schema

```
Detection Result:
{
  "timestamp": "ISO-8601",
  "filename": "string",
  "image_size": {
    "width": int,
    "height": int
  },
  "model": "string (model name)",
  "inference_params": {
    "confidence_threshold": float (0-1),
    "iou_threshold": float (0-1)
  },
  "total_damages": int,
  "detections": [
    {
      "class": "string (damage type)",
      "confidence": float (0-1),
      "combined_severity": float (0-100),
      "severity_level": "LOW|MEDIUM|HIGH|CRITICAL",
      "area_percent": float,
      "area_severity": float (0-100),
      "confidence_severity": float (0-100),
      "location_weight": float (0.6-1.5),
      "bbox": [x1, y1, x2, y2]
    }
  ],
  "statistics": {
    "average_severity": float,
    "max_severity": float,
    "min_severity": float,
    "severity_breakdown": {
      "LOW": int,
      "MEDIUM": int,
      "HIGH": int,
      "CRITICAL": int
    }
  },
  "vehicle_assessment": {
    "average_severity": float,
    "assessment_level": "MINIMAL|MODERATE|SUBSTANTIAL|SEVERE"
  }
}
```

---

## API Scaling Strategy

```
┌──────────────────────────────────────────────────────┐
│              Scaling Considerations                  │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Local Development                                   │
│  └─ 1 process, 8000 req/day, OK                     │
│                                                       │
│  Small Production (AWS t3.medium)                   │
│  └─ 4 workers, ~100,000 req/day                     │
│  └─ Model: 50MB in memory                           │
│  └─ 2GB RAM, 2 vCPU                                 │
│                                                       │
│  Medium Production (AWS t3.large)                   │
│  └─ 8 workers, ~500,000 req/day                     │
│  └─ Model: 50MB in memory per worker                │
│  └─ 8GB RAM, 2 vCPU                                 │
│  └─ GPU optional (3-5x faster)                      │
│                                                       │
│  High Volume (AWS c5.xlarge + GPU)                  │
│  └─ 16 workers, ~5M req/day                         │
│  └─ NVIDIA GPU: 20-50 images/sec                    │
│  └─ Multi-zone deployment with LB                   │
│                                                       │
│  Very High Volume (Kubernetes)                      │
│  └─ Auto-scaling pods                               │
│  └─ Load balancing across zones                     │
│  └─ Model caching layer                             │
│  └─ Request batching optimization                   │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## Performance Metrics

```
┌────────────────────────────────────────┐
│     Performance Characteristics         │
├────────────────────────────────────────┤
│                                         │
│  Latency Breakdown:                    │
│  ├─ Request parse: 1-2ms              │
│  ├─ File upload: Variable             │
│  ├─ Image processing: 5-10ms          │
│  ├─ Model inference: 100-150ms        │
│  ├─ Severity scoring: 5-10ms          │
│  ├─ Response format: 1-2ms            │
│  └─ Total: 120-180ms                  │
│                                         │
│  Throughput:                            │
│  ├─ Single worker: 5-10 req/sec       │
│  ├─ 4 workers: 20-40 req/sec          │
│  ├─ 8 workers: 40-80 req/sec          │
│  └─ With GPU: 2-5x faster             │
│                                         │
│  Resource Usage:                        │
│  ├─ CPU: 10-50% per request           │
│  ├─ Memory: 50-100MB base             │
│  ├─ Per request: 20-50MB              │
│  └─ GPU: 1-2GB (if available)         │
│                                         │
└────────────────────────────────────────┘
```

---

## Monitoring Dashboard

```
┌─────────────────────────────────────────────────────┐
│              API Monitoring Dashboard               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Status: ✅ HEALTHY                                │
│  Uptime: 99.8%                                     │
│  Model: best_run2.pt                               │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Requests per Minute                          │  │
│  │ ▁▂▃▄▅▆▇█▆▅▄▃▂▁▂▃▄▅▆▇█▆▅▄▃▂ 45 req/min       │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Response Times (ms)                          │  │
│  │ Current: 145ms | Avg: 150ms | Max: 280ms    │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Error Rate                                    │  │
│  │ 0.2% (2 errors in last 1000 requests)       │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Server Resources                             │  │
│  │ CPU: 35% | Memory: 2.1GB / 4GB | GPU: 45%  │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  Active Connections: 8                             │
│  Total Processed: 1.2M images                      │
│  Uptime: 45 days                                   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Deployment Timeline

```
Week 1: Development
├─ Day 1: FastAPI setup, basic endpoints
├─ Day 2: Model loading, inference integration
├─ Day 3: Severity scoring, response formatting
├─ Day 4: Docker containerization
└─ Day 5: Documentation, examples

Week 2: Testing & Optimization
├─ Day 1: Load testing, performance tuning
├─ Day 2: Docker Compose, local deployment
├─ Day 3: Security audit, CORS configuration
├─ Day 4: Error handling, logging setup
└─ Day 5: Documentation finalization

Week 3: Deployment
├─ Day 1: Cloud setup (AWS/GCP/Azure)
├─ Day 2: CI/CD pipeline setup
├─ Day 3: Production deployment
├─ Day 4: Monitoring & alerting
└─ Day 5: Performance validation

Ongoing: Maintenance
├─ Monitor logs and metrics
├─ Update dependencies
├─ Fine-tune performance
└─ Add new features
```

---

## Success Criteria

```
✅ All Endpoints Working
   └─ /api/detect
   └─ /api/detect/batch
   └─ /api/detect/url
   └─ /api/models
   └─ /api/model/switch
   └─ /api/health
   └─ /api/config

✅ Performance Targets
   └─ Single image: <200ms
   └─ Batch: <2s per 10 images
   └─ Throughput: >20 req/sec
   └─ Uptime: >99.5%

✅ Quality Standards
   └─ Error rate: <0.5%
   └─ Code coverage: >80%
   └─ Documentation: Complete
   └─ Security: Reviewed

✅ Deployment Success
   └─ Docker: Running
   └─ Docker Compose: Running
   └─ Cloud: Deployed
   └─ Monitoring: Active
```

