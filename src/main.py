import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy # Added import
# from src.models.user import db # Commented out default user model
# from src.routes.user import user_bp # Commented out default user blueprint

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'), template_folder=os.path.join(os.path.dirname(__file__), 'templates')) # Added template_folder
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_please_change_in_prod') # Made secret key more standard

# Database Configuration (SQLite for development)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///portfolio_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # Initialize SQLAlchemy with the app instance
# Import and register blueprints after db is initialized and models are defined
from src.routes.upload_routes import upload_bp
from src.routes.view_routes import view_bp
app.register_blueprint(upload_bp, url_prefix="/api") # Corrected quoting for url_prefix
app.register_blueprint(view_bp) # Register view_bp, typically without a prefix for root views like '/' and '/dashboard'

# Import models here to ensure they are registered with SQLAlchemy before db.create_all()
from src.models.portfolio_holding import PortfolioHolding # Example, will be created later

with app.app_context():
    db.create_all() # Create database tables if they don't exist

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
            # If index.html not in static, try to serve from templates (e.g. for main app page)
            from flask import render_template
            try:
                return render_template('index.html') # Assuming index.html is the main app page
            except Exception as e:
                return f"index.html not found in static or templates. Error: {str(e)}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
