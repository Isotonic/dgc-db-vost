from flask import Flask
from config import Config
from flask_mail import Mail
from flask_cors import CORS
from os import path, makedirs
from flask_restx import abort
from flask_argon2 import Argon2
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy, BaseQuery

class CustomBaseQuery(BaseQuery):
    def get_or_error(self, ident):
        model_class_name = ''
        try:
            model_class_name = self._mapper_zero().class_.__name__
        except Exception as e:
            print(e)

        rv = self.get(ident)
        if not rv:
            abort(404, message=f'{model_class_name} {ident} doesn\'t exist')
        return rv

app = Flask(__name__)
app.config.from_object(Config)
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})
jwt = JWTManager(app)
db = SQLAlchemy(app, query_class=CustomBaseQuery)
migrate = Migrate(app, db)
login = LoginManager(app)
mail = Mail(app)
socketio = SocketIO(app, cors_allowed_origins='*')
argon2 = Argon2(app)

from .api import api_blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')

try:
    if not path.exists(f'./app/static'):
        makedirs(f'./app/static')
    if not path.exists(f'./app/static/img'):
        makedirs(f'./app/static/img')
    if not path.exists(f'./app/static/img/avatars'):
        makedirs(f'./app/static/img/avatars')
except:
    pass

from app import websockets, models
