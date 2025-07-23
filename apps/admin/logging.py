import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

def setup_logging(app):
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

        if app.config.get("MAIL_SERVER"):
            auth = None
            if app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = () if app.config.get("MAIL_USE_TLS") else None

            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"],
                toaddrs=app.config["ADMINS"],
                subject="App Failure",
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)