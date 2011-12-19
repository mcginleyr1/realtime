import os.path

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

DEFAULT_DSN = 'postgresql+psycopg2://user:password@host:port/dbname'

COLLECTOR_PORT = 8888
UI_PORT = 8889

PIXEL = open('../../images/pixel.gif')
