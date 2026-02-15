"""
ClarityVault - PDF Document Classifier with Translation
Main application entry point
"""
import os
from flask import Flask, redirect
import config
from routes import main
from analysis_routes import analysis
from consequences_routes import consequences
from auth_routes import auth
from auth_doc_routes import auth_doc
from comparison_routes import comparison
from chat_routes import chat
from risk_routes import risk
from benefits_routes import benefits
from podcast_routes import podcast

# Create Flask app
app = Flask(__name__)

# Configure app
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(main)
app.register_blueprint(analysis)
app.register_blueprint(consequences)
app.register_blueprint(auth)
app.register_blueprint(auth_doc)
app.register_blueprint(comparison)
app.register_blueprint(chat)
app.register_blueprint(risk)
app.register_blueprint(benefits)
app.register_blueprint(podcast)


# Root redirect to dashboard/login
@app.route('/')
def index():
    """Redirect to dashboard or login"""
    from auth_routes import get_current_user
    user = get_current_user()
    if user:
        return redirect('/dashboard')
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
