"""
Risk Routes - Routes for risk analysis dashboard
"""
from flask import Blueprint, render_template, request, jsonify, redirect
from functools import wraps
from services import risk_service, database_service, auth_service

risk = Blueprint('risk', __name__)


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


@risk.route('/risk/<doc_id>')
@login_required
def risk_page(doc_id):
    """Render the risk analysis dashboard"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    if not doc:
        return redirect('/dashboard')
    return render_template('risk_dashboard.html', doc_id=doc_id)


@risk.route('/analyze-risk/<doc_id>', methods=['POST'])
@login_required
def analyze_risk(doc_id):
    """Perform risk analysis on document"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    # Perform risk analysis
    result = risk_service.analyze_document_risks(
        doc['content'],
        doc['document_type'],
        target_language
    )
    
    return jsonify({
        'success': True,
        'document_type': doc['document_type'],
        'filename': doc['filename'],
        'analysis': result
    })
