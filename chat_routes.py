"""
Chat Routes - Routes for document Q&A chat
"""
from flask import Blueprint, render_template, request, jsonify, redirect
from functools import wraps
from services import chat_service, database_service, auth_service

chat = Blueprint('chat', __name__)


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


@chat.route('/chat/<doc_id>')
@login_required
def chat_page(doc_id):
    """Render the chat page"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    if not doc:
        return redirect('/dashboard')
    return render_template('chat.html', doc_id=doc_id)


@chat.route('/api/chat/<doc_id>', methods=['POST'])
@login_required
def send_message(doc_id):
    """Send a chat message and get response"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    if not data or not data.get('question'):
        return jsonify({'error': 'No question provided'}), 400
    
    question = data.get('question', '').strip()
    language = data.get('language', 'English')
    
    # Get AI response with context
    result = chat_service.ask_question(
        user_id=user['user_id'],
        doc_id=doc_id,
        document_content=doc['content'],
        document_type=doc['document_type'],
        question=question,
        language=language
    )
    
    return jsonify(result)


@chat.route('/api/chat/<doc_id>/history')
@login_required
def get_history(doc_id):
    """Get chat history for a document"""
    user = get_current_user()
    history = chat_service.get_conversation_history(user['user_id'], doc_id)
    return jsonify({'success': True, 'history': history})


@chat.route('/api/chat/<doc_id>/clear', methods=['POST'])
@login_required
def clear_history(doc_id):
    """Clear chat history for a document"""
    user = get_current_user()
    chat_service.clear_conversation(user['user_id'], doc_id)
    return jsonify({'success': True})


@chat.route('/api/chat/<doc_id>/suggestions')
@login_required
def get_suggestions(doc_id):
    """Get suggested questions for a document"""
    user = get_current_user()
    doc = database_service.get_document_by_id(doc_id, user['user_id'])
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    suggestions = chat_service.get_suggested_questions(doc['document_type'])
    return jsonify({'success': True, 'suggestions': suggestions, 'document_type': doc['document_type']})
