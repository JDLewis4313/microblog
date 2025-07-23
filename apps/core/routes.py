from flask import Blueprint, render_template, request, current_app, jsonify, g, redirect, url_for
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from datetime import datetime
from apps.extensions import db
from apps.blog.models import Post
from apps.core.forms import SearchForm

# Optional translate import
try:
    from apps.translate import translate
except ImportError:
    def translate(text, source_language, dest_language):
        return _('Translation service not configured.')

core_bp = Blueprint('core', __name__, template_folder='../../templates/core')

@core_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@core_bp.route('/', methods=['GET'])
def index():
    return render_template('core/index.html', title=_('Home'), user=current_user)

@core_bp.route('/newsletter', methods=['GET'])
def newsletter():
    return render_template('core/newsletter.html', title=_('Newsletter'))

@core_bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('blog.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('core.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('core.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('core/search.html', title=_('Search'), posts=posts,
                         next_url=next_url, prev_url=prev_url)

@core_bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})