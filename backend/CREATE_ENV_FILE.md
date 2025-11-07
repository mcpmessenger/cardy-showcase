# Create .env File - Quick Setup

## ⚠️ IMPORTANT: This file contains API keys and will NOT be committed to git

## Steps:

### 1. Navigate to backend folder
```powershell
cd backend
```

### 2. Create .env file (copy the entire block below)

**PowerShell:**
```powershell
@"
# LLM Configuration
OPENAI_API_KEY=sk-REPLACE_ME
ANTHROPIC_API_KEY=sk-ant-REPLACE_ME
GOOGLE_API_KEY=AIzaREPLACE_ME
LLM_MODEL=gpt-4

# Eleven Labs (if direct API access needed)
ELEVEN_LABS_API_KEY=
ELEVEN_LABS_VOICE_ID=

# Grokipedia (if direct API access needed)
GROKIPEDIA_API_KEY=

# MCP Configuration
MCP_STT_SERVICE=mcp-stt
MCP_TTS_SERVICE=mcp-tts
MCP_RAG_SERVICE=mcp-rag

# Product Catalog
PRODUCT_CATALOG_URL=https://tubbyai-products-catalog.s3.amazonaws.com/unified-products-master.json
PRODUCT_MEDIA_BASE_URL=https://tubbyai-products-catalog.s3.amazonaws.com/

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
"@ | Out-File -FilePath .env -Encoding utf8
```

**Or manually create .env file:**
1. Create a new file named `.env` in the `backend` folder
2. Copy and paste the content above (without the PowerShell command wrapper)
3. Save the file

### 3. Verify .env file exists
```powershell
Test-Path .env
# Should return: True
```

### 4. Test the server
```powershell
.\venv\Scripts\Activate.ps1
python -m app.main
```

## ✅ Security Notes

- ✅ `.env` is already in `.gitignore` - it will NOT be committed
- ✅ Never share API keys publicly
- ✅ If you commit by accident, rotate your keys immediately

