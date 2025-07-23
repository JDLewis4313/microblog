from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, g
from flask_login import login_required, current_user
from flask_babel import _, get_locale

# Optional language detection
try:
    from langdetect import detect, LangDetectError
except ImportError:
    def detect(text):
        return ''
    class LangDetectError(Exception):
        pass

from apps.extensions import db
from apps.blog.forms import PostForm
from apps.blog.models import Post

blog_bp = Blueprint(
    'blog',
    __name__,
    template_folder='../../templates/blog'
)

@blog_bp.route('/', methods=['GET', 'POST'])
@login_required
def blog():
    form = PostForm()
    if form.validate_on_submit():
        language = detect(form.body.data)
        try:
            language = detect(form.body.data)
        except LangDetectError:
            language = ''
        
        p = Post(body=form.body.data, author=current_user, language=language)
        db.session.add(p)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('blog.blog'))

    # Pagination for followed posts
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, 
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    
    next_url = url_for('blog.blog', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('blog.blog', page=posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('blog/blog.html',
                           title=_('Blog'), 
                           form=form, 
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)

@blog_bp.route('/explore')
@login_required
def explore():
    """Explore all posts from all users"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    
    next_url = url_for('blog.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('blog.explore', page=posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('blog/explore.html',
                           title=_('Explore'),
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)