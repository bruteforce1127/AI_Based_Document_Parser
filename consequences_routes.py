"""
Consequences Routes - Routes for rules and consequences analysis feature
"""
from flask import Blueprint, render_template, request, jsonify
from services import openai_service
from routes import document_store

consequences = Blueprint('consequences', __name__)


@consequences.route('/consequences/<doc_id>')
def consequences_page(doc_id):
    """Render the consequences analysis page"""
    if doc_id not in document_store:
        return render_template('index.html')
    return render_template('consequences.html', doc_id=doc_id)


@consequences.route('/analyze-consequences/<doc_id>', methods=['POST'])
def analyze_consequences(doc_id):
    """Analyze document for rules and consequences"""
    if doc_id not in document_store:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    doc = document_store[doc_id]
    
    # Combine all page content
    full_text = '\n\n'.join([p['content'] for p in doc['pages']])
    
    # Analyze for rules and consequences
    result = openai_service.analyze_consequences(full_text, target_language)
    
    return jsonify({
        'success': True,
        'document_type': result.get('document_type', doc['document_type']),
        'rules': result.get('rules', []),
        'consequences': result.get('consequences', []),
        'summary': result.get('summary', ''),
        'filename': doc['filename']
    })
