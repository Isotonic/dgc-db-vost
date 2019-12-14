import pyavagen
from flask import url_for
from string import Template
from os import path, makedirs
from flask_admin import Admin  ##TODO Remove
from flask_login import UserMixin
from app import app, db, login, argon2
from datetime import datetime, timedelta
from flask_admin.contrib.sqla import ModelView

avatar_colours = ['#26de81', '#3867d6', '#eb3b5a', '#0fb9b1', '#f7b731', '#a55eea', '#fed330', '#45aaf2', '#fa8231',
                  '#2bcbba', '#fd9644', '#2d98da', '#8854d0', '#20bf6b', '#fc5c65', '#4b7bec']

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

incident_pinned_junction = db.Table('incident_pins',
                                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                    db.Column('incident_id', db.Integer, db.ForeignKey('incident.id')),
                                    )

incidenttask_user_junction = db.Table('task_users',
                                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                      db.Column('id', db.Integer, db.ForeignKey('incident_task.id')),
                                      )

incidentlog_target_users_junction = db.Table('incidentlog_target_users_actions',
                                             db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                             db.Column('id', db.Integer, db.ForeignKey('incident_log.id')),
                                             )


def list_of_names(names):
    if not names:
        return None
    elif len(names) == 1:
        return str(names[0])
    return f'{", ".join([str(m) for m in names[:-1]])} and {str(names[-1])}'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    superuser = db.Column(db.Boolean(), default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group', backref='users')
    deployments = db.relationship('Deployment', secondary=deployment_user_junction)
    incidents = db.relationship('Incident', secondary=incident_user_junction)
    pinned = db.relationship('Incident', secondary=incident_pinned_junction)
    tasks = db.relationship('IncidentTask', secondary=incidenttask_user_junction)
    incident_log_target = db.relationship('IncidentLog', secondary=incidentlog_target_users_junction)
    audit_actions = db.relationship('AuditLog', backref='user', lazy=True)
    incident_comments = db.relationship('IncidentComment', backref='user')
    media_uploads = db.relationship('IncidentMedia', backref='uploaded_by')

    def set_password(self, password):
        self.password_hash = argon2.generate_password_hash(password)

    def check_password(self, password):
        return argon2.check_password_hash(self.password_hash, password)

    def create_avatar(self):
        if not path.exists(f'./app/static/img/avatars'):  ##TODO Move this to the start-up.
            makedirs(f'./app/static/img/avatars')
        avatar = pyavagen.Avatar(pyavagen.CHAR_AVATAR, size=128, font_size=65,
                                 string=f'{self.firstname} {self.surname}', color_list=avatar_colours)
        avatar.generate().save(f'./app/static/img/avatars/{self.id}_{self.firstname}_{self.surname}.png')

    def get_avatar(self, static=True):
        avatar_path = f'{"/static/" if static else ""}img/avatars/{self.id}_{self.firstname}_{self.surname}.png'
        if path.exists(f'./app{avatar_path}'):
            return avatar_path
        self.create_avatar()
        return avatar_path

    def get_deployments(self):
        deployments = []
        for x in Deployment.query.all():
            if self.has_deployment_access(x):
                deployments.append(x)
        return deployments

    def get_incidents(self, deployment, open_only=True, ignore_permissions=False):
        incidents = []
        if not isinstance(deployment, Deployment):
            deployment = Deployment.query.filter_by(id=deployment).first()
        if not deployment:
            return False
        if not self.has_deployment_access(deployment):
            return incidents
        if not ignore_permissions and self.has_permission('view_all_incidents'):
            return [m for m in deployment.incidents if m.open_status] if open_only else deployment.incidents
        for x in deployment.incidents:
            if (not open_only or (open_only and x.open_status)) and self in x.assigned_to:
                incidents.append(x)
        return incidents

    def has_permission(self, permission):
        if not self.group:
            return False
        return self.group.has_permission(permission)

    def has_deployment_access(self, deployment):
        if not isinstance(deployment, Deployment):
            deployment = Deployment.query.filter_by(id=deployment).first()
        if not deployment:
            return False
        if (not deployment.groups and not deployment.users) or self in deployment.users:
            return True
        for x in deployment.groups:
            if x.id == self.group_id:
                return True

    def has_incident_access(self, deployment_id, incident_id):
        incident = Incident.query.filter(Deployment.id == deployment_id, Incident.id == incident_id).first()
        if not self.has_deployment_access(incident.deployment):
            return False
        if self.has_permission('view_all_incidents') or self.id in incident.assigned_to:
            return True
        return False

    def __repr__(self):
        return f'{self.firstname} {self.surname}'


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Group(db.Model):
    permission_values = {'view_all_incidents': 0x1, 'change_status': 0x2, 'change_allocation': 0x4,
                         'mark_as_public': 0x8,
                         'new_reports': 0x16, 'create_deployment': 0x32, 'decision_making_log': 0x64,
                         'supervisor': 0x128, 'change_priority': 0x256}  ##TODO RE-DORDER ONCE DONE

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
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
    areas = db.Column(db.ARRAY(db.String(64)))
    open_status = db.Column(db.Boolean(), default=True)
    incidents = db.relationship('Incident', backref='deployment')
    groups = db.relationship('Group', secondary=deployment_group_junction)
    users = db.relationship('User', secondary=deployment_user_junction)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def name_check(self, deployment_name):
        return self.name.lower() == deployment_name.lower()

    def calculate_incidents_stat(self, user=None):
        if user:
            incidents = user.get_incidents(self)
        else:
            incidents = self.incidents
        two_hours = len([m for m in incidents if (datetime.utcnow() - timedelta(hours=2)) <= m.created_at < (
                datetime.utcnow() - timedelta(hours=1))])
        one_hour = len([m for m in incidents if m.created_at >= (datetime.utcnow() - timedelta(hours=1))])
        if two_hours == one_hour:
            return ["primary", None, 0]
        elif one_hour > two_hours:
            return ["danger", "plus", one_hour - two_hours]
        else:
            return ["success", "minus", two_hours - one_hour]

    def __repr__(self):
        return f'{self.name}'


class Incident(db.Model):
    priority_values = {'standard': 1, 'prompt': 2, 'immediate': 3}
    priorities = {1: 'standard', 2: 'prompt', 3: 'immediate'}
    priority_colours = {1: '#FFC312', 2: '#fa8231', 3: '#e74c3c'}
    incident_types = {}  ##TODO Get incident types.

    # TODO Add who has this pinned.
    id = db.Column(db.Integer, primary_key=True, index=True)
    deployment_id = db.Column(db.Integer, db.ForeignKey('deployment.id'))
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(256))
    reported_via = db.Column(db.String(256))
    reference = db.Column(db.String(128))  ##TODO MAYBE CHANGE TO INT
    incident_type = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by_user = db.relationship('User', backref='created_incidents')
    closed_at = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    public = db.Column(db.Boolean(), default=False)
    flagged = db.Column(db.Boolean(), default=False)
    open_status = db.Column(db.Boolean(), default=True)
    location = db.Column(db.String(128), index=True)
    priority = db.Column(db.Integer())
    longitude = db.Column(db.Float())
    latitude = db.Column(db.Float())
    assigned_to = db.relationship('User', secondary=incident_user_junction)
    users_pinned = db.relationship('User', secondary=incident_pinned_junction)
    tasks = db.relationship('IncidentTask', backref='incident')
    comments = db.relationship('IncidentComment', backref='incident')
    medias = db.relationship('IncidentMedia', backref='incident')
    actions = db.relationship('IncidentLog', backref='incident')

    def name_check(self, deployment_name, incident_name):
        return self.deployment.name.lower() == deployment_name.lower() and self.name.lower() == incident_name.lower()

    def get_priority(self):
        if not self.priority: return self.priorities[1].title()  ##TODO REMOVE
        return self.priorities[self.priority].title()

    def calculate_task_percentage(self):
        if not self.tasks:
            return
        return int((sum([1 for m in self.tasks if m.completed]) / len(self.tasks)) * 100)

    def task_string(self):
        if not self.tasks:
            return
        completed = [m for m in self.tasks if m.completed]
        return f'{len(completed)}/{len(self.tasks)}'

    def generate_geojson(self):
        if not self.longitude or not self.latitude:
            return
        return {
            'type': 'Feature',
            'properties': {
                'name': self.name,
                'description': self.description,
                'priority': self.get_priority(),
                'created_at': self.created_at.timestamp(),
                'location': self.location,
                'tasks': self.task_string(),
                'comments': len(self.comments),
                'colour': self.priority_colours[self.priority],
                'url': url_for('view_incident', deployment_name=self.deployment, deployment_id=self.deployment.id, incident_name=self.name, incident_id=self.id)
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [self.longitude, self.latitude]
            }
        }


class IncidentTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    name = db.Column(db.String(64))
    details = db.Column(db.String(1024))
    completed_details = db.Column(db.String(1024))
    completed = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    assigned_to = db.relationship('User', secondary=incidenttask_user_junction)

    def get_assigned(self):
        return list_of_names(self.assigned_to)

    def __repr__(self):
        return f'{self.name}'


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
                     'delete_comment': 6, 'incomplete_task': 7, 'assigned_user': 8, 'removed_user': 9,
                     'marked_complete': 10, 'marked_incomplete': 11, 'changed_priority': 12}  ##TODO RE-ORDER ONCE DONE
    action_strings = {1: 'created incident', 2: 'created task $task', 3: 'marked $task as complete',
                      4: 'deleted task $task',
                      5: 'added update', 6: 'deleted update', 7: 'marked $task as incomplete',
                      8: 'assigned $target_users to incident',
                      9: 'removed $target_users from incident', 10: 'marked incident as complete',
                      11: 'marked incident as incomplete', 12: 'changed priority to $extra'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='incident_actions')
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('incident_task.id'))
    task = db.relationship('IncidentTask', backref="logs", lazy=True)
    target_users = db.relationship('User', secondary=incidentlog_target_users_junction)
    action_type = db.Column(db.Integer())
    reason = db.Column(db.String(256))
    extra = db.Column(db.String(64))
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        target_users = None
        if self.target_users:
            if len(self.target_users) > 1:
                target_users = list_of_names(self.target_users)
            else:
                target_users = self.target_users[0]
        msg = Template(self.action_strings[self.action_type]).substitute(target_users=target_users, task=self.task,
                                                                         extra=self.extra)
        return f'{msg}.'


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


admin = Admin(app, name='DGVOST', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Group, db.session))
admin.add_view(ModelView(Deployment, db.session))
admin.add_view(ModelView(Incident, db.session))
admin.add_view(ModelView(IncidentTask, db.session))
admin.add_view(ModelView(IncidentComment, db.session))
admin.add_view(ModelView(IncidentMedia, db.session))
admin.add_view(ModelView(EmailLink, db.session))
admin.add_view(ModelView(AuditLog, db.session))
admin.add_view(ModelView(IncidentLog, db.session))
admin.add_view(ModelView(RevokedToken, db.session))
