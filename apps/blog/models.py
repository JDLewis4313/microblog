from datetime import datetime
from apps.extensions import db
from apps.search import SearchableMixin

class Post(SearchableMixin, db.Model):
    __tablename__ = 'post'
    __searchable__ = ['body']
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return f"<Post {self.body}>"