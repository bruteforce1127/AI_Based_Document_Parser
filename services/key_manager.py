"""
Key Manager Service - Handles API key rotation to avoid rate limits
"""
import itertools
from groq import Groq
import config

# Create a cycle iterator for round-robin rotation
_key_cycle = itertools.cycle(config.GROQ_API_KEYS)

def get_current_key():
    """Get the next API key in the rotation"""
    return next(_key_cycle)

def get_groq_client():
    """Get a Groq client initialized with the next API key"""
    # Simply rotating for every new client request is a simple way 
    # to distribute load roughly evenly.
    api_key = get_current_key()
    # print(f"Using API Key ending in: ...{api_key[-4:]}") # Debug log
    return Groq(api_key=api_key)
