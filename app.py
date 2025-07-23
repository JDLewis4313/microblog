#app.py
import os
from flask import Flask, request, g
from flask_migrate import Migrate
from config.settings import Config
from apps.extensions import db, login, mail, babel, moment
from apps.admin.errors import register_error_handlers
from apps.admin.logging import setup_logging
from apps.cli import register_cli_commands
import redis
import rq
from apps.api import bp as api_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # Initialize Redis and RQ
    app.redis = redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('portfolio-tasks', connection=app.redis)
    
    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')

    # Elasticsearch - Optional import
    if app.config.get('ELASTICSEARCH_URL'):
        try:
            from elasticsearch import Elasticsearch
            app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        except ImportError:
            pass

    # Configure login manager
    login.login_view = 'user.login'
    login.login_message = 'Please log in to access this page.'

    # Babel configuration with version compatibility
    def get_locale():
        return request.accept_languages.best_match(app.config.get('LANGUAGES', ['en']))
    
    try:
        babel.init_app(app, locale_selector=get_locale)
    except TypeError:
        babel.init_app(app)
        babel.localeselector(get_locale)

    @app.before_request
    def before_request():
        g.locale = str(get_locale())

    # Register blueprints
    from apps.core.routes import core_bp
    from apps.user.routes import user_bp
    from apps.blog.routes import blog_bp
    
    app.register_blueprint(core_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(blog_bp)

    # Register additional components
    setup_logging(app)
    register_error_handlers(app)
    register_cli_commands(app)

    # Search event handlers
    from apps.search import SearchableMixin
    db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
    db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

    @app.shell_context_processor
    def make_shell_context():
        from apps.user.models import User, Message, Notification, Task
        from apps.blog.models import Post
        return {'db': db, 'User': User, 'Post': Post, 'Message': Message, 'Notification': Notification, 'Task': Task}

    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
