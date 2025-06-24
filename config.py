import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env (ignored in git)
load_dotenv()

# Base directory - resolves to /home/ec2-user
basedir = Path(__file__).parent.resolve()

# Database path - explicitly set to /home/ec2-user/instance/saasight.db
db_path = basedir / "instance" / "saasight.db"
db_path.parent.mkdir(exist_ok=True, mode=0o775)

class Config:
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set in environment variables.")

    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    FLASK_APP = 'run.py'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:////home/ec2-user/instance/saasight.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SESSION_PROTECTION = 'strong'
    REMEMBER_COOKIE_DURATION = 3600  # seconds
    
    # Bcrypt
    BCRYPT_LOG_ROUNDS = 12
    
    # Pagination
    BOARDGAMES_PER_PAGE = 10
    REVIEWS_PER_PAGE = 5
    
    # File Uploads
    UPLOAD_FOLDER = str(basedir / 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB

    # Email Config (safely from env only)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("⚠️  MAIL_USERNAME or MAIL_PASSWORD not set. Email features may not work.")

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    FLASK_ENV = 'development'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
