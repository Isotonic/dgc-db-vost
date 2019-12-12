import functools
from sqlalchemy import func
from itertools import groupby
from app import app, db, socketio
from flask_socketio import emit, join_room, disconnect
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, CreateUser, CreateGroup, SetPassword, CreateDeployment
from app.utils.change import incident_status, allocation, incident_priority, task_status
from app.models import User, Group, Deployment, Incident, IncidentTask, EmailLink, AuditLog
from app.utils.create import new_user, new_group, new_deployment, new_incident, new_task, new_comment


def login_required_sockets(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

def has_permission_sockets(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.has_permission(None):
            return emit('change_status', {'message': 'You don\'t have permission to change an incident\'s status.', 'code': 403})
        else:
            return f(*args, **kwargs)
    return wrapped

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
    groups = []
    for k, g in groupby(User.query.all(), key=lambda item: item.group):
        groups.append([[k.id, k.name], list(g)])
    return render_template('deployments.html', title='Deployments', nosidebar=True, groups=groups, back_url=url_for('view_deployments'), deployments=current_user.get_deployments())


@app.route('/deployments/<deployment_name>/incidents/', methods=['GET'])
@login_required
def view_incidents(deployment_name):
    deployment_name = deployment_name.replace("-", " ")
    deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(deployment_name)).first()
    if not deployment:
        return render_template('404.html', nosidebar=True), 404
    incidents_stat = deployment.calculate_incidents_stat()
    return render_template('incidents.html', title=f'{deployment.name}', deployment=deployment,
                           incidents_active=True, incidents_stat=incidents_stat, incidents=current_user.get_incidents(deployment.id), back_url=url_for('view_deployments'))

@app.route('/deployments/<deployment_name>/assigned_incidents/', methods=['GET'])
@login_required
def view_assigned_incidents(deployment_name):
    deployment_name = deployment_name.replace("-", " ")
    deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(deployment_name)).first()
    if not deployment:
        return render_template('404.html', nosidebar=True), 404
    incidents_stat = deployment.calculate_incidents_stat(current_user)
    return render_template('incidents.html', title=f'{deployment.name}', deployment=deployment,
                           assigned_incidents_active=True, incidents_stat=incidents_stat, incidents=current_user.get_incidents(deployment.id, ignore_permissions=True), back_url=url_for('view_deployments'))


@app.route('/deployments/<deployment_name>/incidents/<incident_name>-<int:incident_id>', methods=['GET', 'POST'])
@login_required
def view_incident(deployment_name, incident_name, incident_id):
    deployment_name = deployment_name.replace("-", " ")
    incident = Incident.query.filter(func.lower(Incident.name) == func.lower(incident_name),
                                     Incident.id == incident_id).first()
    if not incident or incident.deployment.name.lower() != deployment_name.lower():
        return render_template('404.html', nosidebar=True), 404
    groups = []
    for k, g in groupby(User.query.all(), key=lambda item: item.group):
        groups.append([k.name, list(g)])
    return render_template('incident.html', incident=incident, deployment=incident.deployment, groups=groups, back_url=url_for('view_incidents', deployment_name=deployment_name), title=f'{deployment_name} - Incident {incident_id}')


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

@socketio.on('join')
@login_required_sockets
def on_join(data):
    if data['type'] == 0:
        join_room('deployments')
        print('Joined Private Room: deployments')
    if data['type'] == 1:
        if current_user.has_deployment_access(data['deployment_id']):
            if current_user.has_permission('view_all_incidents'):
                join_room(f'{data["deployment_id"]}-all')
                print(f'Joined Global Room: {data["deployment_id"]}-all')
            else:
                join_room(f'{data["deployment_id"]}-private')
                print(f'Joined Private Room: {data["deployment_id"]}-private')
        else:
            disconnect()
            print(f'Kicked from Room: {data["deployment_id"]}')
    elif data['type'] == 2:
        if current_user.has_incident_access(data['deployment_id'], data['incident_id']):
            join_room(f'{data["deployment_id"]}-{data["incident_id"]}')
            print(f'Joined Room: {data["deployment_id"]}-{data["incident_id"]}')
        else:
            disconnect()
            print(f'Kicked from Room: {data["deployment_id"]}-{data["incident_id"]}')


