from flask import Flask, jsonify
from flask_cors import CORS
import os
from config import Config
from utils.db import init_database
from routes.auth_routes import auth_bp
from routes.event_routes import event_bp
from routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    
    # CORS configuration
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # Initialize database
    with app.app_context():
        if init_database():
            print("Database initialized successfully")
        else:
            print("Failed to initialize database")
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(event_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Event Ticketing API is running'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Event Ticketing API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/auth',
                'api': '/api',
                'admin': '/admin'
            }
        }), 200
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Event Ticketing API on port {port}")
    print("Available endpoints:")
    print("  - Health check: GET /health")
    print("  - Authentication: /auth/*")
    print("  - Public API: /api/*")
    print("  - Admin API: /admin/*")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
