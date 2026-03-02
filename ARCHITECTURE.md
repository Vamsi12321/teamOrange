# System Architecture

## High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Application                       │
│                  (curl, Postman, Web App)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server (Port 8000)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Endpoints:                                          │   │
│  │  • GET  /health  → Health Check                      │   │
│  │  • POST /analyze → CCPA Violation Detection          │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Request Processing Pipeline                │
│                                                               │
│  1. Input Validation (Pydantic)                              │
│     └─> Validate JSON structure                              │
│                                                               │
│  2. Parallel Detection                                       │
│     ├─> Rule Engine (Fast Path)                              │
│     │   • Keyword matching                                   │
│     │   • Pattern recognition                                │
│     │   • Synonym resolution                                 │
│     │   • ~10ms latency                                      │
│     │                                                         │
│     └─> Model Engine (Subtle Cases)                          │
│         • Heuristic detection                                │
│         • Implicit violations                                │
│         • ~100-500ms latency                                 │
│                                                               │
│  3. Aggregation & Deduplication                              │
│     └─> Merge results, sort sections                         │
│                                                               │
│  4. Response Formatting                                      │
│     └─> Construct JSON response                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Server (`app/main.py`)

**Responsibilities**:
- HTTP request handling
- Model preloading at startup
- Error handling and safe defaults
- Health monitoring

**Key Features**:
- Async request processing
- Startup event for model loading
- Graceful error recovery
- Structured logging

### 2. Rule Engine (`app/rules.py`)

**Detection Strategy**:
```python
# Keyword-based detection
keywords = {
    "Section 1798.100": ["no notice", "without informing", ...],
    "Section 1798.105": ["refuse to delete", "deny deletion", ...],
    ...
}

# Pattern-based detection
patterns = [
    r'(sell|share).*(without|no).*(notice|consent)',
    r'(minor|child).*(sell|share)',
    ...
]
```

**Performance**:
- O(n) complexity where n = prompt length
- ~10ms average latency
- No external dependencies
- 100% deterministic

### 3. Model Engine (`app/model.py`)

**Architecture**:
```
Input Text
    ↓
Tokenization (DistilBERT tokenizer)
    ↓
Heuristic Analysis
    ↓
Violation Detection
    ↓
Section Mapping
```

**Model Specs**:
- Model: DistilBERT-base-uncased
- Parameters: 66M (well under 8B limit)
- Memory: ~500MB
- Inference: 100-500ms (CPU), 10-50ms (GPU)

**Fallback Strategy**:
- If model fails to load → Use rule-based only
- If inference fails → Return empty list
- System never crashes due to model issues

### 4. Data Flow

```
POST /analyze
    │
    ├─> Validate Request Schema
    │   └─> {"prompt": "..."}
    │
    ├─> Rule Engine Detection
    │   └─> ["Section 1798.100", "Section 1798.120"]
    │
    ├─> Model Engine Detection
    │   └─> ["Section 1798.125"]
    │
    ├─> Merge & Deduplicate
    │   └─> {"Section 1798.100", "Section 1798.120", "Section 1798.125"}
    │
    ├─> Sort Sections
    │   └─> ["Section 1798.100", "Section 1798.120", "Section 1798.125"]
    │
    └─> Format Response
        └─> {
              "harmful": true,
              "articles": ["Section 1798.100", "Section 1798.120", "Section 1798.125"]
            }
```

## CCPA Section Mapping

| Section | Keywords | Patterns |
|---------|----------|----------|
| 1798.100 | no notice, without informing | collect.*without.*notice |
| 1798.105 | refuse to delete, deny deletion | delete.*refuse |
| 1798.106 | refuse to correct, deny correction | correct.*deny |
| 1798.110 | refuse to disclose, deny access | - |
| 1798.115 | not disclose sale, hide sale | - |
| 1798.120 | no opt out, cannot opt out | opt.*out.*refuse |
| 1798.121 | sensitive + sale | (minor\|child).*(sell\|share) |
| 1798.125 | charge more, discriminate | opt.*out.*price |
| 1798.130 | no response, ignore request | - |
| 1798.135 | no link, no do not sell | - |