@socketio.on('create_deployment')
@login_required_sockets
#@has_permission_sockets
def create_incident(data):
    print(data)
    try:
        name = data['name']
        description = data['description']
        groups = data['groups']
        users = data['users']
    except:
        return emit('create_incident', {'message': 'Incorrect data supplied.', 'code': 403})
    new_deployment(name, description, groups, users, current_user)


@socketio.on('create_incident')
@login_required_sockets
#@has_permission_sockets
def create_incident(data):
    print(data)
    try:
        name = data['name']
        description = data['description']
        location = data['location']
        reported_via = data['reported_via']
        reference = data['reference']
    except:
        return emit('create_incident', {'message': 'Incorrect data supplied.', 'code': 403})
    deployment = Deployment.query.filter_by(id=data['deployment_id']).first()
    if not deployment:
        return emit('create_incident', {'message': 'Unable to find the deployment.', 'code': 404})
    new_incident(name, description, location, reported_via, reference, deployment, current_user)


@socketio.on('change_incident_status')
@login_required_sockets
#@has_permission_sockets
def change_incident_status(data):
    print(data)
    try:
        status = data["status"]
    except:
        return emit('change_incident_status', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id==data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('change_incident_status', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    if incident_status(current_user, incident, status) is False:
        return emit('change_incident_status', {'message': 'Incident already has this status.', 'code': 400})


@socketio.on('change_incident_allocation')
@login_required_sockets
#@has_permission_sockets
def change_incident_allocation(data):
    #if not current_user.has_permission('change_allocation'):
    #    return jsonify(data='You don\'t have permission to change an incident\'s allocation.'), 403
    print(data)
    incident = Incident.query.filter(Deployment.id==data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('change_incident_allocation', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    users = [n for n in [User.query.filter_by(id=int(m)).first() for m in data['users'] if m] if n and n.has_deployment_access(incident.deployment)]
    if allocation(current_user, incident, users) is False:
        return emit('change_incident_allocation', {'message': 'Didn\'t change assigned users.', 'code': 400})


@socketio.on('change_incident_priority')
@login_required_sockets
#@has_permission_sockets
def change_incident_priority(data):
    print(data)
    #if not current_user.has_permission('change_priority'):
    #    return jsonify(data='You don\'t have permission to change an incident\'s priority.'), 403
    try: ##TODO Add in function to get data
        priority = Incident.priority_values[data['priority'].lower()]
    except:
        return emit('change_incident_priority', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id == data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('change_incident_priority', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    if incident_priority(current_user, incident, priority) is False:
        return emit('change_incident_priority', {'message': 'Incident already has this priority.', 'code': 400})

@socketio.on('create_incident_task')
@login_required_sockets
#@has_permission_sockets
def create_incident_task(data):
    print(data)
    try: ##TODO Add in incident id and deployment id in here too
        name = data['name']
        users = [User.query.filter_by(id=int(m)).first() for m in data['users'] if m]
    except:
        return emit('create_incident_task', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id == data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('create_incident_task', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    users = [m for m in users if m and m in incident.assigned_to]
    new_task(name, users, incident, current_user)


@socketio.on('change_task_status')
@login_required_sockets
#@has_permission_sockets
def change_task_status(data):
    task_id = data['task_id']
    completed = data['completed']
       # return emit('change_task_status', {'message': 'Incorrect data supplied.', 'code': 403})
    task = IncidentTask.query.filter_by(incident_id=data['incident_id'], id=task_id).first()
    if not task or task.incident.deployment_id != data['deployment_id']:
        return emit('change_task_status', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    if task_status(current_user, task, completed) is False:
        return emit('change_task_status', {'message': 'Task already has this status.', 'code': 400})


@socketio.on('create_incident_comment')
@login_required_sockets
#@has_permission_sockets
def create_incident_comment(data):
    try:
        text = data['text']
    except:
        return emit('create_incident_comment', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id == data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('create_incident_comment', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    new_comment(text, False, incident, current_user)
