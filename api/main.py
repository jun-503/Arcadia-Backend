"""
FastAPI application for YOLOv11 Damage Detection with Severity Scoring.

Endpoints:
- POST /api/detect - Upload image and get damage detections with severity scores
- GET /api/health - Health check endpoint
- GET /api/models - List available models
- POST /api/detect/batch - Batch inference on multiple images
- GET /api/config - Get current configuration
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
import os
import json
import logging
from datetime import datetime
from pathlib import Path
import tempfile
from typing import Optional, List

from PIL import Image
import numpy as np

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from model.yolov11 import YOLOv11DamageDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="YOLOv11 Damage Detection API",
    description="Detect car damage and calculate severity scores using YOLOv11",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance (loaded once at startup)
model_instance = None
MODEL_CACHE = {}
CURRENT_MODEL = "best_run2.pt"

# Configuration
CONFIG = {
    "confidence_threshold": 0.25,
    "iou_threshold": 0.45,
    "max_image_size": 1024,  # Max width/height
    "max_file_size_mb": 50,
    "supported_formats": ["jpg", "jpeg", "png", "bmp", "gif"],
    "device": "mps"  # or "cuda", "cpu"
}


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    global model_instance
    try:
        logger.info(f"Loading model: {CURRENT_MODEL}")
        model_instance = YOLOv11DamageDetector(model_name=CURRENT_MODEL)
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model_instance is not None,
        "current_model": CURRENT_MODEL
    }


@app.get("/api/models")
async def list_models():
    """List available models in model/weights/"""
    weights_dir = Path(__file__).parent.parent / "model" / "weights"
    
    if not weights_dir.exists():
        return {"models": [], "message": "Weights directory not found"}
    
    models = [f.name for f in weights_dir.glob("*.pt")]
    
    return {
        "available_models": models,
        "current_model": CURRENT_MODEL,
        "count": len(models)
    }


@app.get("/api/config")
async def get_config():
    """Get current API configuration"""
    return {
        "config": CONFIG,
        "current_model": CURRENT_MODEL,
        "max_file_size_mb": CONFIG["max_file_size_mb"],
        "supported_formats": CONFIG["supported_formats"]
    }


@app.post("/api/detect")
async def detect_damage(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0.0, le=1.0),
    iou: float = Query(0.45, ge=0.0, le=1.0),
    return_image: bool = Query(True),
):
    """
    Detect car damage with severity scoring.
    
    Args:
        file: Image file (jpg, png, etc.)
        confidence: Confidence threshold (0-1)
        iou: IOU threshold (0-1)
        return_image: Whether to return annotated image
    
    Returns:
        JSON with detections and optionally annotated image
    """
    if model_instance is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Validate file format
        filename = file.filename.lower()
        file_ext = filename.split('.')[-1]
        if file_ext not in CONFIG["supported_formats"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Supported: {CONFIG['supported_formats']}"
            )
        
        # Read image file
        contents = await file.read()
        
        # Validate file size
        file_size_mb = len(contents) / (1024 * 1024)
        if file_size_mb > CONFIG["max_file_size_mb"]:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max: {CONFIG['max_file_size_mb']}MB"
            )
        
        # Load image
        image = Image.open(io.BytesIO(contents))
        
        # Convert RGBA to RGB if needed
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # Resize if too large
        max_size = CONFIG["max_image_size"]
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            logger.info(f"Resized image to {image.size}")
        
        # Save temporarily for inference
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            image.save(tmp.name, format='JPEG')
            tmp_path = tmp.name
        
        try:
            # Run inference
            logger.info(f"Running inference on {filename}")
            detections, output_image = model_instance.predict(
                image_path=tmp_path,
                conf=confidence,
                iou=iou,
                visualize=return_image
            )
            
            # Prepare response
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "filename": filename,
                "image_size": {"width": image.width, "height": image.height},
                "model": CURRENT_MODEL,
                "inference_params": {
                    "confidence_threshold": confidence,
                    "iou_threshold": iou
                },
                "total_damages": len(detections),
                "detections": detections
            }
            
            # Calculate stats
            if detections:
                severities = [d["combined_severity"] for d in detections]
                severity_levels = [d["severity_level"] for d in detections]
                
                response_data["statistics"] = {
                    "average_severity": round(np.mean(severities), 2),
                    "max_severity": round(max(severities), 2),
                    "min_severity": round(min(severities), 2),
                    "severity_breakdown": {
                        "LOW": severity_levels.count("LOW"),
                        "MEDIUM": severity_levels.count("MEDIUM"),
                        "HIGH": severity_levels.count("HIGH"),
                        "CRITICAL": severity_levels.count("CRITICAL")
                    }
                }
                
                # Vehicle assessment
                avg_sev = response_data["statistics"]["average_severity"]
                if avg_sev < 20:
                    assessment = "MINIMAL"
                elif avg_sev < 50:
                    assessment = "MODERATE"
                elif avg_sev < 75:
                    assessment = "SUBSTANTIAL"
                else:
                    assessment = "SEVERE"
                
                response_data["vehicle_assessment"] = {
                    "average_severity": avg_sev,
                    "assessment_level": assessment
                }
            
            # Save annotated image if requested
            if return_image and output_image is not None:
                img_buffer = io.BytesIO()
                if output_image.mode == 'RGBA':
                    output_image = output_image.convert('RGB')
                output_image.save(img_buffer, format='JPEG', quality=85)
                img_buffer.seek(0)
                
                # Save to temp file and create file response
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_out:
                    output_image.save(tmp_out.name, format='JPEG', quality=85)
                    response_data["annotated_image_path"] = tmp_out.name
            
            logger.info(f"✅ Inference complete: {len(detections)} damages detected")
            return JSONResponse(content=response_data, status_code=200)
        
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error during inference: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.post("/api/detect/batch")
async def detect_batch(
    files: List[UploadFile] = File(...),
    confidence: float = Query(0.25, ge=0.0, le=1.0),
    iou: float = Query(0.45, ge=0.0, le=1.0),
):
    """
    Batch inference on multiple images.
    
    Args:
        files: List of image files
        confidence: Confidence threshold
        iou: IOU threshold
    
    Returns:
        JSON with results for all images
    """
    if model_instance is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(files) > 100:
        raise HTTPException(status_code=400, detail="Max 100 images per batch")
    
    results = []
    errors = []
    
    logger.info(f"Processing batch of {len(files)} images")
    
    for idx, file in enumerate(files):
        try:
            # Read image
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # Save temporarily
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                image.save(tmp.name, format='JPEG')
                tmp_path = tmp.name
            
            try:
                # Run inference
                detections, _ = model_instance.predict(
                    image_path=tmp_path,
                    conf=confidence,
                    iou=iou,
                    visualize=False  # Skip image for batch to save memory
                )
                
                result = {
                    "image_index": idx,
                    "filename": file.filename,
                    "status": "success",
                    "total_damages": len(detections),
                    "detections": detections
                }
                
                if detections:
                    severities = [d["combined_severity"] for d in detections]
                    result["average_severity"] = round(np.mean(severities), 2)
                
                results.append(result)
                logger.info(f"✅ Image {idx+1}/{len(files)}: {len(detections)} damages")
            
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        except Exception as e:
            error = {
                "image_index": idx,
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            }
            errors.append(error)
            logger.error(f"❌ Error processing {file.filename}: {str(e)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "batch_size": len(files),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors if errors else None
    }


@app.post("/api/detect/url")
async def detect_from_url(
    image_url: str = Query(...),
    confidence: float = Query(0.25, ge=0.0, le=1.0),
    iou: float = Query(0.45, ge=0.0, le=1.0),
):
    """
    Detect damage from URL.
    Note: Requires 'requests' library
    """
    try:
        import requests
        
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        image = Image.open(io.BytesIO(response.content))
        
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            image.save(tmp.name, format='JPEG')
            tmp_path = tmp.name
        
        try:
            detections, output_image = model_instance.predict(
                image_path=tmp_path,
                conf=confidence,
                iou=iou,
                visualize=True
            )
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "source_url": image_url,
                "total_damages": len(detections),
                "detections": detections,
                "model": CURRENT_MODEL
            }
            
            if detections:
                severities = [d["combined_severity"] for d in detections]
                result["average_severity"] = round(np.mean(severities), 2)
            
            return result
        
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="requests library not installed. Install with: pip install requests"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process URL: {str(e)}")


@app.post("/api/model/switch")
async def switch_model(model_name: str = Query(...)):
    """
    Switch to a different model.
    
    Args:
        model_name: Name of model file in model/weights/
    """
    global model_instance, CURRENT_MODEL
    
    try:
        # Check if model exists
        weights_dir = Path(__file__).parent.parent / "model" / "weights"
        model_path = weights_dir / model_name
        
        if not model_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Model not found: {model_name}"
            )
        
        logger.info(f"Switching to model: {model_name}")
        model_instance = YOLOv11DamageDetector(model_name=model_name)
        CURRENT_MODEL = model_name
        
        logger.info(f"✅ Successfully switched to {model_name}")
        return {
            "status": "success",
            "current_model": CURRENT_MODEL,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error switching model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model switch error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "title": "YOLOv11 Damage Detection API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "GET /api/health",
            "detect": "POST /api/detect",
            "batch": "POST /api/detect/batch",
            "from_url": "POST /api/detect/url",
            "models": "GET /api/models",
            "switch_model": "POST /api/model/switch",
            "config": "GET /api/config"
        }
    }


if __name__ == "__main__":
    # Run with: python api/main.py
    # Or with: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