## Deployment Architecture

### Single Container Deployment

```
┌─────────────────────────────────┐
│      Docker Container           │
│  ┌───────────────────────────┐  │
│  │   FastAPI Application     │  │
│  │   (Port 8000)             │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │   Rule Engine             │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │   Model Engine            │  │
│  │   (DistilBERT)            │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### Production Deployment (Scalable)

```
                    ┌─────────────┐
                    │ Load Balancer│
                    │  (nginx/ALB) │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  Container 1  │  │  Container 2  │  │  Container 3  │
│  Port 8000    │  │  Port 8000    │  │  Port 8000    │
└───────────────┘  └───────────────┘  └───────────────┘
```

## Performance Optimization

### Startup Optimization
1. Model preloading at startup (not per request)
2. Lazy loading for optional components
3. Connection pooling for external services

### Runtime Optimization
1. Rule engine runs first (fast path)
2. Model engine runs in parallel
3. Results cached for identical prompts (optional)

### Memory Optimization
1. Model loaded once, shared across requests
2. Efficient tokenization
3. Garbage collection tuning

## Error Handling Strategy

```python
try:
    # Primary detection logic
    violations = detect_violations(prompt)
except ModelError:
    # Fallback to rule-based only
    violations = rule_engine.detect(prompt)
except Exception:
    # Safe default: no violations detected
    return {"harmful": false, "articles": []}
```

## Monitoring & Observability

### Key Metrics
- Request latency (p50, p95, p99)
- Error rate
- Model inference time
- Rule engine execution time
- Memory usage
- CPU/GPU utilization

### Logging
```python
logger.info(f"Request received: {prompt[:50]}...")
logger.info(f"Rule violations: {rule_violations}")
logger.info(f"Model violations: {model_violations}")
logger.info(f"Response time: {elapsed:.2f}s")
```

## Security Considerations

### Input Validation
- Max prompt length: 10,000 characters
- Sanitize special characters
- Rate limiting per IP

### Output Validation
- Strict JSON schema enforcement
- No PII in responses
- No model internals exposed

### API Security
- HTTPS only in production
- API key authentication
- CORS configuration
- Request signing

## Scalability

### Horizontal Scaling
- Stateless design (no session storage)
- Load balancer distribution
- Auto-scaling based on CPU/memory

### Vertical Scaling
- GPU acceleration for model inference
- Multi-core CPU utilization
- Memory optimization

### Caching Strategy
```python
# Optional: Cache identical prompts
cache = {
    hash(prompt): response
}
```

## Testing Strategy

### Unit Tests
- Rule engine keyword matching
- Pattern recognition
- Response formatting

### Integration Tests
- End-to-end API tests
- Model loading tests
- Error handling tests

### Load Tests
```bash
ab -n 1000 -c 50 http://localhost:8000/analyze
```

## Future Enhancements

1. **Fine-tuned Model**: Train on CCPA-specific dataset
2. **Confidence Scores**: Add probability to each violation
3. **Explanation Generation**: Explain why violation detected
4. **Batch Processing**: Analyze multiple prompts at once
5. **Multi-language Support**: Detect violations in other languages
6. **Real-time Learning**: Update rules based on feedback
7. **API Versioning**: Support multiple API versions
8. **Webhook Support**: Push notifications for violations

## Resource Requirements

### Minimum
- CPU: 2 cores
- RAM: 2GB
- Disk: 5GB
- Network: 1 Mbps

### Recommended
- CPU: 4 cores
- RAM: 4GB
- Disk: 10GB
- Network: 10 Mbps

### Optimal (with GPU)
- CPU: 8 cores
- RAM: 8GB
- GPU: NVIDIA T4 or better
- Disk: 20GB
- Network: 100 Mbps

## Compliance & Audit

### Logging Requirements
- All requests logged with timestamp
- All responses logged
- Model version tracked
- Rule version tracked

### Audit Trail
```json
{
  "timestamp": "2026-03-01T12:00:00Z",
  "request_id": "uuid",
  "prompt": "...",
  "violations": ["Section 1798.100"],
  "model_version": "distilbert-base-uncased",
  "rule_version": "1.0.0"
}
```
