"""
Key Manager Service - Handles API key rotation to avoid rate limits
"""
import itertools
import importlib
import config

# Dynamically load the AI inference SDK
_sdk = importlib.import_module(config.AI_SDK_MODULE)
_ClientClass = getattr(_sdk, config.AI_SDK_CLIENT)

# Create a cycle iterator for round-robin rotation
_key_cycle = itertools.cycle(config.OPENAI_API_KEYS)

def get_current_key():
    """Get the next API key in the rotation"""
    return next(_key_cycle)

def get_openai_client():
    """Get an OpenAI client initialized with the next API key"""
    api_key = get_current_key()
    return _ClientClass(api_key=api_key)
