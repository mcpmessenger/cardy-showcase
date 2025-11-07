"""Response models for API endpoints."""
from pydantic import BaseModel
from typing import Optional, List, Any


class STTResponse(BaseModel):
    """Speech-to-text response."""
    text: str


class TTSResponse(BaseModel):
    """Text-to-speech response."""
    audio_url: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded


class ChatResponse(BaseModel):
    """Chat response."""
    text: str
    conversation_id: Optional[str] = None
    tools_used: Optional[List[str]] = None
    products: Optional[List[dict]] = None  # Product data when products are found


class ProductSearchResponse(BaseModel):
    """Product search response."""
    products: List[dict]
    count: int

