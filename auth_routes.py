"""
Auth Routes - Login, Signup, and Dashboard routes
"""
from flask import Blueprint, render_template, request, jsonify, redirect, make_response
from functools import wraps
from services import auth_service, database_service

auth = Blueprint('auth', __name__)


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


# ==================== AUTH PAGES ====================

@auth.route('/login')
def login_page():
    """Render login page"""
    user = get_current_user()
    if user:
        return redirect('/dashboard')
    return render_template('login.html')


@auth.route('/signup')
def signup_page():
    """Render signup page"""
    user = get_current_user()
    if user:
        return redirect('/dashboard')
    return render_template('signup.html')


@auth.route('/dashboard')
@login_required
def dashboard():
    """Render user dashboard"""
    user = get_current_user()
    documents = database_service.get_user_documents(user['user_id'])
    return render_template('dashboard.html', user=user, documents=documents)


@auth.route('/logout')
def logout():
    """Logout user"""
    response = make_response(redirect('/login'))
    response.delete_cookie('auth_token')
    return response


# ==================== AUTH API ====================

@auth.route('/api/signup', methods=['POST'])
def api_signup():
    """Handle signup"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validation
    if not name or len(name) < 2:
        return jsonify({'error': 'Name must be at least 2 characters'}), 400
    if not email or '@' not in email:
        return jsonify({'error': 'Invalid email address'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if user exists
    existing = database_service.get_user_by_email(email)
    if existing:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    password_hash = auth_service.hash_password(password)
    user = database_service.create_user(name, email, password_hash)
    
    if not user:
        return jsonify({'error': 'Failed to create account. Please try again.'}), 500
    
    # Create token
    token = auth_service.create_token(user['id'], email, name)
    
    response = jsonify({'success': True, 'message': 'Account created successfully'})
    response.set_cookie('auth_token', token, max_age=90*24*60*60, httponly=True, samesite='Lax')
    
    return response


@auth.route('/api/login', methods=['POST'])
def api_login():
    """Handle login"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Get user
    user = database_service.get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Verify password
    if not auth_service.verify_password(password, user['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create token
    token = auth_service.create_token(user['id'], email, user['name'])
    
    response = jsonify({'success': True, 'message': 'Login successful'})
    response.set_cookie('auth_token', token, max_age=90*24*60*60, httponly=True, samesite='Lax')
    
    return response


@auth.route('/api/me')
def api_me():
    """Get current user info"""
    user = get_current_user()
    if user:
        return jsonify({'authenticated': True, 'user': user})
    return jsonify({'authenticated': False})


# ==================== DOCUMENT API ====================

@auth.route('/api/documents')
@login_required
def api_documents():
    """Get user's documents"""
    user = get_current_user()
    documents = database_service.get_user_documents(user['user_id'])
    return jsonify({'success': True, 'documents': documents})


@auth.route('/api/documents/<doc_id>')
@login_required
def api_document(doc_id):
    """Get a specific document"""
    user = get_current_user()
    document = database_service.get_document_by_id(doc_id, user['user_id'])
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    return jsonify({'success': True, 'document': document})


@auth.route('/api/documents/<doc_id>', methods=['DELETE'])
@login_required
def api_delete_document(doc_id):
    """Delete a document"""
    user = get_current_user()
    success = database_service.delete_document(doc_id, user['user_id'])
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to delete document'}), 500
