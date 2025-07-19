"""
Main Flask application for BitBraniac backend.
"""

import os
import sys

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

from src.config import config
from src.models import init_db
from src.auth import init_jwt
from src.routes.chat import chat_bp
from src.routes.auth import auth_bp
from src.routes.sessions import sessions_bp


def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    # Create Flask app
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    init_db(app)
    init_jwt(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'BitBraniac Backend API',
            'version': '2.0.0',
            'features': ['authentication', 'chat_history', 'ai_tutoring'],
            'success': True
        }
    
    # Serve React frontend (if built files are present)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Run the application
    port = int(os.getenv('PORT', 5001))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )

