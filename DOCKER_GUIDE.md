# Docker Deployment Guide

## Quick Start

### Build the Image
```powershell
.\build_docker.bat
```

Or manually:
```powershell
docker build -t ccpa-detector:latest .
```

### Run the Container
```powershell
docker run -d -p 8000:8000 --name ccpa-detector ccpa-detector:latest
```

### With GPU Support (OpenHack requirement)
```powershell
docker run -d -p 8000:8000 --gpus all --name ccpa-detector ccpa-detector:latest
```

---

## Docker Commands

### Build
```powershell
docker build -t ccpa-detector:latest .
```

### Run
```powershell
# Basic
docker run -d -p 8000:8000 --name ccpa-detector ccpa-detector:latest

# With GPU
docker run -d -p 8000:8000 --gpus all --name ccpa-detector ccpa-detector:latest

# With custom port
docker run -d -p 9000:8000 --name ccpa-detector ccpa-detector:latest
```

### Manage
```powershell
# Stop
docker stop ccpa-detector

# Start
docker start ccpa-detector

# Restart
docker restart ccpa-detector

# Remove
docker rm ccpa-detector

# View logs
docker logs ccpa-detector

# Follow logs
docker logs -f ccpa-detector

# Check status
docker ps
```

### Test
```powershell
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics

# Test detection
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d "{\"prompt\": \"We refuse to delete user data\"}"
```

---

## Save/Load Image

### Save to File
```powershell
docker save ccpa-detector:latest -o ccpa-detector.tar
```

### Compress (optional)
```powershell
# PowerShell
Compress-Archive -Path ccpa-detector.tar -DestinationPath ccpa-detector.zip
```

### Load from File
```powershell
docker load -i ccpa-detector.tar
```

---

## Image Details

**Size:** ~2-3 GB (includes model files)

**Contents:**
- Python 3.10
- FastAPI application
- Fine-tuned DistilBERT model (6092 examples)
- All dependencies

**Exposed Port:** 8000

**Health Check:** Every 30 seconds at `/health`

---

## Troubleshooting

### Docker not running
```
ERROR: Docker is not running
```
**Solution:** Start Docker Desktop

### Port already in use
```
ERROR: port is already allocated
```
**Solution:** Use different port or stop existing container
```powershell
docker stop ccpa-detector
# Or use different port
docker run -d -p 9000:8000 --name ccpa-detector ccpa-detector:latest
```

### Out of memory
```
ERROR: failed to build
```
**Solution:** Increase Docker memory limit in Docker Desktop settings (recommend 4GB+)

### Model not found
```
ERROR: Model loading failed
```
**Solution:** Ensure `ccpa_model_multilabel/` exists before building
```powershell
dir ccpa_model_multilabel
```

---

## OpenHack Submission

For OpenHack, use:
```powershell
docker run -d -p 8000:8000 --gpus all --name ccpa-detector ccpa-detector:latest
```

The `--gpus all` flag is required by OpenHack even if you don't have GPU.

---

## Production Deployment

### Environment Variables
```powershell
docker run -d -p 8000:8000 \
  -e USE_LLM=false \
  -e LOG_LEVEL=INFO \
  --name ccpa-detector \
  ccpa-detector:latest
```

### Volume Mount (for logs)
```powershell
docker run -d -p 8000:8000 \
  -v ${PWD}/logs:/app/logs \
  --name ccpa-detector \
  ccpa-detector:latest
```

### Resource Limits
```powershell
docker run -d -p 8000:8000 \
  --memory="2g" \
  --cpus="2" \
  --name ccpa-detector \
  ccpa-detector:latest
```

---

## Sharing the Image

### Option 1: Docker Hub (Public)
```powershell
# Tag
docker tag ccpa-detector:latest yourusername/ccpa-detector:latest

# Push
docker push yourusername/ccpa-detector:latest

# Others can pull
docker pull yourusername/ccpa-detector:latest
```

### Option 2: File Transfer (Private)
```powershell
# Save
docker save ccpa-detector:latest -o ccpa-detector.tar

# Compress
Compress-Archive -Path ccpa-detector.tar -DestinationPath ccpa-detector.zip

# Send ccpa-detector.zip to recipient

# Recipient loads
docker load -i ccpa-detector.tar
docker run -d -p 8000:8000 --name ccpa-detector ccpa-detector:latest
```

---

## Performance

**Startup Time:** ~10-15 seconds
**Response Time:** ~1-2 seconds per request
**Memory Usage:** ~1-2 GB
**CPU Usage:** Low (model inference on CPU)

---

## Next Steps

1. Build image: `.\build_docker.bat`
2. Test locally: `docker run -d -p 8000:8000 ccpa-detector:latest`
3. Verify: `curl http://localhost:8000/health`
4. Submit to OpenHack with `--gpus all` flag
