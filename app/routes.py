from sqlalchemy import func
from flask_socketio import emit
from datetime import datetime, timedelta
from app import app, db, moment, socketio
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app.utils.change import incident_status, allocation, incident_priority, task_status
from app.models import User, Group, Deployment, Incident, IncidentTask, EmailLink, AuditLog
from app.utils.create import new_user, new_group, new_deployment, new_incident, new_task, new_comment
from app.forms import LoginForm, CreateUser, CreateGroup, SetPassword, CreateDeployment, CreateIncident, ChangeAllocation, AddTask, AddComment


def calculate_incidents_stat(incidents):
    two_hours = len([m for m in incidents if (datetime.utcnow() - timedelta(hours=2)) <= m.created_at < (datetime.utcnow() - timedelta(hours=1))])
    one_hour = len([m for m in incidents if m.created_at >= (datetime.utcnow() - timedelta(hours=1))])
    if two_hours == one_hour:
        return ["primary", None, 0]
    elif one_hour > two_hours:
        return ["danger", "plus", one_hour-two_hours]
    else:
        return ["success", "minus", two_hours-one_hour]

@app.errorhandler(404)
@login_required
def page_not_found(e):
    if current_user.is_authenticated:
        return render_template('404.html', nosidebar=True), 404
    return redirect(url_for('login'))


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
        user = User.query.filter(func.lower(User.email) == func.lower(form.email.data)).first()
        if user is None or not user.check_password(form.password.data):
            return render_template('login.html', title='Sign In', form=form, invalid=True)
        login_user(user, remember=form.remember_me.data)
        next = request.args.get('next')
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
        user = new_user(form.firstname.data, form.surname.data, form.email.data, group.id if group else None, current_user)
        flash('Congratulations, you created a user!')
        return user.email_link
    return render_template('base.html', title='Create New User', form=form)


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
    return render_template('base.html', title='Set Password', form=form, username=email.user.username)


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
    return render_template('base.html', title='Create New Group', form=form)


@app.route('/')
@app.route('/deployments/', methods=['GET'])
@login_required
def view_deployments():
    return render_template('deployments.html', title='Deployments', nosidebar=True, back_url=url_for('view_deployments'), deployments=current_user.get_deployments())


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
    return render_template('base.html', title='Create New User', form=form)


@app.route('/deployments/<deployment_name>/incidents/', methods=['GET'])
@login_required
def view_incidents(deployment_name):
    deployment_name = deployment_name.replace("-", " ")
    deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(deployment_name)).first()
    if not deployment:
        return render_template('404.html', nosidebar=True), 404
    incidents_stat = calculate_incidents_stat(deployment.incidents)
    return render_template('incidents.html', title=f'{deployment.name}', deployment=deployment, deployment_name=deployment.name,
                           incidents_active=True, incidents_stat=incidents_stat, incidents=current_user.get_incidents(deployment.id), back_url=url_for('view_deployments'))


