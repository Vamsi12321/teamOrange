"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import List


class AnalyzeRequest(BaseModel):
    """Request schema for /analyze endpoint"""
    prompt: str


class AnalyzeResponse(BaseModel):
    """Response schema for /analyze endpoint - STRICT OpenHack format"""
    harmful: bool
    articles: List[str]
