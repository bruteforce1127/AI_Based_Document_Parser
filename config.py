"""
Configuration settings for ClarityVault
"""
import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf'}

# Groq AI settings
# API keys are loaded from environment variable (comma-separated for multiple keys)
# Example: GROQ_API_KEYS=key1,key2,key3
_groq_keys_str = os.environ.get('GROQ_API_KEYS', '')
GROQ_API_KEYS = [k.strip() for k in _groq_keys_str.split(',') if k.strip()] if _groq_keys_str else ['placeholder-add-keys-in-render']
GROQ_MODEL = 'llama-3.3-70b-versatile'

# YouTube API settings
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')

# Supabase settings
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

# JWT settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'change-this-secret-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_DAYS = 90
