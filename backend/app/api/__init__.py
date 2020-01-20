from app import jwt, db
from jwt import exceptions
from flask_restplus import Api
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
    return not user or user.password_last_updated.timestamp() > iat or RevokedToken.is_jti_blacklisted(jti)

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
                 description='An API allowing you to carry out actions on behalf of a user.',
                 authorizations=authorizations)

jwt._set_error_handler_callbacks(api)  # Fix for Flask-RestPlus error handler not working.

@api.errorhandler(exceptions.ExpiredSignatureError)
def handle_expired_token(error):
    return {'message': 'Token has expired'}, 401

from .authentication import ns_auth
from .user import ns_user
from .group import ns_group
from .deployment import ns_deployment
from .incident import ns_incident
from .task import ns_task
from .subtask import ns_subtask

api.add_namespace(ns_auth)
api.add_namespace(ns_user)
api.add_namespace(ns_group)
api.add_namespace(ns_deployment)
api.add_namespace(ns_incident)
api.add_namespace(ns_task)
api.add_namespace(ns_subtask)
