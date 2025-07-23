from decouple import config
import os

basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.dirname(basedir)

class Config:
    SECRET_KEY = config("SECRET_KEY", default="fallback-key")
    DEBUG = config("DEBUG", default=False, cast=bool)
    FLASK_ENV = config("FLASK_ENV", default="development")
    TESTING = config("TESTING", default=False, cast=bool)

    # Database
    db_dir = os.path.join(basedir, 'db')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    SQLALCHEMY_DATABASE_URI = config(
        "DATABASE_URL",
        default=f"sqlite:///{os.path.join(basedir, 'db', 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pagination
    POSTS_PER_PAGE = config("POSTS_PER_PAGE", default=5, cast=int)

    # Languages
    LANGUAGES = ['en', 'es']

    # Email
    MAIL_SERVER = config("MAIL_SERVER", default=None)
    MAIL_PORT = config("MAIL_PORT", default=25, cast=int)
    MAIL_USE_TLS = config("MAIL_USE_TLS", default=False, cast=bool)
    MAIL_USERNAME = config("MAIL_USERNAME", default=None)
    MAIL_PASSWORD = config("MAIL_PASSWORD", default=None)
    ADMINS = config("ADMINS", default="admin@example.com").split(",")

    # Search
    ELASTICSEARCH_URL = None

    # Translation
    MS_TRANSLATOR_KEY = config("MS_TRANSLATOR_KEY", default=None)
    MS_TRANSLATOR_REGION = config("MS_TRANSLATOR_REGION", default="eastus")

    # Background Jobs (Redis)
    REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")