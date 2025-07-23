from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from flask_moment import Moment

db = SQLAlchemy()
login = LoginManager()
mail = Mail()
babel = Babel()
moment = Moment()