"""
Database Service - Supabase integration for users and documents
"""
from supabase import create_client
import config
from datetime import datetime

# Initialize Supabase client
supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

import time
from functools import wraps

def retry_db_op(max_retries=3, delay=1):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    print(f"Database operation failed (Attempt {retries+1}/{max_retries}): {e}")
                    if "getaddrinfo failed" in str(e) or "create_connection" in str(e):
                         # Network error, wait and retry
                         time.sleep(delay * (2 ** retries))
                         retries += 1
                    else:
                        # Other error (e.g. logic), raise immediately or return None depending on pattern
                        # For now, we'll retry all exceptions to be safe, but log them
                        time.sleep(delay)
                        retries += 1
            return None # Failed after all retries
        return wrapper
    return decorator


# ==================== USER OPERATIONS ====================

@retry_db_op()
def create_user(name, email, password_hash):
    """Create a new user in the database"""
    try:
        result = supabase.table('users').insert({
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return None


@retry_db_op()
def get_user_by_email(email):
    """Get user by email"""
    try:
        result = supabase.table('users').select('*').eq('email', email).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        import traceback
        traceback.print_exc()
        return None


@retry_db_op()
def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        result = supabase.table('users').select('*').eq('id', user_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


# ==================== DOCUMENT OPERATIONS ====================

@retry_db_op()
def save_document(user_id, filename, document_type, content, pages_count):
    """Save a document to the database"""
    try:
        result = supabase.table('documents').insert({
            'user_id': user_id,
            'filename': filename,
            'document_type': document_type,
            'content': content[:50000],  # Limit content size
            'pages_count': pages_count,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error saving document: {e}")
        return None


@retry_db_op()
def get_user_documents(user_id):
    """Get all documents for a user"""
    try:
        result = supabase.table('documents').select('id, filename, document_type, pages_count, created_at').eq('user_id', user_id).order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting documents: {e}")
        return []


@retry_db_op()
def get_document_by_id(doc_id, user_id=None):
    """Get a document by ID, optionally verify user ownership"""
    try:
        query = supabase.table('documents').select('*').eq('id', doc_id)
        if user_id:
            query = query.eq('user_id', user_id)
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting document: {e}")
        return None


@retry_db_op()
def delete_document(doc_id, user_id):
    """Delete a document"""
    try:
        result = supabase.table('documents').delete().eq('id', doc_id).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False


# ==================== ANALYSIS CACHE OPERATIONS ====================

@retry_db_op()
def save_analysis(document_id, analysis_type, result_data):
    """Save analysis result for a document"""
    try:
        # Check if analysis already exists
        existing = supabase.table('analyses').select('id').eq('document_id', document_id).eq('analysis_type', analysis_type).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing
            result = supabase.table('analyses').update({
                'result': result_data,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', existing.data[0]['id']).execute()
        else:
            # Insert new
            result = supabase.table('analyses').insert({
                'document_id': document_id,
                'analysis_type': analysis_type,
                'result': result_data,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error saving analysis: {e}")
        return None


@retry_db_op()
def get_analysis(document_id, analysis_type):
    """Get cached analysis for a document"""
    try:
        result = supabase.table('analyses').select('*').eq('document_id', document_id).eq('analysis_type', analysis_type).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting analysis: {e}")
        return None
