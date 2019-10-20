from app.api import c5_api
from app.models import User, RevokedToken
from flask_restplus import Resource, Namespace
from app.api.utils.models import login_model, tokens_model
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt

ns_auth = Namespace('Authentication', description='Used to authenticate the user.', path='/auth')


@ns_auth.route('/login')
class Login(Resource):
    @ns_auth.expect(login_model, validate=True)
    @ns_auth.response(200, 'Success', tokens_model)
    @ns_auth.response(401, 'Incorrect credentials')
    def post(self):
        """
                Returns an access and refresh token, as well as their expiry dates, the tokens are JWT so can be decoded for more info
                'access_token' is needed for all other endpoints and has a lifetime of 15 mins.
                'refresh_token' is needed to refresh your access token once it has expired, it has a lifetime of 30 days.
        """
        user = User.query.filter_by(username=c5_api.payload['username']).first()
        if not user:
            ns_auth.abort(401, 'Incorrect credentials')

        if user.check_password(c5_api.payload['password']):
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)

            return {'access_token': access_token, 'refresh_token': refresh_token}, 200

        ns_auth.abort(401, 'Incorrect credentials')

@ns_auth.route('/refresh_access')
class RefreshToken(Resource):
    @jwt_refresh_token_required
    @ns_auth.doc(security='access_token')
    @ns_auth.response(200, 'Success')
    @ns_auth.response(401, 'Incorrect credentials')
    @ns_auth.param(name='Authorization', description='Requires your refresh_token.', _in="header")
    def post(self):
        """
                Returns a new access_token.
        """
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}

@ns_auth.route('/revoke_access')
class UserLogoutAccess(Resource):
    @jwt_required
    @ns_auth.doc(security='access_token')
    @ns_auth.response(200, 'Success')
    @ns_auth.response(401, 'Incorrect credentials')
    @ns_auth.param(name='Authorization', description='Requires your access_token.', _in="header")
    def post(self):
        """
                Revokes access to an access_token
        """
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500

@ns_auth.route('/revoke_refresh')
class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    @ns_auth.doc(security='refresh_token')
    @ns_auth.response(200, 'Success')
    @ns_auth.response(401, 'Incorrect credentials')
    @ns_auth.param(name='Authorization', description='Requires your refresh_token.', _in="header")
    def post(self):
        """
                Revokes access to a refresh_token
        """
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500