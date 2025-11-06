"""LLM service for chat and function calling."""
import json
import logging
from typing import List, Dict, Any, Optional

from openai import OpenAI

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLM APIs."""
    
    def __init__(self):
        self.provider = (settings.llm_provider or "openai").lower()
        self._client: Optional[OpenAI] = None
        self._gemini_model = None
        self.model = settings.llm_model
        self.system_prompt = """You are tubbyAI, a voice assistant for a smart store. 
Search products, add to cart, answer questions. Keep responses brief and natural for spoken conversation. 
Include product images when showing results."""

        if self.provider == "gemini":
            if genai is None:
                raise ValueError(
                    "google-generativeai package is required for Gemini provider. "
                    "Run 'pip install google-generativeai'."
                )
            if not settings.google_api_key:
                raise ValueError(
                    "GOOGLE_API_KEY not configured. Please set it in environment variable."
                )

            api_key = settings.google_api_key.strip()
            if not api_key:
                raise ValueError("Invalid GOOGLE_API_KEY provided.")

            genai.configure(api_key=api_key)
            model_name = settings.gemini_model or "gemini-1.5-flash"
            self.gemini_model_name = model_name
            self._gemini_model = genai.GenerativeModel(model_name=model_name)

            # Ensure system prompt is applied via instructions
            self.system_prompt = (
                "You are tubbyAI, a voice assistant for a smart store. "
                "You can chat about products and general topics. If you cannot perform "
                "an action (like searching inventory), apologize briefly and offer to provide "
                "helpful information instead. Keep responses concise and natural for spoken conversation."
            )
        else:
            self.provider = "openai"
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self.provider != "openai":
            raise RuntimeError("OpenAI client requested while provider is not set to OpenAI.")

        if self._client is None:
            if not settings.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY not configured. Please set it in .env file or environment variable."
                )
            # Clean API key (remove whitespace)
            api_key = settings.openai_api_key.strip()
            if not api_key or len(api_key) < 20:
                raise ValueError("Invalid API key format. Key appears to be empty or too short.")

            client_kwargs = {"api_key": api_key}
            if settings.openai_project_id:
                client_kwargs["default_headers"] = {
                    "OpenAI-Project": settings.openai_project_id
                }

            self._client = OpenAI(**client_kwargs)
        return self._client
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """Send chat completion request with optional tools."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                *messages
            ],
            "temperature": 0.7,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
        
        try:
            response = self.client.chat.completions.create(**payload)
            return {
                "message": response.choices[0].message,
                "usage": response.usage,
            }
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise
    
    def process_with_tools(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        tools: List[Dict],
        tool_executor
    ) -> str:
        """
        Process chat request with tool calling support.
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation messages
            tools: List of tool definitions for LLM
            tool_executor: Tool executor instance
        
        Returns:
            Final response text
        """
        if self.provider == "gemini":
            return self._process_with_tools_gemini(user_message, conversation_history)

        messages = [
            *conversation_history,
            {"role": "user", "content": user_message}
        ]
        
        # First LLM call (with tools)
        response = self.chat_completion(messages, tools=tools)
        response_message = response["message"]
        
        # Convert message to dict format
        message_dict = {
            "role": response_message.role,
            "content": response_message.content
        }
        
        # Add tool calls if present
        if response_message.tool_calls:
            message_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in response_message.tool_calls
            ]
        
        messages.append(message_dict)
        
        # Check for tool calls
        if response_message.tool_calls:
            tools_used = []
            products_found = []
            
            # Execute tools
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"Executing tool: {function_name} with args: {function_args}")
                
                # Execute tool
                tool_result = tool_executor.execute(function_name, function_args)
                tools_used.append(function_name)
                
                # Capture product search results
                if function_name == "search_products" and isinstance(tool_result, list):
                    products_found = tool_result
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result
                })
            
            # Second LLM call (with tool results)
            final_response = self.chat_completion(messages)
            return {
                "text": final_response["message"].content,
                "tools_used": tools_used,
                "products": products_found if products_found else None
            }
        
        # No tools called, return direct response
        return {
            "text": response_message.content,
            "tools_used": [],
            "products": None
        }

    # Gemini -----------------------------------------------------------------
    def _process_with_tools_gemini(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        if not self._gemini_model:
            raise RuntimeError("Gemini model is not initialized.")

        prompt_parts = [self.system_prompt.strip()]
        for message in conversation_history:
            role = message.get("role", "user")
            content = message.get("content", "")
            if not content:
                continue
            if role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            elif role == "tool":
                prompt_parts.append(f"Tool output: {content}")
            else:
                prompt_parts.append(f"User: {content}")

        prompt_parts.append(f"User: {user_message}")
        prompt_parts.append("Assistant:")
        prompt = "\n".join(prompt_parts)

        try:
            response = self._gemini_model.generate_content(prompt)
            text = self._extract_gemini_text(response)
            return {
                "text": text,
                "tools_used": [],
                "products": None,
            }
        except Exception as exc:  # pragma: no cover - network call
            logger.error(f"Gemini API error: {exc}")
            raise

    @staticmethod
    def _extract_gemini_text(response) -> str:
        if not response:
            return "I'm sorry, but I couldn't generate a response right now."

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        texts: List[str] = []
        candidates = getattr(response, "candidates", []) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            parts = getattr(content, "parts", []) or []
            for part in parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    texts.append(part_text)

        if texts:
            return "\n".join(text.strip() for text in texts if text.strip())

        return "I'm sorry, but I couldn't generate a response right now."


# Singleton instance - lazy initialization
llm_service = LLMService()

