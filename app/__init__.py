from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///study_tool.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Add utility functions to templates
    @app.template_global()
    def hasattr_jinja(obj, attr):
        return hasattr(obj, attr)
    
    app.jinja_env.globals.update(hasattr=hasattr_jinja)
    
    # Register blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.dashboard import dashboard_bp
    from app.controllers.schedule import schedule_bp
    from app.controllers.materials import materials_bp
    from app.controllers.skills import skills_bp
    from app.controllers.profile import profile_bp
    from app.controllers.ai_assistant import ai_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(ai_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 