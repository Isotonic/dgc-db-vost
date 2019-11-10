from flask import Flask
from config import Config
from flask_moment import Moment
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

CSRFProtect(app)

from .api import api_blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')

from app import routes, models

login.login_view = 'login'

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedToken.is_jti_blacklisted(jti)
