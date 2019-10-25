from sqlalchemy import func
from flask_wtf import FlaskForm
from app.models import User, Group, Deployment
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class CreateUser(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    group = SelectField('Group', coerce=int)
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class CreateGroup(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    view_all_incidents = BooleanField("View All Incidents", default=False)
    change_status = BooleanField("Change Status", default=False)
    change_allocations = BooleanField("Change Allocations", default=False)
    mark_as_public = BooleanField("Mark As Public", default=False)
    create_deployments = BooleanField("Create Deployments", default=False)
    decision_making_log = BooleanField("Decision-Making Log", default=False)
    new_reports = BooleanField("Handle New Reports", default=False)
    supervisor = BooleanField("Supervisor", default=False)
    submit = SubmitField('Create Group')

    def validate_name(self, name):
        group = Group.query.filter(func.lower(Group.name) == func.lower(name)).first()
        if group is not None:
            raise ValidationError('Please choose a different group name.')


class SetPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')


class CreateDeployment(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    groups = SelectMultipleField('Groups', coerce=int)
    users = SelectMultipleField('Users', coerce=int)
    submit = SubmitField('Submit')

    def validate_name(self, name):
        deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(name)).first()
        if deployment is not None:
            raise ValidationError('Please choose a different deployment name.')


class CreateIncident(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CreateTask(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    details = StringField('Details')
    users = SelectMultipleField('Users', coerce=int)
    submit = SubmitField('Submit')


class AddComment(FlaskForm):
    text = StringField('Comment', validators=[DataRequired()])
    highlight = BooleanField("Highlight", default=False)
    submit = SubmitField('Submit')