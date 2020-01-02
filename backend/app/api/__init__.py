from app import jwt
from flask_restplus import Api
from flask import Blueprint, url_for

@property
def specs_url(self):
    """
    The Swagger specifications absolute url (ie. `swagger.json`)

    :rtype: str
    """
    return url_for(self.endpoint('specs'), _external=False)

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

dgvost_api = Api(api_blueprint,
                 title='DGVOST API',
                 version='1.0',
                 description='An API allowing you to carry out actions on behalf of a user.',
                 authorizations=authorizations)

jwt._set_error_handler_callbacks(dgvost_api)  # Fix for Flask-RestPlus error handler not working.

from .authentication import ns_auth
from .user import ns_user
from .group import ns_group
from .deployment import ns_deployment
from .incident import ns_incident

dgvost_api.add_namespace(ns_auth)
dgvost_api.add_namespace(ns_user)
dgvost_api.add_namespace(ns_group)
dgvost_api.add_namespace(ns_deployment)
dgvost_api.add_namespace(ns_incident)
