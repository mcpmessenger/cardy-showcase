"""FastAPI application entry point."""
import logging
import tempfile
import os
import base64

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from mangum import Mangum

from app.config import settings
from app.models.request import TTSRequest, ChatRequest
from app.models.response import STTResponse, TTSResponse, ChatResponse
from app.mcp.client import execute_mcp_command
from app.services.llm import llm_service
from app.services.tool_executor import tool_executor
from app.services.stt_fallback import transcribe_with_openai
from app.services.tts_fallback import synthesize_with_elevenlabs
from app.services.tts_fallback_gtts import synthesize_with_gtts
from app.services.api_key_manager import api_key_manager
from app.tools.product_search import search_products, add_to_cart
from app.tools.grokipedia import grokipedia_search
from app.tools.alpha_vantage import alpha_vantage_market_data
from app.tools.polymarket import polymarket_market_data
from app.tools.schemas import TOOLS_SCHEMA

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="tubbyAI Assistant API",
    description="AI Assistant API with voice, chat, and e-commerce capabilities",
    version="1.0.0"
)

# CORS middleware
cors_origins = settings.cors_origins_list
allow_all_origins = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else cors_origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Lambda handler (via Mangum)
handler = Mangum(app)

# Register tools
tool_executor.register_tool("search_products", search_products)
tool_executor.register_tool("add_to_cart", add_to_cart)
tool_executor.register_tool("grokipedia_search", grokipedia_search)
tool_executor.register_tool("alpha_vantage_market_data", alpha_vantage_market_data)
tool_executor.register_tool("polymarket_market_data", polymarket_market_data)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "tubbyAI Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health or /api/health",
            "chat": "POST /api/chat",
            "stt": "POST /api/stt/transcribe",
            "tts": "POST /api/tts/synthesize",
            "products": "GET /api/products/search?query=..."
        },
        "docs": "/docs (Swagger UI)"
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "tubbyAI Assistant API",
        "version": "1.0.0"
    }


