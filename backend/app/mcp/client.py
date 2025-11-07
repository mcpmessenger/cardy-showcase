"""MCP (Model Context Protocol) client helper."""
import subprocess
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def execute_mcp_command(
    service: str, 
    action: str, 
    timeout: int = 30,
    **kwargs
) -> Dict[str, Any]:
    """
    Executes an MCP command and returns parsed JSON response.
    
    Args:
        service: MCP service name (e.g., 'mcp-stt', 'mcp-tts', 'mcp-rag')
        action: Action to perform (e.g., 'transcribe', 'synthesize', 'search')
        timeout: Command timeout in seconds
        **kwargs: Parameters for the command (converted to --key value flags)
    
    Returns:
        Parsed JSON response or error dict with 'error' key
    """
    base_command = ["manus-mcp-cli", "call", service, action]
    
    # Convert kwargs to command-line flags
    for key, value in kwargs.items():
        base_command.append(f"--{key}")
        base_command.append(str(value))
    
    try:
        logger.info(f"Executing MCP command: {service}.{action} with args: {kwargs}")
        
        result = subprocess.run(
            base_command,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        
        # Try to parse JSON response
        try:
            response = json.loads(result.stdout.strip())
            logger.debug(f"MCP {service}.{action} success")
            return response
        except json.JSONDecodeError:
            # If not JSON, return as text
            logger.warning(f"MCP {service}.{action} returned non-JSON response")
            return {"text": result.stdout.strip()}
            
    except subprocess.CalledProcessError as e:
        error_msg = f"MCP command failed: {e.stderr or e.stdout or 'Unknown error'}"
        logger.error(f"MCP {service}.{action} error: {error_msg}")
        return {"error": error_msg}
        
    except subprocess.TimeoutExpired:
        error_msg = f"MCP command timed out after {timeout}s"
        logger.error(f"MCP {service}.{action} timeout")
        return {"error": error_msg}
        
    except FileNotFoundError:
        error_msg = "manus-mcp-cli not found. Please install it first."
        logger.error(error_msg)
        return {"error": error_msg}
        
    except Exception as e:
        error_msg = f"Execution error: {str(e)}"
        logger.exception(f"MCP {service}.{action} exception")
        return {"error": error_msg}


def safe_mcp_call(
    service: str, 
    action: str, 
    default_return: Any = None,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Safely call MCP with error handling, returns None on error.
    
    Args:
        service: MCP service name
        action: Action to perform
        default_return: Value to return on error (default: None)
        **kwargs: Parameters for the command
    
    Returns:
        Response dict or None on error
    """
    result = execute_mcp_command(service, action, **kwargs)
    if "error" in result:
        logger.error(f"MCP {service}.{action} failed: {result['error']}")
        return default_return
    return result

