from flask import Flask, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Login configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Comment out other blueprints until we create them
    # from app.products import bp as products_bp
    # app.register_blueprint(products_bp, url_prefix='/products')
    
    # from app.inventory import bp as inventory_bp
    # app.register_blueprint(inventory_bp, url_prefix='/inventory')
    
    # from app.dashboard import bp as dashboard_bp
    # app.register_blueprint(dashboard_bp)
    
    # Main index route - redirect to dashboard (will be protected)
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))  # Redirect to login first
    
    return app