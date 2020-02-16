from app import jwt, db
from jwt import exceptions
from flask_restx import Api
from flask import Blueprint, url_for
from ..models import User, RevokedToken

@property
def specs_url(self):
    """
    The Swagger specifications absolute url (ie. `swagger.json`)

    :rtype: str
    """
    return url_for(self.endpoint('specs'), _external=False)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token): ##TODO Check if it returns false when the password updated is greater than iat
    jti = decrypted_token['jti']
    iat = decrypted_token['iat']
    identity = int(decrypted_token['identity'])
    user = User.query.filter_by(id=identity).first()
    return not user or user.status != 1 or user.password_last_updated.timestamp() + 15 < iat or RevokedToken.is_jti_blacklisted(jti)

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

@api.errorhandler(Exception)
def generic_exception_handler(e: Exception):
    exc_type, exc_value, exc_traceback = sys.exc_info()

    if exc_traceback:
        traceback_details = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': get_type_or_class_name(exc_type),
            'message': str(exc_value),
        }
        return {'message': traceback_details['message']}, 500
    else:
        return {'message': 'Internal Server Error'}, 500

@api.errorhandler(exceptions.ExpiredSignatureError)
def handle_expired_token(error):
    return {'message': 'Token has expired'}, 401

from .authentication import ns_auth
from .user import ns_user
from .group import ns_group
from .deployment import ns_deployment
from .incident import ns_incident
from .comment import ns_comment
from .task import ns_task
from .subtask import ns_subtask
from .public import ns_public

api.add_namespace(ns_auth)
api.add_namespace(ns_user)
api.add_namespace(ns_group)
api.add_namespace(ns_deployment)
api.add_namespace(ns_incident)
api.add_namespace(ns_comment)
api.add_namespace(ns_task)
api.add_namespace(ns_subtask)
api.add_namespace(ns_public)
