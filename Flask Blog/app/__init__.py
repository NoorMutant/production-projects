import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor
import logging
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
ckeditor = CKEditor()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'Your Secret Key Here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)

    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Configure logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # Register blueprints
    from app.routes import main, auth 
    app.register_blueprint(main)
    app.register_blueprint(auth)

    # Create tables
    with app.app_context():
        db.create_all()

    return app