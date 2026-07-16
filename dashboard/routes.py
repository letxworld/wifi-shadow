from flask import render_template

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint for testing"""
        return {'status': 'ok', 'service': 'wifi-shadow'}
    
    @app.route('/api/version')
    def version():
        """Return version info"""
        return {
            'name': 'wifi-shadow',
            'version': '0.1.0',
            'description': 'Network attack awareness & education tool'
        }