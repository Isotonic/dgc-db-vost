from app import jwt, db
from jwt import exceptions
from flask_restx import Api
from flask import Blueprint, url_for
from ..models import User, RevokedToken
from flask_jwt_extended import exceptions as extended_exceptions

@property
def specs_url(self):
    """
    The Swagger specifications absolute url (ie. `swagger.json`)

    :rtype: str
    """
    return url_for(self.endpoint('specs'), _external=False)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    iat = decrypted_token['iat']
    identity = int(decrypted_token['identity'])
    user = User.query.filter(User.id==identity, User.status>=1).first()
    return not user or (user.password_last_updated and user.password_last_updated.timestamp() > iat) or RevokedToken.is_jti_blacklisted(jti)

api_blueprint = Blueprint('api', __name__)

authorizations = {
    'access_token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }, 'refresh_token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

Api.specs_url = specs_url

api = Api(api_blueprint,
                 title='DGVOST API',
                 version='1.0',
                 description='An API allowing you to interact with the DGVOST backend.',
                 authorizations=authorizations)

jwt._set_error_handler_callbacks(api)  # Fix for Flask-RestPlus error handler not working.

import sys


def get_type_or_class_name(var) -> str:
    if type(var).__name__ == 'type':
        return var.__name__
    else:
        return type(var).__name__

@api.errorhandler(exceptions.ExpiredSignatureError)
def handle_expired_token(error):
    return {'message': 'Token has expired'}, 401

@api.errorhandler(extended_exceptions.RevokedTokenError)
def handle_expired_token(error):
    return {'message': 'Token has been revoked'}, 403

from .authentication import ns_auth
from .user import ns_user
from .group import ns_group
from .notification import ns_notification
from .deployment import ns_deployment
from .incident import ns_incident
from .comment import ns_comment
from .task import ns_task
from .task_comment import ns_task_comment
from .subtask import ns_subtask
from .actions_required import ns_actions_required
from .public import ns_public

api.add_namespace(ns_auth)
api.add_namespace(ns_user)
api.add_namespace(ns_group)
api.add_namespace(ns_notification)
api.add_namespace(ns_deployment)
api.add_namespace(ns_incident)
api.add_namespace(ns_comment)
api.add_namespace(ns_task)
api.add_namespace(ns_task_comment)
api.add_namespace(ns_subtask)
api.add_namespace(ns_actions_required)
api.add_namespace(ns_public)
