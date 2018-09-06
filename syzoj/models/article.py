from syzoj import db
import time


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("articles", lazy='dynamic'))

    public_time = db.Column(db.Integer)  # goodbye at 2038-1-19
    update_time = db.Column(db.Integer)
    sort_time = db.Column(db.Integer, index=True)

    tags = db.Column(db.Text)

    comments_num = db.Column(db.Integer)
    allow_comment = db.Column(db.Boolean)

    def __init__(self, title, content, user, allow_comment=True, public_time=None):
        if not public_time:
            public_time = int(time.time())
        self.title = title
        self.content = content
        self.user = user
        self.public_time = public_time
        self.update_time = public_time
        self.sort_time = public_time
        self.comments_num = 0
        self.allow_comment = allow_comment

    def __repr__(self):
        return "<Article %r>" % self.title

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_allowed_edit(self, user=None):
        if not user:
            return False
        if user.id == self.user_id:
            return True
        if user.have_privilege(6):
            return True
        return False


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), index=True)
    article = db.relationship("Article", backref=db.backref("comments", lazy='dynamic'))

    origin_comment_id = db.Column(db.Integer, db.ForeignKey("comment.id"), index=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("comments", lazy='dynamic'))

    public_time = db.Column(db.Integer)  # goodbye at 2038-1-19

    def __init__(self, content, article, user, public_time=None):
        if not public_time:
            public_time = int(time.time())
        self.content = content
        self.article = article
        self.user = user
        self.public_time = public_time

    def __repr__(self):
        return "<Comment %r>" % self.content

    def is_allowed_edit(self, user=None):
        if not user:
            return False
        if user.id == self.user_id:
            return True
        if user.have_privilege(6):
            return True
        return False

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    user = db.relationship("User", backref=db.backref("notices", lazy='dynamic'))

    public_time = db.Column(db.Integer)  # goodbye at 2038-1-19
    update_time = db.Column(db.Integer)
    sort_time = db.Column(db.Integer, index=True)

    tags = db.Column(db.Text)

    comments_num = db.Column(db.Integer)
    allow_comment = db.Column(db.Boolean)

    def __init__(self, title, content, user, allow_comment=True, public_time=None):
        if not public_time:
            public_time = int(time.time())
        self.title = title
        self.content = content
        self.user = user
        self.public_time = public_time
        self.update_time = public_time
        self.sort_time = public_time
        self.comments_num = 0
        self.allow_comment = allow_comment

    def __repr__(self):
        return "<Notice %r>" % self.title

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_allowed_edit(self, user=None):
        if user and user.have_privilege(1):
            return True
        if not user:
            return False
        return False
