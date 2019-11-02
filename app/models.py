import pyavagen
from os import path
from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

deployment_user_junction = db.Table('deployment_users',
                                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                    db.Column('deployment_id', db.Integer, db.ForeignKey('deployment.id')),
                                    )

deployment_group_junction = db.Table('deployment_groups',
                                     db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
                                     db.Column('deployment_id', db.Integer, db.ForeignKey('deployment.id')),
                                     )

incident_user_junction = db.Table('incident_users',
                                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                  db.Column('incident_id', db.Integer, db.ForeignKey('incident.id')),
                                  )

incidenttask_user_junction = db.Table('incident_tasks',
                                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                      db.Column('id', db.Integer, db.ForeignKey('incident_task.id')),
                                      )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean(), default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    deployments = db.relationship('Deployment', secondary=deployment_user_junction)
    incidents = db.relationship('Incident', secondary=incident_user_junction)
    tasks = db.relationship('IncidentTask', secondary=incidenttask_user_junction)
    audit_actions = db.relationship('AuditLog', backref='user', lazy=True)
    incident_actions = db.relationship('IncidentLog', backref='user', lazy=True)
    incident_comments = db.relationship('IncidentComment', backref='user')
    media_uploads = db.relationship('IncidentMedia', backref='uploaded_by')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def create_avatar(self):
        avatar = pyavagen.Avatar(pyavagen.CHAR_SQUARE_AVATAR, size=500, string=self.username)
        avatar.generate().save(f'./app/static/img/avatars/{self.username.replace(" ", "_")}.png')

    def get_avatar(self):
        avatar_path = f'/static/img/avatars/{self.username.replace(" ", "_")}.png'
        if path.exists(avatar_path):
            return avatar_path
        self.create_avatar()
        return avatar_path

    def get_deployments(self):
        deployments = []
        for x in Deployment.query.all():
            if not x.groups and not x.users:
                deployments.append(x)
            else:
                if self in x.users:
                    deployments.append(x)
                for y in x.groups:
                    if y.id == self.group_id:
                        deployments.append(x)
                        continue
        return deployments

    def get_incidents(self, deployment_id):
        incidents = []
        deployment = Deployment.query.filter_by(id=deployment_id).first()
        if self.group_id and Group.query.filter_by(id=self.group_id).first().has_permission('view_all_incidents'):
            return deployment.incidents
        for x in deployment.incidents:
            if self.id in x.users:
                incidents.append(x)
        return incidents


    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Group(db.Model):
    permission_values = {'view_all_incidents': 0x1, 'change_status': 0x2, 'change_allocations': 0x4,
                         'mark_as_public': 0x8,
                         'new_reports': 0x16, 'create_deployments': 0x32, 'decision_making_log': 0x64,
                         'supervisor': 0x128}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    users = db.relationship('User', backref='group')
    deployments = db.relationship('Deployment', secondary=deployment_group_junction)
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
        if self.permission_values['supervisor']:
            return True
        try:
            if self.permissions & self.permission_values[permission.lower()] > 0:
                return True
            return False
        except ValueError:
            return False

    def __repr__(self):
        return f'<Group {self.name}>'


class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(256))
    open_status = db.Column(db.Boolean(), default=True)
    incidents = db.relationship('Incident', backref='deployment')
    groups = db.relationship('Group', secondary=deployment_group_junction)
    users = db.relationship('User', secondary=deployment_user_junction)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Incident(db.Model):
    priorities = {1: 'standard', 2: 'prompt', 3: 'immediate'}
    incident_types = {}  ##TODO Get incident types.
    # TODO Add who has this pinned.
    id = db.Column(db.Integer, primary_key=True, index=True)
    deployment_id = db.Column(db.Integer, db.ForeignKey('deployment.id'))
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(256))
    incident_type = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    public = db.Column(db.Boolean(), default=False)
    flagged = db.Column(db.Boolean(), default=False)
    open_status = db.Column(db.Boolean(), default=True)
    location = db.Column(db.String(128), index=True)
    priority = db.Column(db.Integer())
    longitude = db.Column(db.Float())
    latitude = db.Column(db.Float())
    users = db.relationship('User', secondary=incident_user_junction)
    tasks = db.relationship('IncidentTask', backref='incident')
    comments = db.relationship('IncidentComment', backref='incident')
    medias = db.relationship('IncidentMedia', backref='incident')
    actions = db.relationship('IncidentLog', backref='incident')

    def get_priority(self):
        return self.priorities[1].title() ##TODO REMOVE
        return self.priorities[self.priority].title()

    def calculate_task_percentage(self):
        if not self.tasks:
            return None
        return int(sum([1 for m in self.tasks if m.completed])/len(self.tasks))

class IncidentTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    name = db.Column(db.String(64))
    details = db.Column(db.String(1024))
    completed_details = db.Column(db.String(1024))
    completed = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    allocated_to = db.relationship('User', secondary=incidenttask_user_junction)


class IncidentComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(1024))
    highlight = db.Column(db.Boolean(), default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)


class IncidentMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    saved_as = db.Column(db.String(64))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmailLink(db.Model):  ##TODO Cascade
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='email_link')  ##Maybe unused so not needed.
    link = db.Column(db.String(128), unique=True)
    verify = db.Column(db.Boolean(), default=False)
    forgot_password = db.Column(db.Boolean(), default=False)


class AuditLog(db.Model):
    action_values = {'create_user': 1, 'verify_user': 2, 'edit_user': 3, 'delete_user': 4, 'create_group': 5,
                     'edit_group': 6, 'delete_group': 7, 'create_deployment': 8, 'edit_deployment': 9,
                     'delete_deployment': 10}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action_type = db.Column(db.Integer())
    target_id = db.Column(db.Integer)
    reason = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class IncidentLog(db.Model):
    action_values = {'create_incident': 1, 'create_task': 2, 'complete_task': 3, 'delete_task': 4, 'add_comment': 5,
                     'delete_comment': 6}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    action_type = db.Column(db.Integer())
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
