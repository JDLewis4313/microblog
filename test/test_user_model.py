import pytest

from datetime import datetime, timedelta
from apps.user.models import User
from apps.blog.models import Post
from apps.db import db

def test_password_hashing():
    u = User(username="susan")
    u.set_password("cat")
    assert not u.check_password("dog")
    assert u.check_password("cat")

def test_avatar():
    u = User(username="john", email="john@example.com")
    avatar_url = u.avatar(128)
    assert "gravatar.com/avatar" in avatar_url

def test_follow():
    u1 = User(username="john", email="john@example.com")
    u2 = User(username="susan", email="susan@example.com")
    db.session.add_all([u1, u2])
    db.session.commit()

    u1.follow(u2)
    db.session.commit()

    assert u1.is_following(u2)
    assert u2.followers.count() == 1

def test_followed_posts():
    u1 = User(username="john", email="john@example.com")
    u2 = User(username="susan", email="susan@example.com")
    now = datetime.utcnow()
    p1 = Post(body="post from john", author=u1, timestamp=now + timedelta(seconds=1))
    p2 = Post(body="post from susan", author=u2, timestamp=now + timedelta(seconds=2))

    db.session.add_all([u1, u2, p1, p2])
    u1.follow(u2)
    db.session.commit()

    posts = u1.followed_posts().all()
    assert posts == [p2, p1] or (p2 in posts and p1 in posts)

def test_send_welcome_email(app):
    from apps.user.utils import send_welcome_email
    from apps.user.models import User
    with app.app_context():
        user = User(username="Jermarcus", email="j@example.com")
        send_welcome_email(user)

def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
