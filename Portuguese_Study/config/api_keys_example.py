"""
Example API Key Configuration

This file shows how to configure your API keys for the Portuguese Study TTS System.
Copy this file to api_keys.py and add your actual API keys.

IMPORTANT: Never commit api_keys.py to version control!
"""

from config.api_key_config import set_api_key

# Example: Set your API keys directly
# Uncomment and replace with your actual API keys

# set_api_key('openai', 'sk-proj-your-openai-api-key-here')
# set_api_key('gemini', 'AIzaSy-your-gemini-api-key-here')

# Alternative: You can also set environment variables instead:
# export OPENAI_API_KEY="sk-proj-your-openai-api-key-here"
# export GEMINI_API_KEY="AIzaSy-your-gemini-api-key-here"

print("API key configuration example loaded.")
print("To configure your API keys:")
print("1. Copy this file to 'api_keys.py'")
print("2. Uncomment and add your actual API keys")
print("3. Or set environment variables OPENAI_API_KEY and GEMINI_API_KEY")
