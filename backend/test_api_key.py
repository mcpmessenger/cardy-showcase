"""Test OpenAI API key validity."""
import sys
from app.config import settings
from openai import OpenAI

def test_api_key():
    """Test if the OpenAI API key is valid."""
    api_key = settings.openai_api_key.strip()
    
    print(f"API Key Info:")
    print(f"  Length: {len(api_key)}")
    print(f"  Starts with: {api_key[:10]}...")
    print(f"  Ends with: ...{api_key[-10:]}")
    print(f"  Has whitespace: {api_key != api_key.strip()}")
    print()
    
    if not api_key:
        print("ERROR: API key is empty!")
        return False
    
    if len(api_key) < 20:
        print("ERROR: API key is too short!")
        return False
    
    if not api_key.startswith(('sk-', 'sk-proj-')):
        print("WARNING: API key doesn't start with 'sk-' or 'sk-proj-'")
        print("   This might still be valid, but unusual.")
    
    print("Testing API key with OpenAI...")
    try:
        client = OpenAI(api_key=api_key)
        # Try a simple API call
        models = client.models.list()
        print("SUCCESS: API key is valid!")
        print(f"   Found {len(list(models))} models available")
        return True
    except Exception as e:
        error_str = str(e)
        print("ERROR: API key is invalid or rejected")
        print(f"   Error: {error_str}")
        
        if "401" in error_str or "invalid_api_key" in error_str:
            print()
            print("FIX:")
            print("1. Go to: https://platform.openai.com/account/api-keys")
            print("2. Verify your key is active")
            print("3. Create a new key if needed")
            print("4. Update backend/.env with the new key")
            print("5. Make sure key has no spaces or quotes")
        
        return False

if __name__ == "__main__":
    success = test_api_key()
    sys.exit(0 if success else 1)

