from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    email_link = db.relationship("EmailLink", back_populates="user")
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship("Group", back_populates="users")
    admin = db.Column(db.Boolean(), default=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    users = db.relationship("User", back_populates="group")
    view_all_incidents = db.Column(db.Boolean(), default=False)
    change_status = db.Column(db.Boolean(), default=False)
    change_allocations = db.Column(db.Boolean(), default=False)
    mark_as_public = db.Column(db.Boolean(), default=False)
    create_deployments = db.Column(db.Boolean(), default=False)
    decision_making_log = db.Column(db.Boolean(), default=False)
    new_reports = db.Column(db.Boolean(), default=False)
    supervisor = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return f'<Group {self.name}>'

class EmailLink(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship("User", back_populates="email_link")
    link = db.Column(db.String(128), unique=True)
    verify = db.Column(db.Boolean(), default=False)
    forgot_password = db.Column(db.Boolean(), default=False)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))