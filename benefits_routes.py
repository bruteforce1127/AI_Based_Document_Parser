"""
Benefits Routes - Routes for benefits analysis dashboard
"""
from flask import Blueprint, render_template, request, jsonify, redirect
from functools import wraps
from services import benefits_service, database_service, auth_service

benefits = Blueprint('benefits', __name__)


def get_current_user():
    token = request.cookies.get('auth_token')
    if token:
        return auth_service.get_user_from_token(token)
    return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@benefits.route('/benefits/<doc_id>')
@login_required
def benefits_page(doc_id):
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    if not doc:
        return redirect('/dashboard')
    return render_template('benefits_dashboard.html', doc_id=doc_id)


@benefits.route('/analyze-benefits/<doc_id>', methods=['POST'])
@login_required
def analyze_benefits(doc_id):
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    result = benefits_service.analyze_document_benefits(
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
