"""
Authenticated Routes - Routes that require login and save to database
"""
import os
import uuid
from flask import Blueprint, render_template, request, jsonify, redirect
from functools import wraps
from werkzeug.utils import secure_filename

import config
from services import pdf_service, groq_service, database_service, auth_service

auth_doc = Blueprint('auth_doc', __name__)


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


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


# ==================== DOCUMENT ROUTES ====================

@auth_doc.route('/classify-auth', methods=['POST'])
@login_required
def classify_auth():
    """Handle PDF upload with authentication and database storage"""
    user = get_current_user()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Ensure upload folder exists
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extract text
        pages = pdf_service.extract_text_from_pdf(filepath)
        
        # Clean up
        os.remove(filepath)
        
        if not pages:
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Combine text for classification
        full_text = '\n\n'.join([p['content'] for p in pages])
        
        # Classify
        document_type = groq_service.classify_document(full_text)
        
        # Save to database
        doc = database_service.save_document(
            user_id=user['user_id'],
            filename=file.filename,
            document_type=document_type,
            content=full_text,
            pages_count=len(pages)
        )
        
        if not doc:
            return jsonify({'error': 'Failed to save document'}), 500
        
        return jsonify({
            'success': True,
            'document_type': document_type,
            'filename': file.filename,
            'doc_id': doc['id'],
            'total_pages': len(pages)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_doc.route('/viewer-auth/<doc_id>')
@login_required
def viewer_auth(doc_id):
    """Render authenticated document viewer"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    if not doc:
        return redirect('/dashboard')
    return render_template('viewer_auth.html', doc_id=doc_id)


@auth_doc.route('/document-auth/<doc_id>')
@login_required
def get_document_auth(doc_id):
    """Get document content for authenticated user"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    # Parse content into pages (simple split by page markers if present)
    content = doc.get('content', '')
    pages = []
    
    # Try to split by page markers
    if '--- Page ' in content:
        parts = content.split('--- Page ')
        for i, part in enumerate(parts[1:], 1):
            lines = part.split('\n', 1)
            page_content = lines[1] if len(lines) > 1 else ''
            pages.append({'page_number': i, 'content': page_content.strip()})
    else:
        # Single page
        pages.append({'page_number': 1, 'content': content})
    
    return jsonify({
        'filename': doc['filename'],
        'document_type': doc['document_type'],
        'pages': pages,
        'total_pages': doc.get('pages_count', len(pages))
    })


@auth_doc.route('/analysis-auth/<doc_id>')
@login_required
def analysis_auth(doc_id):
    """Render authenticated analysis page"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    if not doc:
        return redirect('/dashboard')
    return render_template('analysis_auth.html', doc_id=doc_id)


@auth_doc.route('/consequences-auth/<doc_id>')
@login_required
def consequences_auth(doc_id):
    """Render authenticated consequences page"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    if not doc:
        return redirect('/dashboard')
    return render_template('consequences_auth.html', doc_id=doc_id)


@auth_doc.route('/translate-auth', methods=['POST'])
@login_required
def translate_auth():
    """Handle translation for authenticated users"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    text = data.get('text', '')
    target_language = data.get('target_language', 'English')
    
    if not text:
        return jsonify({'error': 'No text to translate'}), 400
    
    translated = groq_service.translate_text(text, target_language)
    
    return jsonify({
        'success': True,
        'translated': translated,
        'target_language': target_language
    })


@auth_doc.route('/analyze-terms-auth/<doc_id>', methods=['POST'])
@login_required
def analyze_terms_auth(doc_id):
    """Analyze document for difficult terms (authenticated)"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    terms = groq_service.analyze_difficult_terms(doc['content'], target_language)
    
    return jsonify({
        'success': True,
        'terms': terms,
        'document_type': doc['document_type'],
        'filename': doc['filename']
    })


@auth_doc.route('/analyze-consequences-auth/<doc_id>', methods=['POST'])
@login_required
def analyze_consequences_auth(doc_id):
    """Analyze document for consequences (authenticated)"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    result = groq_service.analyze_consequences(doc['content'], target_language)
    
    return jsonify({
        'success': True,
        'document_type': result.get('document_type', doc['document_type']),
        'rules': result.get('rules', []),
        'consequences': result.get('consequences', []),
        'summary': result.get('summary', ''),
        'filename': doc['filename']
    })


@auth_doc.route('/translate-document-auth/<doc_id>', methods=['POST'])
@login_required
def translate_document_auth(doc_id):
    """Translate entire document (authenticated)"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    # Create pages from content
    content = doc.get('content', '')
    pages = [{'page_number': 1, 'content': content}]
    
    translated_pages = groq_service.translate_full_document(pages, target_language)
    
    return jsonify({
        'success': True,
        'filename': doc['filename'],
        'target_language': target_language,
        'translated_pages': translated_pages
    })