@app.route('/deployments/<deployment_name>/add_incident/', methods=['POST'])
@login_required
def add_incident(deployment_name):
    deployment_name = deployment_name.replace("-", " ")
    deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(deployment_name)).first()
    if not deployment:
        return jsonify(data='Unable to find deployment.'), 404
    form = CreateIncident()
    if form.validate_on_submit():
        incident = new_incident(form.name.data, form.description.data, form.location.data, deployment, current_user)
        return jsonify(data={'url': url_for("view_incident", deployment_name=deployment.name, incident_name=incident.name, incident_id=incident.id)}), 200
    return jsonify(data=form.errors), 400


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>', methods=['GET', 'POST'])
@login_required
def view_incident(deployment_name, incident_name, incident_id):
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name),
                                     Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return render_template('404.html', nosidebar=True), 404
    from itertools import groupby
    groups = []
    for k, g in groupby(User.query.all(), key=lambda item: item.group):
        groups.append([k.name, list(g)])
    return render_template('incident.html', incident=incident, deployment_name=incident.deployment.name, groups=groups, back_url=url_for('view_incidents', deployment_name=deployment_name), title=f'{deployment_name} - Incident {incident_id}')


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>/change_incident_status/', methods=['POST'])
@login_required
def change_incident_status(deployment_name, incident_name, incident_id):
    if not current_user.has_permission('change_status'):
        return jsonify(data="You don't have permission to change an incident's status."), 403
    try:
        status = bool(int(request.form['status']))
    except:
        return jsonify(data='Incorrect data supplied.'), 404
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name), Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return jsonify(data='Unable to find the deployment or incident.'), 404
    if incident_status(current_user, incident, status) is False:
        return jsonify(data="Incident already has this status."), 400
    return jsonify(status=status), 200


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>/change_allocation/', methods=['POST'])
@login_required
def change_allocation(deployment_name, incident_name, incident_id):
    if not current_user.has_permission('change_allocation'):
        return jsonify(data="You don't have permission to change an incident's allocation."), 403
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name), Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return jsonify(data='Unable to find the deployment or incident.'), 404
    users_list = [(i.id, str(i)) for i in User.query.all()]
    form = ChangeAllocation()
    form.users.choices = users_list
    if form.validate_on_submit():
        if allocation(current_user, incident, form.users.data) is False:
            return jsonify(data="Didn't change assigned users."), 400
        return jsonify(html=[render_template('assigned_to.html', user=m) for m in incident.assigned_to]), 200
    return jsonify(data=form.errors), 400


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>/change_incident_priority/', methods=['POST'])
@login_required
def change_incident_priority(deployment_name, incident_name, incident_id):
    if not current_user.has_permission('change_priority'):
        return jsonify(data="You don't have permission to change an incident's priority."), 403
    try:
        priority = Incident.priority_values[request.form['priority'].lower()]
    except:
        return jsonify(data='Incorrect data supplied.'), 404
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name), Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return jsonify(data='Unable to find the deployment or incident.'), 404
    if incident_priority(current_user, incident, priority) is False:
        return jsonify(data="Incident already has this priority."), 400
    return jsonify(priority=Incident.priorities[incident.priority].title()), 200


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>/add_task/', methods=['POST'])
@login_required
def add_task(deployment_name, incident_name, incident_id):
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name), Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return jsonify(data='Unable to find the deployment or incident.'), 404
    users_list = [(i.id, str(i)) for i in User.query.all()]
    form = AddTask()
    form.users.choices = users_list
    if form.validate_on_submit():
        task = new_task(form.name.data, form.users.data, incident, current_user)
        return jsonify(html=render_template('task.html', task=task)), 200
    return jsonify(data=form.errors)


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>/change_task_status/', methods=['POST'])
@login_required
def change_task_status(deployment_name, incident_name, incident_id):
    try:
        task_id = request.form['id']
        completed = bool(int(request.form['completed']))
    except:
        return jsonify(data='Incorrect data supplied.'), 404
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name), Incident.id == incident_id).first()
    task = IncidentTask.query.filter_by(incident_id=incident.id, id=task_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower() or not task:
        return jsonify(data='Unable to find the deployment or incident.'), 404
    if task.assigned_to and current_user not in task.assigned_to:
        return jsonify(data='You are not assigned to this task.'), 403
    if task_status(current_user, task, completed) is False:
        return jsonify(data="Task already has this status."), 400
    if task.completed:
        return jsonify(timestamp=moment.create(task.completed_at).fromNow(refresh=True))
    else:
        return jsonify(timestamp=moment.create(task.created_at).fromNow(refresh=True))


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>/add_comment/', methods=['GET', 'POST'])
@login_required
def add_incident_comment(deployment_name, incident_name, incident_id):
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name),
                                     Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return render_template('404.html', nosidebar=True), 404
    form = AddComment()
    if form.validate_on_submit():
        comment = new_comment(form.text.data, form.highlight.data, incident, current_user)
        return comment.text
    return render_template('base.html', title=f'{incident.name}', form=form)


@app.route('/notifications/', methods=['GET'])
@login_required
def view_notifications():
    pass


@app.route('/<deployment_name>/map/', methods=['GET'])
@login_required
def view_map(deployment_name):
    pass


@app.route('/<deployment_name>/live-feed/', methods=['GET'])
@login_required
def view_live_feed(deployment_name):
    pass


@app.route('/<deployment_name>/decision-making-log/', methods=['GET'])
@login_required
def view_decision_making_log(deployment_name):
    pass

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message["data"])