@app.post("/api/stt/transcribe", response_model=STTResponse)
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe audio using MCP-STT service (Whisper).
    
    Args:
        audio_file: Audio file to transcribe (webm, mp3, wav)
    
    Returns:
        Transcribed text
    """
    # Validate file type
    allowed_types = ["audio/webm", "audio/mpeg", "audio/wav", "audio/mp3"]
    content_type = (audio_file.content_type or "").split(";")[0].strip().lower()

    if content_type not in allowed_types:
        logger.warning(f"Invalid audio format: {audio_file.content_type}")
        raise HTTPException(
            400,
            f"Invalid audio format '{audio_file.content_type}'. Allowed: {allowed_types}"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Try MCP-STT first, fallback to OpenAI Whisper if MCP not available
        transcript = None
        mcp_error = None
        use_mcp = getattr(settings, "enable_mcp_stt", False)
        
        # Try MCP-STT service if enabled
        if use_mcp:
            try:
                file_url = f"file://{tmp_path}"
                logger.info("Calling MCP-STT for transcription")
                result = execute_mcp_command(
                    service=settings.mcp_stt_service,
                    action="transcribe",
                    file_url=file_url
                )
                
                if "error" not in result:
                    transcript = result.get("text", result.get("transcript", ""))
                    if transcript:
                        logger.info("Transcription successful via MCP-STT")
            except Exception as e:
                mcp_error = str(e)
                logger.warning(f"MCP-STT failed: {mcp_error}")
        else:
            mcp_error = "MCP STT disabled"
        
        # Use OpenAI Whisper when MCP disabled or unavailable
        if not transcript:
            logger.info("Using OpenAI Whisper for transcription")
            
            try:
                transcript = transcribe_with_openai(tmp_path)
                logger.info(f"Whisper transcription successful: {len(transcript)} characters")
            except Exception as e:
                logger.error(f"Whisper transcription failed: {e}")
                raise HTTPException(
                    500,
                    f"Transcription failed: {str(e)}. "
                    f"Please check your OPENAI_API_KEY is valid and has access to Whisper API."
                )
        
        return STTResponse(text=transcript)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Transcription error")
        raise HTTPException(500, f"Transcription error: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/tts/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech using MCP-TTS service (Eleven Labs).
    
    Args:
        request: TTS request with text and optional voice_id
    
    Returns:
        Audio data or URL
    """
    try:
        logger.info(f"Synthesizing speech for text length: {len(request.text)}")
        
        # Try MCP-TTS first, fallback to Eleven Labs if MCP not available
        audio_data_bytes = None
        mcp_error = None
        result = {}
        
        # Try MCP-TTS service
        try:
            result = execute_mcp_command(
                service=settings.mcp_tts_service,
                action="synthesize",
                text=request.text,
                voice_id=request.voice_id or settings.eleven_labs_voice_id or "default"
            )
            
            if "error" not in result:
                audio_data = result.get("audio_data")  # Base64 encoded
                audio_url = result.get("audio_url")
                
                if audio_data:
                    # Decode base64 if needed
                    import base64
                    audio_data_bytes = base64.b64decode(audio_data)
                    logger.info("Speech synthesis successful via MCP-TTS")
                elif audio_url:
                    return TTSResponse(audio_url=audio_url)
        except Exception as e:
            mcp_error = str(e)
            logger.warning(f"MCP-TTS failed: {mcp_error}")
        
        # Configure fallback order
        prefer_gtts = getattr(settings, "tts_prefer_gtts", True)
        eleven_error = None
        gtts_error = None

        def try_gtts():
            nonlocal audio_data_bytes, gtts_error
            if audio_data_bytes:
                return
            try:
                audio_data_bytes = synthesize_with_gtts(request.text)
                logger.info("Speech synthesis successful via gTTS fallback")
            except Exception as exc:
                gtts_error = str(exc)
                logger.warning("gTTS fallback failed: %s", exc)

        def try_eleven_labs():
            nonlocal audio_data_bytes, eleven_error
            if audio_data_bytes:
                return
            if not getattr(settings, "enable_eleven_labs", False):
                eleven_error = "Eleven Labs disabled"
                return
            if not settings.eleven_labs_api_key:
                eleven_error = "ELEVEN_LABS_API_KEY not configured"
                return
            if "manus-mcp-cli not found" in str(mcp_error) or "manus-mcp-cli not found" in str(result.get("error", "")):
                logger.info("MCP not available, using Eleven Labs fallback")
            else:
                logger.info("MCP-TTS failed, trying Eleven Labs fallback")
            try:
                voice_id = request.voice_id or settings.eleven_labs_voice_id
                audio_data_bytes = synthesize_with_elevenlabs(request.text, voice_id)
                logger.info("Speech synthesis successful via Eleven Labs fallback")
            except Exception as exc:
                eleven_error = str(exc)
                logger.warning("Eleven Labs fallback failed: %s", exc)

        if prefer_gtts:
            try_gtts()
            try_eleven_labs()
        else:
            try_eleven_labs()
            try_gtts()

        if not audio_data_bytes:
            if getattr(settings, "enable_eleven_labs", False) and settings.eleven_labs_api_key:
                eleven_status = eleven_error or "N/A"
            else:
                eleven_status = eleven_error or "Not attempted"
            gtts_status = gtts_error or "N/A"
            raise HTTPException(
                500,
                "Speech synthesis failed. "
                f"MCP error: {mcp_error or result.get('error') or 'N/A'}. "
                f"Eleven Labs error: {eleven_status}. "
                f"gTTS error: {gtts_status}. "
                "Note: configure MCP or ensure outbound network access for gTTS."
            )

        # Convert bytes to base64 for response
        import base64
        audio_data_base64 = base64.b64encode(audio_data_bytes).decode('utf-8')
        return TTSResponse(audio_data=audio_data_base64)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("TTS synthesis error")
        raise HTTPException(500, f"Speech synthesis error: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with LLM and tool calling.
    Includes smart API key detection and management.
    
    Args:
        request: Chat request with message and optional conversation history
    
    Returns:
        LLM response with optional tool usage info
    """
    try:
        # Check if user wants to switch LLM provider
        provider_intent = api_key_manager.detect_provider_intent(request.message)
        if provider_intent:
            success, message = api_key_manager.update_provider(provider_intent)
            if success:
                return ChatResponse(
                    text=f"✅ {message}",
                    conversation_id=request.conversation_id,
                    tools_used=[]
                )
            return ChatResponse(
                text=f"❌ {message}",
                conversation_id=request.conversation_id,
                tools_used=[]
            )

        # Check if user wants to set an API key
        key_intent = api_key_manager.detect_key_intent(request.message)
        
        if key_intent:
            # User wants to set an API key
            service = key_intent['service']
            key = key_intent['key']
            
            success, message = api_key_manager.update_env_key(service, key)
            
            if success:
                return ChatResponse(
                    text=f"✅ {message}\n\nI've updated your {service} API key. "
                         f"Please restart the backend server (stop with CTRL+C and run 'python -m app.main' again) "
                         f"for the changes to take effect.",
                    conversation_id=request.conversation_id,
                    tools_used=[]
                )
            else:
                return ChatResponse(
                    text=f"❌ {message}\n\nPlease check the key format and try again. "
                         f"Example: 'Set my OpenAI key to sk-proj-...'",
                    conversation_id=request.conversation_id,
                    tools_used=[]
                )
        
        # Check API key status if user asks
        if any(word in request.message.lower() for word in ['api key', 'key status', 'configured keys', 'what keys']):
            status = api_key_manager.get_key_status()
            configured = [k for k, v in status.items() if v]
            missing = [k for k, v in status.items() if not v]
            
            status_text = "**API Key Status:**\n\n"
            if configured:
                status_text += f"✅ Configured: {', '.join(configured)}\n"
            if missing:
                status_text += f"❌ Missing: {', '.join(missing)}\n"
            status_text += f"\nCurrent LLM provider: **{status.get('provider', 'openai')}**\n"
            status_text += "\nTo set a key, say: 'Set my OpenAI key to sk-proj-...'."
            status_text += "\nTo switch providers, say: 'Use Anthropic provider'."
            
            return ChatResponse(
                text=status_text,
                conversation_id=request.conversation_id,
                tools_used=[]
            )
        
        # Get conversation history (or empty)
        history = request.history or []
        
        # Process with LLM and tools
        result = llm_service.process_with_tools(
            user_message=request.message,
            conversation_history=history,
            tools=TOOLS_SCHEMA,
            tool_executor=tool_executor
        )
        
        return ChatResponse(
            text=result["text"],
            conversation_id=request.conversation_id,
            tools_used=result.get("tools_used", []),
            products=result.get("products"),
            tool_outputs=result.get("tool_outputs")
        )
        
    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(500, f"Chat error: {str(e)}")


@app.get("/api/products/search")
async def search_products_endpoint(
    query: str,
    max_price: float = None,
    category: str = None
):
    """
    Direct product search endpoint (for testing/debugging).
    
    Args:
        query: Search query
        max_price: Optional max price
        category: Optional category
    
    Returns:
        List of matching products
    """
    try:
        products = search_products(query, max_price, category)
        return {
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        logger.exception("Product search error")
        raise HTTPException(500, f"Product search error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )

