"""Configuration and environment variables."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    openai_api_key: str = ""
    openai_project_id: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-haiku-20240307"
    google_api_key: str = ""
    llm_model: str = "gpt-4"
    llm_provider: str = "openai"
    gemini_model: str = "gemini-pro"
    
    # Eleven Labs
    eleven_labs_api_key: str = ""
    eleven_labs_voice_id: str = ""
    
    # Grokipedia
    grokipedia_api_key: str = ""
    
    # MCP Configuration
    mcp_stt_service: str = "mcp-stt"
    mcp_tts_service: str = "mcp-tts"
    mcp_rag_service: str = "mcp-rag"
    
    # Product Catalog
    product_catalog_url: str = "https://tubbyai-products-catalog.s3.amazonaws.com/unified-products-master.json"
    product_media_base_url: str = "https://tubbyai-products-catalog.s3.amazonaws.com/"
    
    # Server Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = 'utf-8'
        
    def model_post_init(self, __context):
        """Clean up API keys - remove whitespace."""
        if self.openai_api_key:
            self.openai_api_key = self.openai_api_key.strip()
        if self.openai_project_id:
            self.openai_project_id = self.openai_project_id.strip()
        if self.anthropic_api_key:
            self.anthropic_api_key = self.anthropic_api_key.strip()
        if self.anthropic_model:
            self.anthropic_model = self.anthropic_model.strip()
        if self.google_api_key:
            self.google_api_key = self.google_api_key.strip()
        if self.eleven_labs_api_key:
            self.eleven_labs_api_key = self.eleven_labs_api_key.strip()
        if self.llm_provider:
            self.llm_provider = self.llm_provider.strip()
        if self.gemini_model:
            self.gemini_model = self.gemini_model.strip()
        if self.product_catalog_url:
            self.product_catalog_url = self.product_catalog_url.strip()
        if self.product_media_base_url:
            self.product_media_base_url = self.product_media_base_url.strip()


settings = Settings()

# Validate critical settings at startup
if not settings.openai_api_key:
    import warnings
    warnings.warn(
        "OPENAI_API_KEY not set. Chat functionality will not work. "
        "Set it in .env file or environment variable.",
        UserWarning
    )

