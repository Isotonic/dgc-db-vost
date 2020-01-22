# Credit to Vlad Frolov
# https://github.com/frol/flask-restplus-server-example/blob/master/flask_restplus_patched/namespace.py
from functools import wraps
from flask_restx import Namespace as OriginalNamespace

class Namespace(OriginalNamespace):

    def resolve_object(self, object_arg_name, resolver):
        """
        A helper decorator to resolve object instance from arguments (e.g. identity).
        Example:
        ...  @namespace.route('/<int:user_id>')
        ... class MyResource(Resource):
        ...    @namespace.resolve_object(
        ...        object_arg_name='user',
        ...        resolver=lambda kwargs: User.query.get_or_404(kwargs.pop('user_id'))
        ...    )
        ...    def get(self, user):
        ...        # user is a User instance here
        """
        def decorator(func_or_class):
            if isinstance(func_or_class, type):
                # Handle Resource classes decoration
                func_or_class._apply_decorator_to_methods(decorator)
                return func_or_class

            @wraps(func_or_class)
            def wrapper(*args, **kwargs):
                kwargs[object_arg_name] = resolver(kwargs)
                return func_or_class(*args, **kwargs)
            return wrapper
        return decorator

    def has_permission(self, user, permission):
        if not user.group.has_permission(permission):
            self.abort(403, f'Missing {permission.title()} permission')

    def has_deployment_access(self, user, deployment):
        if not user.has_deployment_access(deployment):
            self.abort(403, 'Missing access to this deployment')

    def has_incident_access(self, user, incident):
        if not user.has_incident_access(incident):
            self.abort(403, 'Missing access to this incident')
