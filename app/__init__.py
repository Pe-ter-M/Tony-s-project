from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_required
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
    login_manager.login_view = 'auth.login'  # type: ignore
    login_manager.login_message_category = 'info'
    
    # Import and register user loader
    from app.models.user import load_user
    # The @login_manager.user_loader decorator in user.py handles this
    
    # Register blueprints
    from app.auth import bp as auth_bp
    from app.store import store_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(store_bp)
    
    # Main index route - protected
    @app.route('/')
    # @login_required
    def index():
        return render_template('index.html', user=current_user)
    
    return app