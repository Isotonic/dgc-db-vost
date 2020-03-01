from ..api import api
from sqlalchemy import func
from ..models import User, RevokedToken
from flask_restx import Resource, Namespace
from .utils.models import login_model, tokens_model
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt

ns_auth = Namespace('Authentication', description='Used to authenticate the user.', path='/auth')


@ns_auth.route('/login')
class LoginEndpoint(Resource):
    @ns_auth.expect(login_model, validate=True)
    @ns_auth.response(200, 'Success', tokens_model)
    @ns_auth.response(401, 'Incorrect credentials')
    def post(self):
        """
                Returns an access and refresh token, as well as their expiry dates, the tokens are JWT so can be decoded for more info
                'access_token' is needed for all other endpoints and has a lifetime of 20 mins.
                'refresh_token' is needed to refresh your access token once it has expired, it has a lifetime of 2 days.
        """
        user = User.query.filter(func.lower(User.email) == func.lower(api.payload['email'])).first()
        if not user or user.status < 1:
            ns_auth.abort(401, 'Incorrect credentials')

        if user.check_password(api.payload['password']):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return {'access_token': access_token, 'refresh_token': refresh_token}, 200

        ns_auth.abort(401, 'Incorrect credentials')


@ns_auth.route('/refresh-access')
class RefreshTokenEndpoint(Resource):
    @jwt_refresh_token_required
    @ns_auth.doc(security='access_token')
    @ns_auth.response(200, 'Success')
    @ns_auth.response(401, 'Incorrect credentials')
    @ns_auth.param(name='Authorization', description='Requires your refresh_token.', _in='header')
    def get(self):
        """
                Returns a new access token.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        access_token = create_access_token(identity=current_user.id)
        refresh_token = create_refresh_token(identity=current_user.id)
        jti = get_raw_jwt()['jti']
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add()
        return {'access_token': access_token, 'refresh_token': refresh_token}


@ns_auth.route('/revoke-access')
class RevokeAccessEndpoint(Resource):
    @jwt_required
    @ns_auth.doc(security='access_token')
    @ns_auth.response(200, 'Success')
    @ns_auth.response(401, 'Incorrect credentials')
    @ns_auth.param(name='Authorization', description='Requires your access_token.', _in='header')
    def delete(self):
        """
                Revokes access to an access token.
        """
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


@ns_auth.route('/revoke-refresh')
class RevokeRefreshEndpoint(Resource):
    @jwt_refresh_token_required
    @ns_auth.doc(security='refresh_token')
    @ns_auth.response(200, 'Success')
    @ns_auth.response(401, 'Incorrect credentials')
    @ns_auth.param(name='Authorization', description='Requires your refresh_token.', _in="header")
    def delete(self):
        """
                Revokes access to a refresh token.
        """
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
