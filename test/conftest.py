import pytest
import sys, os

# 1) ensure project root is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2) import your real Flask app and unified db
from app import app as flask_app
from apps.db import db

@pytest.fixture(scope="session")
def app():
    return flask_app

@pytest.fixture(scope="session")
def app_context(app):
    ctx = app.app_context()
    ctx.push()
    yield ctx
    ctx.pop()

@pytest.fixture(autouse=True)
def clean_db(app_context):
    db.drop_all()
    db.create_all()
    yield
    db.session.rollback()
    db.session.remove()

@pytest.fixture
def client(app):
    return app.test_client()
