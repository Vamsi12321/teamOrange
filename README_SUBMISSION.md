# CCPA Compliance Detection System

OpenHack 2026 Submission

[![Demo Video](https://img.shields.io/badge/Demo-Video-red?style=for-the-badge&logo=youtube)](https://docs.google.com/videos/d/1UjOMXShO_XvnEVu4j4ZQDemIrxcas80N90Qw93MdpPw/play?pli=1)
[![Presentation](https://img.shields.io/badge/Presentation-Slides-blue?style=for-the-badge&logo=google)](https://docs.google.com/presentation/d/1TzX78DZCp5izRqiDbnLNQMVsLTO78k49v9PT3BNSqOk/edit?usp=sharing)

> AI-powered CCPA violation detection using hybrid architecture (Rules + Fine-tuned ML + Optional LLM)

---

## 📚 Resources

- **Demo Video:** [Watch System in Action](https://docs.google.com/videos/d/1UjOMXShO_XvnEVu4j4ZQDemIrxcas80N90Qw93MdpPw/play?pli=1)
- **Presentation:** [View Technical Slides](https://docs.google.com/presentation/d/1TzX78DZCp5izRqiDbnLNQMVsLTO78k49v9PT3BNSqOk/edit?usp=sharing)

---

## 🚀 Quick Start

### Run Container
```bash
docker run -d -p 8000:8000 ccpa-detector
```

**Note:** The system auto-detects GPU availability. If GPU is present, it will be used automatically. No `--gpus` flag needed.

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Test violation detection
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We refuse to delete user data"}'

# Test safe practice
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We comply with all CCPA requirements and honor deletion requests"}'
```

---

## 📊 Expected Response

### Violation Detected
```json
{
  "harmful": true,
  "articles": ["Section 1798.105"]
}
```

### No Violation
```json
{
  "harmful": false,
  "articles": []
}
```

### Multiple Violations
```json
{
  "harmful": true,
  "articles": ["Section 1798.105", "Section 1798.125"]
}
```

---

## 🔌 API Endpoints

### POST /analyze
Detects CCPA violations in business practices.

**Request:**
```json
{
  "prompt": "Business practice description"
}
```

**Response:**
```json
{
  "harmful": boolean,
  "articles": ["Section 1798.XXX", ...]
}
```

**Example Violations:**
- "We refuse to delete user data" → Section 1798.105
- "We don't tell users what data we collect" → Section 1798.100
- "Users cannot opt out of data sales" → Section 1798.120
- "We charge more to users who opt out" → Section 1798.125

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### GET /metrics
System capabilities and metadata.

**Response:**
```json
{
  "rules_loaded": true,
  "model_loaded": true,
  "sections_supported": 10,
  "device": "cpu",
  "response_time_target": "<2s",
  "ccpa_sections": ["Section 1798.100", ...]
}
```

---

## 🏗️ System Architecture

**3-Layer Hybrid Detection System:**

```
Input Text
    ↓
┌─────────────────────────────────────┐
│  Layer 1: Rule Engine (Fast)       │
│  - Keyword matching                 │
│  - Pattern detection                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 2: ML Model (Intelligent)    │
│  - Fine-tuned DistilBERT            │
│  - Multi-label classification       │
│  - 6,092 training examples          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 3: LLM (Optional)            │
│  - Phi-2 (2.7B params)              │
│  - Advanced reasoning               │
│  - Disabled by default              │
└─────────────────────────────────────┘
    ↓
Combined Results → Final Output
```

**Why Hybrid?**
- **Rules:** Fast, handles explicit violations
- **ML Model:** Intelligent, handles subtle/complex cases
- **LLM:** Advanced reasoning for edge cases (optional)

---

## 📋 CCPA Sections Detected

| Section | Description | Example Violation |
|---------|-------------|-------------------|
| **1798.100** | Notice at Collection | "We collect data without informing users" |
| **1798.105** | Right to Delete | "We refuse to delete user data" |
| **1798.106** | Right to Correct | "Users cannot correct their information" |
| **1798.110** | Right to Know (Collected) | "We don't disclose what data we collect" |
| **1798.115** | Right to Know (Sold/Shared) | "We hide the fact that we sell data" |
| **1798.120** | Right to Opt-Out | "Users cannot opt out of data sales" |
| **1798.121** | Sensitive Personal Info | "We sell children's data without consent" |
| **1798.125** | Non-Discrimination | "We charge more to users who opt out" |
| **1798.130** | Response Requirements | "We take months to respond to requests" |
| **1798.135** | Do Not Sell Link | "Our website has no Do Not Sell link" |

---

## 🎯 Key Features

### 1. Multi-Label Classification
- Detects multiple violations in a single text
- Each CCPA section is evaluated independently
- More accurate than single-label approaches

### 2. Fine-Tuned Model
- **Base:** DistilBERT (66M parameters)
- **Training:** 6,092 examples, 5 epochs
- **Loss:** 0.6257 → 0.007 (excellent convergence)
- **Accuracy:** 95-100% expected

### 3. False Positive Prevention
- Smart filtering with 60+ positive compliance indicators
- Skips model prediction for obviously compliant statements
- Examples: "allows users", "respects", "verified", "complies"

### 4. Configurable Threshold
- Current: 0.75 (75% confidence required)
- Balances precision vs recall
- Tunable for different use cases

### 5. Auto GPU/CPU Detection
- Automatically uses GPU if available
- Falls back to CPU if not
- No configuration needed

---

## 🔧 Technical Details

### Model
- **Architecture:** DistilBERT (Transformer-based)
- **Parameters:** 66 million
- **Training Data:** 6,092 examples
  - 2,000 single-violation examples
  - 200 multi-violation examples
  - 400 safe practice examples
  - 1,000 natural language edge cases
  - 1,000 contrast pairs
  - 992 realistic business practices
  - 500 questions/hypotheticals

### Performance
- **Response Time:** ~1-2 seconds per request
- **Startup Time:** ~10-15 seconds
- **Memory Usage:** ~1-2 GB
- **Device:** Auto-detects GPU/CPU

### Training
- **Optimizer:** AdamW
- **Learning Rate:** 2e-5
- **Batch Size:** 16
- **Epochs:** 5
- **Loss Function:** BCEWithLogitsLoss (multi-label)

---

## 🛠️ Build Instructions (Optional)

If you need to rebuild the image:

```bash
# Clone or extract the submission
cd ccpa-detector

# Build Docker image
docker build -t ccpa-detector .

# Run container
docker run -d -p 8000:8000 ccpa-detector

# Test
curl http://localhost:8000/health
```

### Training Your Own Model

The trained model files are not included in this repository due to size constraints (~260MB).

**Option 1: Train from scratch**
```bash
# Generate training data
python generate_training_data.py

# Train model (takes ~3 hours)
python train_2k_model.py --data ccpa_training_data_6600.json --epochs 5 --output ./ccpa_model_multilabel

# Model will be saved to ./ccpa_model_multilabel/
```

**Option 2: Use pre-trained model**
- Download from submission package
- Extract to `ccpa_model_multilabel/` directory
- Rebuild Docker image

---

## 📦 Requirements

- **Docker:** Any recent version
- **Port:** 8000 (configurable)
- **GPU:** Optional (auto-detected)
- **Disk Space:** ~2-3 GB for Docker image
- **Memory:** ~1-2 GB RAM

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Check if port 8000 is already in use
docker ps

# Use different port if needed
docker run -d -p 9000:8000 ccpa-detector
curl http://localhost:9000/health
```

### View logs
```bash
# Get container ID
docker ps

# View logs
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>
```

### Stop container
```bash
docker stop <container_id>
docker rm <container_id>
```

### Check system status
```bash
# Health check
curl http://localhost:8000/health

# System metrics
curl http://localhost:8000/metrics
```

---

## 🧪 Testing Examples

### Violations
```bash
# Deletion violation
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We refuse to delete user data"}'

# Notice violation
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We collect data without informing users"}'

# Opt-out violation
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Users cannot opt out of data sales"}'

# Multiple violations
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We refuse to delete data and charge more to users who opt out"}'
```

### Safe Practices
```bash
# Compliant practice
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We comply with all CCPA requirements"}'

# Proper deletion
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We honor all deletion requests within 45 days"}'

# Proper opt-out
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Users can easily opt out of data sales"}'
```

---

## 🏆 Competitive Advantages

1. **Hybrid Architecture** - Combines speed (rules) with intelligence (ML)
2. **Large Training Dataset** - 6,092 examples vs typical 100-500
3. **Multi-Label Classification** - Handles complex multi-violation cases
4. **False Positive Prevention** - Smart filtering reduces errors
5. **Production Ready** - Docker, health checks, monitoring
6. **Fast Response** - 1-2 seconds (competitive requirement)
7. **Comprehensive Coverage** - All 10 CCPA sections
8. **Auto GPU/CPU** - Works on any hardware

---

## 📄 License

OpenHack 2026 Submission

---

## 👥 Author

Vamsi Vakada

---

## 📞 Support

For issues or questions:
1. Check the [Demo Video](https://docs.google.com/videos/d/1UjOMXShO_XvnEVu4j4ZQDemIrxcas80N90Qw93MdpPw/play?pli=1)
2. Review the [Presentation Slides](https://docs.google.com/presentation/d/1TzX78DZCp5izRqiDbnLNQMVsLTO78k49v9PT3BNSqOk/edit?usp=sharing)
3. Review the troubleshooting section above
4. Check Docker logs: `docker logs <container_id>`

---

**Built with ❤️ for OpenHack 2026**
