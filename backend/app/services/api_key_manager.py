"""API Key Manager - Secure API key configuration via chat."""
import logging
import os
import re
from typing import Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages API keys securely."""
    
    def __init__(self, env_file_path: str = None):
        # Use backend/.env by default
        if env_file_path is None:
            # Get the backend directory
            backend_dir = Path(__file__).parent.parent.parent
            self.env_file_path = backend_dir / ".env"
        else:
            self.env_file_path = Path(env_file_path)
        self.env_backup_path = self.env_file_path.parent / f"{self.env_file_path.name}.backup"
    
    def detect_key_intent(self, message: str) -> Optional[Dict[str, str]]:
        """
        Detect if user wants to set an API key from chat message.
        
        Returns:
            Dict with 'service' and 'key' if detected, None otherwise
        """
        message_lower = message.lower().strip()
        
        # Patterns to detect API key setting
        patterns = [
            # "set openai key to sk-..."
            r"(?:set|update|configure|add)\s+(?:my\s+)?(openai|eleven.?labs|anthropic|google|grokipedia|alpha\s+vantage|polymarket)\s+(?:api\s+)?key\s+(?:to|as|is)?\s+(sk-[\w\-]+|[\w\-]{4,})",
            # "my openai key is sk-..."
            r"(?:my\s+)?(openai|eleven.?labs|anthropic|google|grokipedia|alpha\s+vantage|polymarket)\s+(?:api\s+)?key\s+(?:is|:)\s+(sk-[\w\-]+|[\w\-]{4,})",
            # "openai key: sk-..."
            r"(openai|eleven.?labs|anthropic|google|grokipedia|alpha\s+vantage|polymarket)\s+(?:api\s+)?key\s*[:=]\s*(sk-[\w\-]+|[\w\-]{4,})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                service = match.group(1).lower()
                # Normalize service names
                service_map = {
                    'openai': 'openai',
                    'elevenlabs': 'eleven_labs',
                    'eleven labs': 'eleven_labs',
                    'anthropic': 'anthropic',
                    'google': 'google',
                    'grokipedia': 'grokipedia',
                    'alpha vantage': 'alpha_vantage',
                    'polymarket': 'polymarket'
                }
                service = service_map.get(service, service)
                
                # Extract the key (might be in different groups)
                key = None
                for group in match.groups():
                    if group and (group.startswith('sk-') or len(group) > 20):
                        key = group
                        break
                
                # Also try to find key in original message (case-sensitive for actual keys)
                if not key:
                    # Look for keys that start with sk- or are long alphanumeric strings
                    key_match = re.search(r'(sk-[\w\-]+|[\w\-]{30,})', message)
                    if key_match:
                        potential_key = key_match.group(1)
                        # Make sure it's not part of a URL or other text
                        if len(potential_key) >= 20 and not potential_key.endswith('.com'):
                            key = potential_key
                
                if key and service:
                    return {
                        'service': service,
                        'key': key.strip()
                    }
        
        return None
    
    def detect_provider_intent(self, message: str) -> Optional[str]:
        """Detect if user wants to change the active LLM provider."""
        message_lower = message.lower().strip()

        patterns = [
            r"(?:set|switch|change|use|select)\s+(?:the\s+)?(?:llm\s+)?provider\s+(?:to|as)?\s+(openai|anthropic|gemini)",
            r"(?:use|switch to|activate)\s+(openai|anthropic|gemini)\s+(?:llm|model|provider)"
        ]

        for pattern in patterns:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                provider = match.group(1).lower()
                return provider

        return None

    def _write_env_value(self, env_var: str, value: str) -> Tuple[bool, str]:
        """Helper to upsert an environment variable in the .env file."""
        try:
            env_file = self.env_file_path
            if not env_file.is_absolute():
                backend_dir = Path(__file__).parent.parent.parent
                env_file = backend_dir / env_file

            env_lines = []
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_lines = f.readlines()

            new_lines = []
            updated = False
            for line in env_lines:
                stripped = line.strip()
                if stripped.startswith(f"{env_var}=") or stripped.startswith(f"{env_var} ="):
                    new_lines.append(f"{env_var}={value}\n")
                    updated = True
                else:
                    new_lines.append(line)

            if not updated:
                new_lines.append(f"{env_var}={value}\n")

            if env_file.exists():
                import shutil
                if self.env_backup_path.exists():
                    self.env_backup_path.unlink()
                shutil.copy(env_file, self.env_backup_path)

            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            logger.info(f"Updated {env_var} in {env_file}")
            return True, f"Updated {env_var}."
        except Exception as exc:
            logger.error(f"Error writing env var {env_var}: {exc}")
            return False, str(exc)

    def validate_key(self, service: str, key: str) -> Tuple[bool, str]:
        """
        Validate API key format.
        
        Returns:
            (is_valid, error_message)
        """
        key = key.strip()
        
        if not key:
            return False, "API key cannot be empty"
        
        if len(key) < 20:
            return False, "API key appears too short"
        
        # Service-specific validation
        if service == 'openai':
            if not key.startswith(('sk-', 'sk-proj-')):
                return False, "OpenAI key should start with 'sk-' or 'sk-proj-'"
        
        elif service == 'eleven_labs':
            # Eleven Labs keys are typically longer alphanumeric strings
            if len(key) < 30:
                return False, "Eleven Labs key appears too short"
        
        elif service == 'anthropic':
            if not key.startswith('sk-ant-'):
                return False, "Anthropic key should start with 'sk-ant-'"

        elif service == 'alpha_vantage':
            # Alpha Vantage keys are typically 16 alphanumeric chars but allow the demo key
            if key.lower() != 'demo' and len(key) < 8:
                return False, "Alpha Vantage key appears too short"

        elif service == 'polymarket':
            # Polymarket API tokens vary; ensure reasonable length
            if len(key) < 10:
                return False, "Polymarket key appears too short"
        
        return True, ""
    
    def update_env_key(self, service: str, key: str) -> Tuple[bool, str]:
        """
        Update API key in .env file.
        
        Returns:
            (success, message)
        """
        # Validate key first
        is_valid, error_msg = self.validate_key(service, key)
        if not is_valid:
            return False, f"Invalid key format: {error_msg}"
        
        try:
            # Map service name to env var name
            env_var_map = {
                'openai': 'OPENAI_API_KEY',
                'eleven_labs': 'ELEVEN_LABS_API_KEY',
                'anthropic': 'ANTHROPIC_API_KEY',
                'google': 'GOOGLE_API_KEY',
                'grokipedia': 'GROKIPEDIA_API_KEY',
                'alpha_vantage': 'ALPHA_VANTAGE_API_KEY',
                'polymarket': 'POLYMARKET_API_KEY'
            }
            
            env_var = env_var_map.get(service)
            if not env_var:
                return False, f"Unknown service: {service}"
            
            success, write_message = self._write_env_value(env_var, key)
            if not success:
                return False, f"Error updating key: {write_message}"
            return True, f"Successfully updated {service} API key. Please restart the backend server for changes to take effect."
            
        except Exception as e:
            logger.error(f"Error updating .env file: {e}")
            return False, f"Error updating key: {str(e)}"

    def update_provider(self, provider: str) -> Tuple[bool, str]:
        provider = provider.lower().strip()
        allowed = {"openai", "anthropic", "gemini"}
        if provider not in allowed:
            return False, f"Unsupported provider '{provider}'. Choose from {', '.join(sorted(allowed))}."

        success, message = self._write_env_value("LLM_PROVIDER", provider)
        if success:
            return True, (
                f"Switched LLM provider to **{provider}**. "
                "Redeploy or restart the backend so the change takes effect."
            )
        return False, f"Error updating provider: {message}"
    
    def get_key_status(self) -> Dict[str, bool]:
        """Get status of which API keys are configured."""
        from app.config import settings
        
        return {
            'openai': bool(settings.openai_api_key),
            'eleven_labs': bool(settings.eleven_labs_api_key),
            'anthropic': bool(settings.anthropic_api_key),
            'google': bool(settings.google_api_key),
            'grokipedia': bool(settings.grokipedia_api_key),
            'alpha_vantage': bool(settings.alpha_vantage_api_key),
            'polymarket': bool(settings.polymarket_api_key),
            'provider': settings.llm_provider or 'openai'
        }


# Singleton instance
api_key_manager = APIKeyManager()

