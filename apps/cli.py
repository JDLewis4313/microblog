import os
import click
from flask import current_app

def register_cli_commands(app):
    
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel init -i messages.pot -d translations -l ' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d translations'):
            raise RuntimeError('compile command failed')

    @app.cli.command()
    def init_db():
        """Initialize the database."""
        from apps.extensions import db
        db.create_all()
        print('Initialized the database.')

    @app.cli.command()
    @click.option('--length', default=25,
                  help='Number of functions to include in the profiler report.')
    @click.option('--profile-dir', default=None,
                  help='Directory where profiler data files are saved.')
    def profile(length, profile_dir):
        """Start the application under the code profiler."""
        from werkzeug.middleware.profiler import ProfilerMiddleware
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                          profile_dir=profile_dir)
        app.run(debug=False)

    @app.cli.command()
    def deploy():
        """Run deployment tasks."""
        from flask_migrate import upgrade
        
        # migrate database to latest revision
        upgrade()
        
        # reindex search if elasticsearch is available
        if current_app.elasticsearch:
            from apps.blog.models import Post
            Post.reindex()
            print('Search indices updated.')
        else:
            print('Elasticsearch not configured - skipping search reindex.')

    @app.cli.command()
    def init_elasticsearch():
        """Initialize Elasticsearch indices."""
        if not current_app.elasticsearch:
            print('Elasticsearch is not configured.')
            return
        from apps.blog.models import Post
        Post.reindex()
        print('Elasticsearch indices initialized.')