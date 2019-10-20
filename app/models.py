from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    email_link = db.relationship("EmailLink", back_populates="user")
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group', back_populates='users')
    admin = db.Column(db.Boolean(), default=False)
    actions = db.relationship('ActionLog', backref='user', lazy=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Group(db.Model):
    permission_values = {"view_all_incidents": 0x1, "change_status": 0x2, "change_allocations": 0x4,
                         "mark_as_public": 0x8,
                         "new_reports": 0x16, "create_deployments": 0x32, "decision_making_log": 0x64,
                         "supervisor": 0x128}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    users = db.relationship('User', back_populates='group')
    permissions = db.Column(db.Integer)

    def set_permissions(self, permission_list):
        permission_value = 0
        for item in permission_list:
            try:
                permission_value += self.permission_values[item.lower()]
            except ValueError:
                pass
        self.permissions = int(permission_value)

    def has_permission(self, permission):
        try:
            if self.permissions & self.permission_values[permission.lower()] > 0:
                return True
            return False
        except ValueError:
            return False

    def __repr__(self):
        return f'<Group {self.name}>'


class EmailLink(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', back_populates='email_link')
    link = db.Column(db.String(128), unique=True)
    verify = db.Column(db.Boolean(), default=False)
    forgot_password = db.Column(db.Boolean(), default=False)


class ActionLog(db.Model):
    action_values = {"create_user": 1, "verify_user": 2, "delete_user": 3, "create_group": 4, "delete_group": 5}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action_type = db.Column(db.Integer())
    target_id = db.Column(db.Integer)
    reason = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
