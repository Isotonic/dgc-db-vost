import os


class Config(object):
    def get_env_variable(name):
        try:
            return os.environ[name]
        except KeyError:
            message = "Expected environment variable '{}' not set.".format(name)
            raise Exception(message)

    # Setup Postgres details.
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
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    MAPBOX_API_KEY = os.environ.get('MAPBOX_API_KEY')
    ERROR_404_HELP = False