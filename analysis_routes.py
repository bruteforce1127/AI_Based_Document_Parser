"""
Analysis Routes - Routes for tough words analysis feature
"""
from flask import Blueprint, render_template, request, jsonify
from services import groq_service, youtube_service
from routes import document_store

analysis = Blueprint('analysis', __name__)


@analysis.route('/analysis/<doc_id>')
def analysis_page(doc_id):
    """Render the analysis page"""
    if doc_id not in document_store:
        return render_template('index.html')
    return render_template('analysis.html', doc_id=doc_id)


@analysis.route('/analyze-terms/<doc_id>', methods=['POST'])
def analyze_terms(doc_id):
    """Analyze document for difficult terms"""
    if doc_id not in document_store:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    doc = document_store[doc_id]
    
    # Combine all page content
    full_text = '\n\n'.join([p['content'] for p in doc['pages']])
    
    # Analyze for difficult terms
    terms = groq_service.analyze_difficult_terms(full_text, target_language)
    
    return jsonify({
        'success': True,
        'terms': terms,
        'document_type': doc['document_type'],
        'filename': doc['filename']
    })


@analysis.route('/get-videos', methods=['POST'])
def get_videos():
    """Get YouTube videos for terms"""
    data = request.get_json()
    
    if not data or 'terms' not in data:
        return jsonify({'error': 'No terms provided'}), 400
    
    terms = data['terms'][:5]  # Limit to 5 terms to avoid too many API calls
    
    videos = youtube_service.search_videos_for_terms(terms, max_per_term=2)
    
    return jsonify({
        'success': True,
        'videos': videos
    })
