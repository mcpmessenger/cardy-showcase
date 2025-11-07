"""Request models for API endpoints."""
from pydantic import BaseModel
from typing import Optional, List


class TTSRequest(BaseModel):
    """Text-to-speech request."""
    text: str
    voice_id: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request."""
    message: str
    conversation_id: Optional[str] = None
    history: Optional[List[dict]] = None


class ProductSearchRequest(BaseModel):
    """Product search request."""
    query: str
    max_price: Optional[float] = None
    category: Optional[str] = None

