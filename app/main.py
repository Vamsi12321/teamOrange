"""
FastAPI CCPA Compliance Detection System
OpenHack 2026 - Production Ready Implementation
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.rules import RuleEngine
from app.model import ModelEngine
from app.llm_engine import LLMEngine
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="CCPA Compliance Detection System")

# Global engines (loaded at startup)
rule_engine = None
model_engine = None
llm_engine = None


@app.on_event("startup")
async def startup_event():
    """Load models and rules at startup"""
    global rule_engine, model_engine, llm_engine
    
    logger.info("Initializing CCPA Detection System...")
    
    # Initialize rule engine (fast)
    rule_engine = RuleEngine()
    logger.info("Rule engine loaded")
    
    # Initialize model engine (may take time)
    model_engine = ModelEngine()
    logger.info("Model engine loaded")
    
    # Initialize LLM engine (optional, controlled by USE_LLM env var)
    llm_engine = LLMEngine()
    if llm_engine.use_llm:
        logger.info("LLM engine loaded")
    else:
        logger.info("LLM engine disabled (set USE_LLM=true to enable)")
    
    logger.info("System ready")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )


@app.get("/metrics")
async def metrics():
    """System metrics and capabilities endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "rules_loaded": len(rule_engine.notice_keywords) > 0 if rule_engine else False,
            "model_loaded": model_engine.model is not None if model_engine else False,
            "sections_supported": 10,
            "device": model_engine.device if model_engine else "none",
            "response_time_target": "<2s",
            "ccpa_sections": [
                "Section 1798.100", "Section 1798.105", "Section 1798.106",
                "Section 1798.110", "Section 1798.115", "Section 1798.120",
                "Section 1798.121", "Section 1798.125", "Section 1798.130",
                "Section 1798.135"
            ]
        }
    )


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Analyze business practice for CCPA compliance
    
    Returns STRICT OpenHack format:
        {"harmful": bool, "articles": List[str]}
    """
    try:
        prompt = request.prompt.strip()
        
        if not prompt:
            return AnalyzeResponse(
                harmful=False, 
                articles=[]
            )
        
        # Step 1: Rule-based detection (fast path)
        rule_violations = rule_engine.detect(prompt)
        if rule_violations:
            logger.info(f"Rule engine detected: {rule_violations}")
        
        # Step 2: Model-based detection (for subtle cases)
        model_violations, model_confidences = model_engine.detect(prompt)
        if model_violations:
            logger.info(f"Model detected: {model_violations}")
            for section, conf in model_confidences.items():
                if conf > 0.5:
                    logger.info(f"  {section}: {conf:.3f}")
        
        # Step 3: LLM-based detection (for context understanding) - OPTIONAL
        llm_violations = []
        if llm_engine and llm_engine.use_llm:
            llm_violations, llm_confidence = llm_engine.detect(prompt)
            if llm_violations:
                logger.info(f"LLM detected: {llm_violations}")
        
        # Step 4: Merge and deduplicate
        all_violations = set(rule_violations + model_violations + llm_violations)
        
        # Step 5: Sort and format
        sorted_violations = sorted(list(all_violations))
        
        # Step 6: Construct response (STRICT FORMAT - no extra fields)
        harmful = len(sorted_violations) > 0
        
        return AnalyzeResponse(
            harmful=harmful,
            articles=sorted_violations if harmful else []
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        # Return safe default on error
        return AnalyzeResponse(
            harmful=False, 
            articles=[]
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
