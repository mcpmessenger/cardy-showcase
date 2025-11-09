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
        self.system_prompt = (
            "You are tubbyAI, a voice assistant for a smart store with access to helper tools. "
            "Use the available functions whenever they help: search the product catalog for retail questions, "
            "query Alpha Vantage for up-to-date stock quotes or intraday data when a user asks about tickers, "
            "consult Polymarket data for prediction market odds, and call Grokipedia for general knowledge "
            "research. Keep responses brief and natural for spoken conversation. Mention sources when possible "
            "and include product images when showing shopping results."
        )
        # Conversation management
        # GPT-4 has 8192 token limit. Reserve ~2500 for system prompt + tools, leaving ~5500 for messages
        # Be conservative to account for token estimation inaccuracy
        self.max_history_messages = 6  # keep last N messages (including tool messages)
        self.max_message_tokens = 5000  # target max tokens for all messages (excluding system + tools) - conservative
        self.max_tool_response_chars = 1500  # truncate tool responses more aggressively

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
                "You are tubbyAI, a voice assistant for a smart store with access to helper tools. "
                "Use the available functions whenever they help: product search for retail queries, "
                "Alpha Vantage for stock data, Polymarket for prediction odds, and Grokipedia for general knowledge. "
                "If you cannot perform an action, apologize briefly and offer alternative help. "
                "Keep responses concise and natural for spoken conversation."
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
            error_str = str(e)
            # Check if it's a context length error
            if "context_length" in error_str.lower() or "maximum context length" in error_str.lower():
                logger.warning(f"Context length exceeded. Attempting to trim messages more aggressively.")
                # Try with just the last few messages
                if len(payload["messages"]) > 3:  # system + at least 2 user/assistant messages
                    # Keep system prompt and last 2-3 messages only
                    trimmed_payload = payload.copy()
                    trimmed_payload["messages"] = [
                        payload["messages"][0],  # system prompt
                        *payload["messages"][-3:]  # last 3 messages
                    ]
                    try:
                        response = self.client.chat.completions.create(**trimmed_payload)
                        logger.info("Successfully retried with aggressively trimmed context")
                        return {
                            "message": response.choices[0].message,
                            "usage": response.usage,
                        }
                    except Exception as retry_e:
                        logger.error(f"Retry with trimmed context also failed: {retry_e}")
                        raise
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

        history = self._prepare_history(conversation_history)
        messages = [
            *history,
            {"role": "user", "content": user_message}
        ]
        # Apply context limits before first call (tools present, so reserve space)
        messages = self._enforce_context_limits(messages, tools_present=bool(tools))
        
        tool_outputs: Dict[str, Any] = {}

        # First LLM call (with tools)
        # Note: tools schema adds significant tokens, so be extra conservative
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
                tool_outputs[function_name] = tool_result
                
                # Capture product search results
                if function_name == "search_products" and isinstance(tool_result, list):
                    products_found = tool_result
                
                # Add tool result to messages (truncate if too large)
                tool_content = json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result
                original_length = len(tool_content)
                if original_length > self.max_tool_response_chars:
                    tool_content = tool_content[:self.max_tool_response_chars] + f"\n... (truncated, original length: {original_length} chars)"
                    logger.debug(f"Truncated tool response for {function_name} from {original_length} to {self.max_tool_response_chars} chars")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": tool_content
                })
            
            # Second LLM call (with tool results)
            # No tools in second call (just messages), but tool responses are large
            constrained_messages = self._enforce_context_limits(messages, tools_present=False)
            final_response = self.chat_completion(constrained_messages)
            return {
                "text": final_response["message"].content,
                "tools_used": tools_used,
                "products": products_found if products_found else None,
                "tool_outputs": tool_outputs or None,
            }
        
        # No tools called, return direct response
        # No need to constrain again since we already did before the first call
        return {
            "text": response_message.content,
            "tools_used": [],
            "products": None,
            "tool_outputs": None,
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

    # ------------------------------------------------------------------ helpers
    def _prepare_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Trim conversation history to stay within configured limits.

        Args:
            history: Original conversation history (list of message dicts).

        Returns:
            Trimmed copy of the history.
        """
        if not history:
            return []

        # Keep only the most recent messages
        trimmed = history[-self.max_history_messages :]
        
        # Estimate tokens and trim if needed
        trimmed = self._trim_to_token_limit(trimmed, self.max_message_tokens)
        
        if len(trimmed) < len(history):
            logger.info(
                "Trimmed conversation history from %s to %s messages to stay within context window.",
                len(history),
                len(trimmed),
            )

        return trimmed

    def _enforce_context_limits(self, messages: List[Dict[str, Any]], tools_present: bool = False) -> List[Dict[str, Any]]:
        """
        Apply context limits to the message list before an LLM call.
        Truncates tool responses and keeps only recent messages.
        
        Args:
            messages: List of messages to trim
            tools_present: If True, reserve more space for tools schema (which can be 1000-2000 tokens)
        """
        if not messages:
            return messages

        # Truncate large tool responses first
        messages = self._truncate_tool_responses(messages)
        
        # Keep only recent messages
        trimmed = messages[-self.max_history_messages :]
        
        # Adjust token limit based on whether tools are present
        # Tools schema can be 1000-2000 tokens, so be more conservative
        effective_limit = self.max_message_tokens - (1500 if tools_present else 0)
        effective_limit = max(effective_limit, 2000)  # Never go below 2000 tokens
        
        # Trim to token limit (more aggressive)
        trimmed = self._trim_to_token_limit(trimmed, effective_limit)

        if not trimmed:
            # Fallback: keep the most recent message to avoid empty payload
            return messages[-1:] if messages else []

        if len(trimmed) < len(messages):
            logger.info(
                "Trimmed messages from %s to %s to stay within token limit (limit: %s tokens, tools: %s).",
                len(messages),
                len(trimmed),
                effective_limit,
                tools_present,
            )

        return trimmed

    def _truncate_tool_responses(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Truncate tool response content to avoid bloating context."""
        result = []
        for msg in messages:
            if msg.get("role") == "tool" and msg.get("content"):
                content = msg["content"]
                if isinstance(content, str) and len(content) > self.max_tool_response_chars:
                    # Truncate and add indicator
                    truncated = content[:self.max_tool_response_chars]
                    msg = msg.copy()
                    msg["content"] = truncated + f"\n... (truncated, original length: {len(content)} chars)"
                    logger.debug(f"Truncated tool response from {len(content)} to {self.max_tool_response_chars} chars")
            result.append(msg)
        return result

    def _trim_to_token_limit(self, messages: List[Dict[str, Any]], max_tokens: int) -> List[Dict[str, Any]]:
        """Trim messages to stay within token limit, keeping the most recent."""
        if not messages:
            return messages
        
        # Estimate tokens for each message (rough: 1 token ≈ 4 chars for English, but JSON is more)
        total_tokens = 0
        trimmed = []
        
        # Work backwards from the end to keep most recent messages
        for msg in reversed(messages):
            msg_tokens = self._estimate_tokens(msg)
            if total_tokens + msg_tokens > max_tokens:
                break
            trimmed.insert(0, msg)
            total_tokens += msg_tokens
        
        return trimmed

    @staticmethod
    def _estimate_tokens(message: Dict[str, Any]) -> int:
        """
        Estimate token count for a message.
        Conservative approximation: 1 token ≈ 3 chars for safety (accounts for JSON/structured data).
        """
        if not message:
            return 0
        
        # Get content
        content = message.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        elif not isinstance(content, str):
            content = str(content)
        
        if not content:
            # Tool calls without content still have overhead
            if message.get("tool_calls"):
                return 50  # Estimate for tool call structure
            return 5  # Minimal overhead
        
        # Conservative token estimate: ~3 chars per token (accounts for JSON being more token-dense)
        base_tokens = len(content) // 3
        
        # Adjust for JSON/structure (tool responses, function calls)
        if message.get("role") == "tool":
            # Tool responses (JSON) are very token-heavy
            base_tokens = int(base_tokens * 1.5)
        elif message.get("tool_calls"):
            # Tool call definitions
            base_tokens = int(base_tokens * 1.2)
        
        # Add overhead for message structure (role, name, tool_call_id, etc.)
        overhead = 15 if message.get("tool_calls") or message.get("role") == "tool" else 10
        
        return base_tokens + overhead


# Singleton instance - lazy initialization
llm_service = LLMService()

