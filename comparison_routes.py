"""
Comparison Routes - Routes for market comparison analysis
"""
from flask import Blueprint, render_template, request, jsonify, redirect
from functools import wraps
from services import comparison_service, database_service, auth_service

comparison = Blueprint('comparison', __name__)


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
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@comparison.route('/comparison/<doc_id>')
@login_required
def comparison_page(doc_id):
    """Render the comparison analysis page"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    if not doc:
        return redirect('/dashboard')
    return render_template('comparison.html', doc_id=doc_id)


@comparison.route('/analyze-comparison/<doc_id>', methods=['POST'])
@login_required
def analyze_comparison(doc_id):
    """Perform market comparison analysis on document"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    # Perform comparison analysis
    result = comparison_service.analyze_document_for_comparison(
        doc['content'],
        doc['document_type'],
        target_language
    )
    
    # Get search suggestions
    key_terms = result.get('key_terms', [])
    search_suggestions = comparison_service.get_search_suggestions(
        doc['document_type'],
        key_terms
    )
    
    return jsonify({
        'success': True,
        'document_type': doc['document_type'],
        'filename': doc['filename'],
        'comparison': result,
        'search_suggestions': search_suggestions
    })
