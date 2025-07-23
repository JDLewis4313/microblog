def test_send_welcome_email(app):
    from apps.user.utils import send_welcome_email
    from apps.user.models import User

    with app.app_context():
        user = User(username="Jermarcus", email="j@example.com")
        send_welcome_email(user)
        # If using a debugging server, email will print to console
def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
