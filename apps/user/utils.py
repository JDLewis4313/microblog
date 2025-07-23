from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from apps.extensions import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_welcome_email(user):
    msg = Message(
        subject="Welcome to the Microblog!",
        sender=current_app.config["MAIL_USERNAME"] or "noreply@localhost",
        recipients=[user.email]
    )
    msg.body = f"Hi {user.username},\n\nThanks for joining the journey!"
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.warning(f"Email send failed: {e}")