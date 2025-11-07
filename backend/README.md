# tubbyAI Backend API

FastAPI backend for the tubbyAI AI assistant with voice, chat, and e-commerce capabilities.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key for LLM
- `MCP_STT_SERVICE` - MCP service name for STT (default: `mcp-stt`)
- `MCP_TTS_SERVICE` - MCP service name for TTS (default: `mcp-tts`)
- `MCP_RAG_SERVICE` - MCP service name for RAG (default: `mcp-rag`)

### 3. Run Server

```bash
python -m app.main
# Or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will run at `http://localhost:8000`

### 4. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Chat (requires OPENAI_API_KEY)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find me a smart speaker under $100"}'
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/stt/transcribe` - Speech-to-text (audio file upload)
- `POST /api/tts/synthesize` - Text-to-speech
- `POST /api/chat` - Chat with LLM and tools
- `GET /api/products/search` - Direct product search

### Product Catalog Integration

- Product data is sourced from an S3-hosted unified master list (`PRODUCT_CATALOG_URL`)
- Media paths are normalized using `PRODUCT_MEDIA_BASE_URL`, so relative `product_media/...` entries resolve to publicly accessible URLs
- Update these environment variables before deploying to Lambda if you host the catalog elsewhere

## Architecture

- **FastAPI** - Web framework
- **MCP (Model Context Protocol)** - External service integration
- **OpenAI** - LLM provider
- **Function Calling** - Tool execution for e-commerce and research

## Development

### Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── config.py         # Configuration
│   ├── mcp/
│   │   └── client.py     # MCP client helper
│   ├── services/
│   │   ├── llm.py        # LLM service
│   │   └── tool_executor.py  # Tool execution
│   ├── tools/
│   │   ├── product_search.py  # Product search tool
│   │   ├── grokipedia.py     # Grokipedia RAG tool
│   │   └── schemas.py        # Tool schemas
│   └── models/
│       ├── request.py     # Request models
│       └── response.py    # Response models
├── requirements.txt
├── .env.example
└── README.md
```

### Adding New Tools

1. Create tool function in `app/tools/`
2. Add tool schema to `app/tools/schemas.py`
3. Register tool in `app/main.py`:
   ```python
   tool_executor.register_tool("tool_name", tool_function)
   ```

## Notes

- MCP services must be configured and accessible via `manus-mcp-cli`
- Product catalog is cached for 5 minutes
- Chat maintains conversation history (currently in-memory, can be extended to database)

