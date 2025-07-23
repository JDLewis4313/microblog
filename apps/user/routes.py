#apps/user/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse as url_parse
from datetime import datetime
from flask_babel import _

from apps.extensions import db, login
from apps.user.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, ResetPasswordRequestForm, ResetPasswordForm, MessageForm
from apps.user.utils import send_password_reset_email
from apps.user.models import User, Message, Notification
from apps.blog.models import Post

user_bp = Blueprint(
    'user',
    __name__,
    template_folder='../../templates/user'
)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@user_bp.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u is None or not u.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('user.login'))

        login_user(u, remember=form.remember_me.data)
        nxt = request.args.get('next')
        if not nxt or url_parse(nxt).netloc:
            nxt = url_for('core.index')
        return redirect(nxt)

    return render_template(
        'login.html',
        title='Sign In',
        form=form
    )

@user_bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('core.index'))

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        new_u = User(
            username=form.username.data,
            email=form.email.data
        )
        new_u.set_password(form.password.data)
        db.session.add(new_u)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('user.login'))

    return render_template(
        'register.html',
        title='Register',
        form=form
    )

@user_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me  = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user.edit_profile'))

    form.username.data = current_user.username
    form.about_me.data  = current_user.about_me
    return render_template(
        'edit_profile.html',
        title='Edit Profile',
        form=form
    )

@user_bp.route('/<username>', methods=['GET'])
@login_required
def profile(username):
    u = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    
    # Add pagination to user profile posts
    page = request.args.get('page', 1, type=int)
    posts = u.posts.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    
    next_url = url_for('user.profile', username=u.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user.profile', username=u.username, page=posts.prev_num) \
        if posts.has_prev else None
    
    return render_template(
        'user.html',
        user=u,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form
    )

@user_bp.route('/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        target = User.query.filter_by(username=username).first()
        if not target:
            flash(f'User {username} not found.')
            return redirect(url_for('core.index'))
        if target == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for('user.profile', username=username))

        current_user.follow(target)
        db.session.commit()
        flash(f'You are following {username}!')

    return redirect(url_for('user.profile', username=username))

@user_bp.route('/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        target = User.query.filter_by(username=username).first()
        if not target:
            flash(f'User {username} not found.')
            return redirect(url_for('core.index'))
        if target == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for('user.profile', username=username))

        current_user.unfollow(target)
        db.session.commit()
        flash(f'You are not following {username}.')

    return redirect(url_for('user.profile', username=username))

@user_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('user.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@user_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('core.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('user.login'))
    return render_template('reset_password.html', form=form)

@user_bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)

@user_bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('user.profile', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)

@user_bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('user.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('user.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)

@user_bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])

# Export Route 

@user_bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('user.profile', username=current_user.username))