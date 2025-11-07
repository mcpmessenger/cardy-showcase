"""Grokipedia RAG tool for research queries."""
import logging
from typing import Dict, Any

from app.mcp.client import execute_mcp_command
from app.config import settings

logger = logging.getLogger(__name__)


def grokipedia_search(query: str) -> Dict[str, Any]:
    """
    Search Grokipedia for research information.
    
    Args:
        query: Research topic or question
    
    Returns:
        Search results with content and citations
    """
    logger.info(f"Searching Grokipedia for: {query}")
    
    # Call MCP-RAG service
    result = execute_mcp_command(
        service=settings.mcp_rag_service,
        action="search",
        query=query
    )
    
    if "error" in result:
        error_msg = result["error"]
        logger.warning(f"Grokipedia search error: {error_msg}")
        
        # If MCP not available, return helpful message
        if "manus-mcp-cli not found" in error_msg:
            return {
                "error": "MCP-RAG service not available",
                "content": (
                    f"I couldn't access the research database right now. "
                    f"However, I can still help answer your question about '{query}' "
                    f"based on my training data. Would you like me to do that?"
                ),
                "sources": [],
                "note": "MCP-RAG service requires manus-mcp-cli to be installed"
            }
        
        return {
            "error": error_msg,
            "content": "Sorry, I couldn't access Grokipedia at this time. Please try again later.",
            "sources": []
        }
    
    # Extract content and format for LLM
    content = result.get("content", result.get("text", ""))
    sources = result.get("sources", result.get("citations", []))
    
    return {
        "content": content,
        "sources": sources if isinstance(sources, list) else [],
        "query": query
    }

