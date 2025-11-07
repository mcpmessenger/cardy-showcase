"""Tool executor for LLM function calling."""
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools called by LLM."""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, func: Callable):
        """Register a tool function."""
        self.tools[name] = func
        logger.info(f"Registered tool: {name}")
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool
        
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            error_msg = f"Tool '{tool_name}' not found. Available: {list(self.tools.keys())}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**args)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            error_msg = f"Tool {tool_name} execution failed: {str(e)}"
            logger.exception(error_msg)
            return {"error": error_msg}


# Singleton instance
tool_executor = ToolExecutor()

