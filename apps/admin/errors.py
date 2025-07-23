from flask import render_template
from apps.extensions import db

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("admin/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("admin/500.html"), 500