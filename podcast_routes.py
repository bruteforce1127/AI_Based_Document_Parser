"""
Podcast Routes - Handles podcast summary generation
"""
from flask import Blueprint, request, jsonify
from functools import wraps

from services import podcast_service, database_service, auth_service

podcast = Blueprint('podcast', __name__)


def get_current_user():
    """Get current user from JWT cookie"""
    token = request.cookies.get('auth_token')
    if token:
        return auth_service.get_user_from_token(token)
    return None


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@podcast.route('/podcast-summary/<doc_id>', methods=['POST'])
@login_required
def podcast_summary(doc_id):
    """Generate a podcast-style summary of a document"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])

    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'

    content = doc.get('content', '')
    if not content.strip():
        return jsonify({'error': 'Document has no content to summarize'}), 400

    summary = podcast_service.generate_podcast_summary(content, target_language)

    return jsonify({
        'success': True,
        'summary': summary,
        'language': target_language,
        'filename': doc['filename']
    })
