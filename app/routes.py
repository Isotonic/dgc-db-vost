from app import app, db
from sqlalchemy import func
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from app.models import User, Group, Deployment, Incident, EmailLink, AuditLog
from app.utils.create import new_user, new_group, new_deployment, new_incident, new_task, new_comment
from app.forms import LoginForm, CreateUser, CreateGroup, SetPassword, CreateDeployment, CreateIncident, CreateTask, \
    AddComment


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html', title='Index')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/supervisor/create_user', methods=['GET', 'POST'])
def create_user():
    groups_list = [(i.id, i.name) for i in Group.query.all()]
    form = CreateUser()
    form.group.choices = groups_list
    if form.validate_on_submit():
        group = None
        if form.group.data:
            group = Group.query.get(form.group.data)
        user = new_user(form.username.data, form.email.data, group.id if group else None, current_user)
        flash('Congratulations, you created a user!')
        return user.email_link
    return render_template('new_user.html', title='Create New User', form=form)


@app.route('/verify/<link>', methods=['GET', 'POST'])
def verify_user(link):
    email = EmailLink.query.filter_by(link=link).first()
    if not email:
        return "Invalid Link"
    form = SetPassword()
    if form.validate_on_submit():
        email.user.set_password(form.password.data)
        action = AuditLog(user=email.user, action_type=AuditLog.action_values["verify_user"])
        db.session.add(action)
        db.session.delete(email)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('verify.html', title='Set Password', form=form, username=email.user.username)


@app.route('/supervisor/create_group', methods=['GET', 'POST'])
def create_group():
    form = CreateGroup()
    if form.validate_on_submit():
        permissions = {"view_all_incidents": form.view_all_incidents.data, "change_status": form.change_status.data,
                       "change_allocations": form.change_allocations.data, "mark_as_public": form.mark_as_public.data,
                       "new_reports": form.new_reports.data, "create_deployments": form.create_deployments.data,
                       "decision_making_log": form.decision_making_log.data, "supervisor": form.supervisor.data}
        chosen_permissions = [k for k, v in permissions.items() if v]
        group = new_group(form.name.data, chosen_permissions, current_user)
        return redirect(url_for('create_new_user'))
    return render_template('new_group.html', title='Create New Group', form=form)


@app.route('/create_deployment', methods=['GET', 'POST'])
def create_deployment():
    groups_list = [(i.id, i.name) for i in Group.query.all()]
    users_list = [(i.id, i.username) for i in User.query.all()]
    form = CreateDeployment()
    form.groups.choices = groups_list
    form.users.choices = users_list
    if form.validate_on_submit():
        deployment = new_deployment(form.name.data, form.description.data, form.groups.data, form.users.data,
                                    current_user)
        return deployment.name
    return render_template('new_user.html', title='Create New User', form=form)


@app.route('/deployment/<deployment_name>', methods=['GET'])
def deployment(deployment_name):
    deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(deployment_name)).first()
    if not deployment:
        return render_template('index.html', title='No deployment found')
    return render_template('base.html', title=f'{deployment.name}')


@app.route('/deployment/<deployment_name>/create_incident', methods=['GET', 'POST'])
def create_incident(deployment_name):
    deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(deployment_name)).first()
    if not deployment:
        return render_template('index.html', title='No deployment found')
    form = CreateIncident()
    if form.validate_on_submit():
        incident = new_incident(form.name.data, form.description.data, form.location.data, deployment, current_user)
        return incident.name
    return render_template('new_user.html', title=f'{deployment.name}', form=form)


@app.route('/deployment/<deployment_name>/<incident_name>-<int:incident_id>/create_task', methods=['GET', 'POST'])
def create_incident_task(deployment_name, incident_name, incident_id):
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name),
                                     Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return render_template('index.html', title='No deployment found')
    users_list = [(i.id, i.username) for i in User.query.all()]
    form = CreateTask()
    form.users.choices = users_list
    if form.validate_on_submit():
        task = new_task(form.name.data, form.details.data, form.users.data, incident, current_user)
        return task.name
    return render_template('new_user.html', title=f'{incident.name}', form=form)


@app.route('/deployment/<deployment_name>/<incident_name>-<int:incident_id>/add_comment', methods=['GET', 'POST'])
def add_incident_comment(deployment_name, incident_name, incident_id):
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name),
                                     Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return render_template('index.html', title='No deployment found')
    form = AddComment()
    if form.validate_on_submit():
        comment = new_comment(form.text.data, form.highlight.data, incident, current_user)
        return comment.text
    return render_template('new_user.html', title=f'{incident.name}', form=form)
