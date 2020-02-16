import os
from dotenv import load_dotenv

class Config(object):
    def get_env_variable(name):
        try:
            return os.environ[name]
        except KeyError:
            raise Exception(f"Expected environment variable '{name}' not set.")

    def get_env_boolean(name, default):
        env = os.environ.get(name, default)
        if isinstance(env, str):
            if env.lower() == 'false':
                env = False
            elif env.lower() == 'true':
                env = True
            else:
                raise Exception(f"Expected environment variable '{name}' is not a boolean.")
        return env

    load_dotenv()

    POSTGRES_URL = get_env_variable('POSTGRES_URL')
    POSTGRES_USER = get_env_variable('POSTGRES_USER')
    POSTGRES_PASSWORD = get_env_variable('POSTGRES_PASSWORD')
    POSTGRES_DB = get_env_variable('POSTGRES_DB')

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{url}/{db}'.format(user=POSTGRES_USER,
                                                                                          password=POSTGRES_PASSWORD,
                                                                                          url=POSTGRES_URL,
                                                                                          db=POSTGRES_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = get_env_variable('FLASK_SECRET_KEY')

    JWT_SECRET_KEY = get_env_variable('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1800))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 172800))
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    MAPBOX_API_KEY = os.environ.get('MAPBOX_API_KEY')

    MAIL_SERVER = get_env_variable('MAIL_SERVER')
    MAIL_PORT = get_env_variable('MAIL_PORT')
    MAIL_USE_TLS = get_env_boolean('MAIL_USE_TLS', False)
    MAIL_USE_SSL = get_env_boolean('MAIL_USE_SSL', True)
    MAIL_USERNAME = get_env_variable('MAIL_USERNAME')
    MAIL_PASSWORD = get_env_variable('MAIL_PASSWORD')

    DOMAIN_NAME = get_env_variable('DOMAIN_NAME')
    ERROR_404_HELP = False