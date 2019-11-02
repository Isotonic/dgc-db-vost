from app import app, db
from sqlalchemy import func
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Group, Deployment, Incident, EmailLink, AuditLog
from app.utils.create import new_user, new_group, new_deployment, new_incident, new_task, new_comment
from app.forms import LoginForm, CreateUser, CreateGroup, SetPassword, CreateDeployment, CreateIncident, CreateTask, \
    AddComment


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('view_deployments'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.username) == func.lower(form.username.data)).first()
        if user is None or not user.check_password(form.password.data):
            return render_template('login.html', title='Sign In', form=form, invalid=True)
        login_user(user, remember=form.remember_me.data)
        next = request.args.get('next')
        print(next)
        if next:
            return redirect(next)
        return redirect(url_for('view_deployments'))
    return render_template('login.html', title='Sign In', form=form, invalid=False)


@app.route('/supervisor/create_user/', methods=['GET', 'POST'])
@login_required
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


@app.route('/verify/<link>/', methods=['GET', 'POST'])
@login_required
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


@app.route('/supervisor/create_group/', methods=['GET', 'POST'])
@login_required
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


@app.route('/')
@app.route('/deployments/', methods=['GET'])
@login_required
def view_deployments():
    return render_template('deployments.html', title='Deployments', deployments=current_user.get_deployments())


@app.route('/create_deployment/', methods=['GET', 'POST'])
@login_required
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


@app.route('/deployments/<deployment_name>/incidents/', methods=['POST', 'GET']) ##TODO Use AJAX
@login_required
def view_incidents(deployment_name):
    deployment_name = deployment_name.replace("-", " ")
    deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(deployment_name)).first()
    if not deployment:
        return render_template('index.html', title='No deployment found')
    form = CreateIncident()
    if form.validate_on_submit():
        new_incident(form.name.data, form.description.data, form.location.data, deployment, current_user)
        return redirect(url_for("view_incidents", deployment_name=deployment_name))
    return render_template('incidents.html', title=f'{deployment.name}', deployment_name=deployment.name,
                           incidents=current_user.get_incidents(deployment.id), form=form)


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>', methods=['GET', 'POST'])
@login_required
def view_incident(deployment_name, incident_name, incident_id):
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name),
                                     Incident.id == incident_id).first()
    print(1)
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return render_template('incidents.html', title='No deployment found')
    return render_template('incidents.html', title=f'{incident.name}')

@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>/create_task/', methods=['GET', 'POST'])
@login_required
def create_incident_task(deployment_name, incident_name, incident_id):
    deployment_name = deployment_name.replace("-", " ")
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


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>/add_comment/', methods=['GET', 'POST'])
@login_required
def add_incident_comment(deployment_name, incident_name, incident_id):
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name),
                                     Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return render_template('index.html', title='No deployment found')
    form = AddComment()
    if form.validate_on_submit():
        comment = new_comment(form.text.data, form.highlight.data, incident, current_user)
        return comment.text
    return render_template('new_user.html', title=f'{incident.name}', form=form)


@app.route('/notification/', methods=['GET'])
@login_required
def view_notifications():
    pass


@app.route('/map/', methods=['GET'])
@login_required
def view_map():
    pass


@app.route('/live-feed/', methods=['GET'])
@login_required
def view_live_feed():
    pass


@app.route('/decision-making-log/', methods=['GET'])
@login_required
def view_decision_making_log():
    pass
