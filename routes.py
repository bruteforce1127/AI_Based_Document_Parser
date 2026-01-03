"""
Flask Routes for ClarityVault
"""
import os
import uuid
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename

import config
from services import pdf_service, groq_service

# Create blueprint
main = Blueprint('main', __name__)

# Document storage
document_store = {}


def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


# Legacy route for non-authenticated access (kept for backwards compatibility)
@main.route('/upload')
def upload_page():
    """Render the upload page (for non-authenticated users testing)"""
    return render_template('index.html')


@main.route('/viewer/<doc_id>')
def viewer(doc_id):
    """Render the document viewer page"""
    if doc_id not in document_store:
        return render_template('index.html')
    return render_template('viewer.html', doc_id=doc_id)


@main.route('/classify', methods=['POST'])
def classify():
    """Handle PDF upload and classification"""
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
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extract text from PDF (all pages)
        pages = pdf_service.extract_text_from_pdf(filepath)
        
        # Clean up the uploaded file
        os.remove(filepath)
        
        if not pages:
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Combine text for classification
        full_text = ' '.join([p['content'] for p in pages])
        
        # Classify the document
        document_type = groq_service.classify_document(full_text)
        
        # Generate a unique document ID and store the content
        doc_id = str(uuid.uuid4())[:8]
        document_store[doc_id] = {
            'filename': file.filename,
            'document_type': document_type,
            'pages': pages,
            'total_pages': len(pages)
        }
        
        return jsonify({
            'success': True,
            'document_type': document_type,
            'filename': file.filename,
            'doc_id': doc_id,
            'total_pages': len(pages)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/document/<doc_id>')
def get_document(doc_id):
    """Get document content by ID"""
    if doc_id not in document_store:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(document_store[doc_id])


@main.route('/translate', methods=['POST'])
def translate():
    """Handle text translation"""
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
        'original': text,
        'translated': translated,
        'target_language': target_language
    })


@main.route('/translate-document/<doc_id>', methods=['POST'])
def translate_document(doc_id):
    """Translate entire document"""
    if doc_id not in document_store:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    target_language = data.get('target_language', 'English') if data else 'English'
    
    doc = document_store[doc_id]
    
    # Translate all pages
    translated_pages = groq_service.translate_full_document(doc['pages'], target_language)
    
    return jsonify({
        'success': True,
        'filename': doc['filename'],
        'document_type': doc['document_type'],
        'target_language': target_language,
        'translated_pages': translated_pages
    })
