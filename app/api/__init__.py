from flask import Blueprint
from flask_restplus import Api

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

c5_api = Api(api_blueprint,
             title='C5 API',
             version='1.0',
             description='Complete actions via the API on behalf of a user.',
             authorizations=authorizations)

from .authentication import ns_auth
from .user import ns_user
from .group import ns_group

c5_api.add_namespace(ns_auth)
c5_api.add_namespace(ns_user)
c5_api.add_namespace(ns_group)