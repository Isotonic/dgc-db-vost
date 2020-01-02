from flask import Flask
from config import Config
from flask_cors import CORS
from flask_moment import Moment
from flask_argon2 import Argon2
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
cors = CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
moment = Moment(app)
csrf = CSRFProtect(app)
socketio = SocketIO(app)
argon2 = Argon2(app)
bootstrap = Bootstrap(app)

from .api import api_blueprint
app.register_blueprint(api_blueprint)
csrf.exempt(api_blueprint)

from app import routes, models
login.login_view = 'login'

db.create_all()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedToken.is_jti_blacklisted(jti)

